import html
import json
import uuid
import sys

import os

import datetime
from flask import Flask, request, redirect, render_template, send_file, session, send_from_directory
from werkzeug.exceptions import abort
import facebook

from accounts.users import UserJobs
from communities import merge_similar
from tables import create_file_and_upload_to_s3, ans_from_s3_ans_bucket, delete_job, create_staging_file_and_upload_to_s3
from excel_converter import make_workbook
from accounts import db, users
import random
from collections import defaultdict
from flask_sslify import SSLify

app = Flask(__name__, static_url_path='/static')

if 'DYNO' in os.environ: # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app)

app.secret_key = os.environ['FLASK_SECRET']
fb_app_id = os.environ['FB_APP_ID']
fb_app_secret = os.environ['FB_APP_SECRET']

ALLOWED_EXTENSIONS = set(['csv', 'xlsx'])

app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 megabyte



@app.route('/')
def hello_world():

    return render_template('index.html', result = {'deleted_msg' : request.args.get('message')}, fb_app_id=fb_app_id)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/submissions_for_user', methods=['GET'])
def get_submissions():
    access_token = request.args.get('access_token')
    user_id = verify_facebook_access_token_and_get_user_id(access_token)
    jobs = users.jobs_of_user(user_id)
    return render_template('binder.html', jobs = jobs)


@app.route('/review', methods=['POST'])
def review():
    """
    Endpoint to review the guest list, and to assign weights.
    Should also allow user to confirm if the number of distinct guests for each name
    """
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    try:
        table_size = int(request.form['size'])
    except Exception as e:
        table_size = 10

    if file.filename == '':
        return redirect(request.url)

    if not file or not allowed_file(file.filename):
        return redirect(request.url)

    job_id, community, persons, clique_names = create_staging_file_and_upload_to_s3(table_size, file)

    facebook_access_token = request.form['facebook_access_token']
    return render_template('review.html', job_id=job_id,
                           clique_names=[clique_name
                                         for clique_name in clique_names],
                           facebook_access_token=facebook_access_token)


@app.route('/solve', methods=['POST'])
def solve():

    job_id = request.form['job_id']

    if job_id == '':
        return redirect('/')

    num_cliques = request.form['num_cliques']
    clique_weights = {}
    for i in range(1, int(num_cliques) + 1):
        name = request.form[str(i) + '_clique_name']
        weight = request.form[str(i) + '_weight']
        clique_weights[name] = weight

    create_file_and_upload_to_s3(job_id, clique_weights)

    user_facebook_access_token = request.form['facebook_access_token']

    if user_facebook_access_token is not None and len(user_facebook_access_token) > 0:
        user_id = verify_facebook_access_token_and_get_user_id()
        db.db_session.add(UserJobs(id=user_id, job_id=job_id))
        db.db_session.commit()

    page_html = """
    <!doctype html>
    <html>
    <head>
        <title>Seating Chart Plan - Token and Further Instructions</title>
        <link rel="stylesheet"
    href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
    <link rel="shortcut icon" href="static/favicon.ico">
    </head>
    <body>
        <article>
        <p>
        Your token is <strong>{}</strong>. If you were not logged-in to Facebook when submitting the guest list, please copy and paste it somewhere for retrieving the seating chart in future.
        </p>
        <p>
        We will need some time to process your guest list and plan the sitting arrangement for your seating chart.
        </p>
        <p>
        Visit <a href="retrieve?job_id={}&from_submit_page=true">this page</a> after ~{}
        hours to collect our proposed seating plan to your event.
        </p>
        </article>
        <a href="/">Back to Home</a>
    </body>
    """
    return app.response_class(
        response=page_html.format(job_id, job_id, '5'),
        status=200,
        mimetype='text/html'
    )


@app.route('/retrieve', methods=['GET'])
def retrieve():
    job_id = request.args.get('job_id').strip()
    tables, persons, coarse_to_original, new_community, clique_names = ans_from_s3_ans_bucket(job_id)
    if tables is None:
        from_submit_page = request.args.get('from_submit_page')
        return app.response_class(
            response="""
            <!doctype html>
            <html>
            <head>
                <title>Seating Chart Plan - Not Ready Yet</title>
                <link rel="stylesheet"
            href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
            <link rel="shortcut icon" href="static/favicon.ico">
            </head>
            <body>
                <h1>Oops, we need more time</h1>
                <p>Sorry, but we are not ready with
                    your seating plan yet.</p>
                <p>Please come back later.</p>
                <p>{}</p>
                <p>
                If you are unable to access this page even
                after waiting for about 6 hours,
                let us know!</p>
            </body>
            </html>
            """.format('' if from_submit_page else 'Please also check that you used the right token'),
            status=503,
            mimetype='text/html'
        )
    table_size = max([len(seats) for seats in tables.values()])

    table_html = convert_tables_html(table_size, persons, tables, coarse_to_original, new_community, clique_names)

    return render_template('retrieve.html',
                           result={
                            'table' : table_html,
                            'job_id' : job_id
                           })


def convert_tables_html(table_size, persons, tables, coarse_to_original, new_community, clique_names):
    def r():
        return random.randint(0,255)

    num_tables = len(tables.keys())

    colours = {}
    original_to_coarse = {}
    coarse_to_community = defaultdict(list)
    for key, items in coarse_to_original.items():
        for item in items:
            original_to_coarse[item] = key
    for community_key, members in new_community.items():
        for member in members:
            coarse_to_community[member].append(community_key)
    
    for community_key in new_community.keys():        
        colour = '#%02X%02X%02X' % (r(),r(),r())
        colours[community_key] = colour

    html = "<table>"
    headers = [str(i) for i in range(1, num_tables + 1)]
    headers_html = "<tr>" + "".join(
        ["<th> Table " + j + "</th>" for j in headers]) + "</tr>"
    html += headers_html
    body_html = ""
    for i in range(0, table_size):
        body_html += "<tr>"
        # for table_num, person_ids in tables.items():
        for table_num in range(0, num_tables):
            try:
                person_ids = tables[str(table_num)]
            except KeyError:
                body_html += '<td>' + "---" + '</td>'
                continue
            try:
                person_id = person_ids[i]
            except IndexError:
                body_html += '<td>' + "---" + '</td>'
                continue

            person_name = persons[int(person_id) - 1]

            communities = coarse_to_community[int(original_to_coarse[person_id])]

            body_html += '<td class="{}">'.format('has-multiple' if len(communities) > 0 else '')
            body_html += str(person_name)

            for community in communities:
                colour = colours[community]
                body_html += '<small class="community-tag" style="color:' + colour + '">' + clique_names[int(community) - 1] + '</span>'

            body_html += '</td>'

        body_html += "</tr>"

    return html + body_html + "</table>"


@app.route('/retrieve_as_xlsx', methods=['POST'])
def retrieve_as_excel():
    job_id = request.form['job_id']
    tables, persons, coarse_to_original, new_community, clique_names = ans_from_s3_ans_bucket(job_id)
    bytes_xlsx = make_workbook(persons, tables)

    return send_file(bytes_xlsx, attachment_filename="seating_plan.xlsx",
                     as_attachment=True)


@app.route('/delete', methods=['POST'])
def delete():
    job_id = request.form['job_id']
    delete_job(job_id)

    return redirect('/?message=deleted')


@app.route('/from_photos')
def login():
    return render_template('from_photos.html', fb_app_id=fb_app_id)


@app.route('/template_spreadsheet', methods=['POST'])
def template_spreadsheet():
    return render_template('template_spreadsheet.html',
                           communities=request.form['communities'],
                           persons=request.form['persons'],
                           fb_app_id=fb_app_id)


@app.route('/template_spreadsheet_contents', methods=['POST'])
def template_spreadsheet_contents():
    def r():
        return random.randint(0,255)

    communities_json = json.loads(request.form['communities'])
    community_names = list(communities_json.keys())
    persons = json.loads(request.form['persons'])

    # merge similar communities
    communities = {key: set(members) for key, members in communities_json.items()}
    colours = {}
    for community_key in communities.keys():
        colour = '#%02X%02X%02X' % (r(),r(),r())
        colours[community_key] = colour

    person_to_community = defaultdict(list)
    for key, members in communities.items():
        for member in members:
            person_to_community[member].append(key)

    merged_communities = merge_similar(communities)

    merged_communities = {key: sorted(list(members)) for key, members in merged_communities.items()}

    html_response = "<table>"
    headers = [str(i) for i in range(1, len(communities) + 1)]
    headers_html = "<tr>" + "".join(
        ["<th> Group " + j + "</th>" for j in headers]) + "</tr>"
    html_response += headers_html
    body_html = ""

    largest_community_size = max([len(community) for community in merged_communities.values()])
    for i in range(0, largest_community_size):
        body_html += "<tr>"

        for community_num in merged_communities.keys():
            try:
                person_ids = merged_communities[community_num]
            except KeyError:
                body_html += '<td>' + "---" + '</td>'
                continue
            try:
                person_id = person_ids[i]
            except IndexError:
                body_html += '<td>' + "---" + '</td>'
                continue

            person_name = persons[int(person_id)]

            communities = person_to_community[person_id]

            body_html += '<td class="{}">'.format('has-multiple' if len(communities) > 0 else '')
            body_html += person_name

            for community in communities:
                colour = colours[community]
                body_html += '<a href="#"><small class="community-tag" style="color:' + colour + '" data-photo-id="' + \
                             str(community) \
                             + '"> Photo ' + str(community_names.index(community)) + '</small><a>'

            body_html += '</td>'

        body_html += "</tr>"

    html_response = html_response + body_html + "</table>"

    html_response += """<form id="template_spreadsheet_download" action="template_spreadsheet_download" method="POST">'
                <input type="hidden" name="communities" value="{}">

                <input type="hidden" name="persons" value="{}">
                <input name=_csrf_token type=hidden value="{}">

                <input class="" type="submit" value="Download">

            </form>""".format(html.escape(request.form['communities']), html.escape(request.form['persons']), generate_csrf_token())

    return app.response_class(
            response=html_response,
            status=200,
            mimetype='text/html_response'
        )


@app.route('/template_spreadsheet_download', methods=['POST'])
def template_spreadsheet_download():
    communities_json = json.loads(request.form['communities'])
    persons = json.loads(request.form['persons'])

    # merge similar communities
    communities = {i + 1 : set(members) for i, (key, members) in enumerate(communities_json.items())}

    communities = merge_similar(communities)

    communities = {key : sorted(members) for key, members in communities.items()}

    bytes_xlsx = make_workbook(persons, communities)
    return send_file(bytes_xlsx, attachment_filename="guest_list.xlsx",
                     as_attachment=True)


@app.route('/privacy', methods=['GET'])
def privacy():
    return send_from_directory('static', 'privacy.html')


@app.route('/terms', methods=['GET'])
def terms():
    return send_from_directory('static', 'terms.html')


def verify_facebook_access_token_and_get_user_id(access_token = None):
    if access_token is None and request.form['facebook_access_token']:
        fb_access_token = request.form['facebook_access_token']
    else:
        fb_access_token = access_token
    graph = facebook.GraphAPI(access_token=fb_access_token, version="2.7")
    debug_data = graph.debug_access_token(fb_access_token, fb_app_id, fb_app_secret)
    return debug_data['data']['user_id']


def get_facebook_app_access_token():
    return facebook.get_app_access_token(fb_app_id, fb_app_secret)


@app.errorhandler(404)
def four_zero_four(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def five_hundred(e):
    return render_template('500.html'), 404


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            print('csrf token missing or invalid', file=sys.stderr)

            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid.uuid4())
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token


@app.context_processor
def inject_yearmonth():
    now = datetime.datetime.utcnow()
    return {'yearmonth': now.strftime("%Y%W")}

@app.teardown_request
def shutdown_session(exception=None):
    """
    Remove database connection
    """

    db.db_session.remove()

@app.after_request
def add_header(response):
    """
    Cache
    """
    if 'html' in response.mimetype:
        response.headers['Cache-Control'] = 'no-cache'
    else:
        response.headers['Cache-Control'] = 'public, max-age=86400'
    return response