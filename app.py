import sys
from flask import Flask, request, redirect, render_template, send_file
from tables import create_file_and_upload_to_s3, ans_from_s3_ans_bucket
from excel_converter import make_workbook
import random
from collections import defaultdict
app = Flask(__name__, static_url_path='/static')

ALLOWED_EXTENSIONS = set(['csv', 'xlsx'])

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 megabytes


@app.route('/')
def hello_world():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/solve', methods=['POST'])
def solve():
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

    job_id = create_file_and_upload_to_s3(table_size, file)
    page_html = """
    <!doctype html>
    <html>
    <head>
        <title>Tables</title>
        <link rel="stylesheet"
    href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
    </head>
    <body>
        <p>
        Your token is {}. Please copy and paste it somewhere.
        </p>
        <p>
        Visit <a href="retrieve?job_id={}&from_submit_page=true">this page</a> after {}
        minutes and collect our proposed seating plan to your event.
        </p>
    </body>
    """
    return app.response_class(
        response=page_html.format(job_id, job_id, '15'),
        status=200,
        mimetype='text/html'
    )


@app.route('/retrieve', methods=['GET'])
def retrieve():
    job_id = request.args.get('job_id')
    tables, persons, coarse_to_original, new_community, clique_names = ans_from_s3_ans_bucket(job_id)
    if tables is None:
        from_submit_page = request.args.get('from_submit_page')
        return app.response_class(
            response="""
            <!doctype html>
            <html>
            <head>
                <title>Not ready yet</title>
                <link rel="stylesheet"
            href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
            </head>
            <body>
                <h1>Oops, we need more time</h1>
                <p>Sorry, but we are not ready with
                    your seating plan yet.</p>
                <p>Please come back later.</p>
                <p>{}</p>
                <p>
                If you are unable to access this page even
                after waiting for 6 hours,
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
                           result = {
                            'table' : table_html,
                            'job_id' : job_id
                           }
    )



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
            body_html += person_name

            for community in communities:
                colour = colours[community]
                body_html += '<small class="community-tag" style="color:' + colour + '">' + clique_names[int(community) - 1] + '</span>'

            body_html += '</td>'

        body_html += "</tr>"

    return html + body_html + "</table>"


@app.route('/retrieve_as_xlsx', methods=['GET'])
def retrieve_as_excel():
    job_id = request.args.get('job_id')
    tables, persons, coarse_to_original, new_community = ans_from_s3_ans_bucket(job_id)
    bytes_xlsx = make_workbook(persons, tables)

    return send_file(bytes_xlsx, attachment_filename="seating_plan.xlsx",
                     as_attachment=True)
