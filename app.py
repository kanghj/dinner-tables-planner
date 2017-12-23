from flask import Flask, request, redirect, render_template, send_file
from tables import create_file_and_upload_to_s3, ans_from_s3_ans_bucket
from excel_converter import make_workbook
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
        Visit <a href="retrieve?job_id={}">this page</a> after {}
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
    tables, persons, coarse_to_original = ans_from_s3_ans_bucket(job_id)
    if tables is None:
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
                <p>
                If you are unable to access this page even
                after waiting for 6 hours,
                let us know!</p>
            </body>
            </html>
            """,
            status=503,
            mimetype='text/html'
        )
    table_size = max([len(seats) for seats in tables.values()])
    page_html = """
    <!doctype html>
    <html>
    <head>
        <title>Tables</title>
        <link rel="stylesheet"
    href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
    </head>
    <body>
    {}
    <div>
        <p><a href="retrieve_as_xlsx?job_id={}">Download as an Excel file</a>
        </p>
    </div>
    </body>
    </html>
    """.format(convert_tables_html(table_size, persons, tables, coarse_to_original),
               job_id)
    return app.response_class(
        response=page_html,
        status=200,
        mimetype='text/html'
    )


def convert_tables_html(table_size, persons, tables, coarse_to_original):
    import random
    r = lambda: random.randint(0,255)

    num_tables = len(tables.keys())

    colours = {}
    for key in coarse_to_original.keys():
        colour = '#%02X%02X%02X' % (r(),r(),r())
        colours[key] = colour


    original_to_coarse = {}
    for key, items in coarse_to_original.items():
        for item in items:
            original_to_coarse[item] = key

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

            colour = colours[original_to_coarse[int(person_id)]]
            body_html += '<td class="' + colour + '">' + person_name + '</td>'

        body_html += "</tr>"
    return html + body_html + "</table>"


@app.route('/retrieve_as_xlsx', methods=['GET'])
def retrieve_as_excel():
    job_id = request.args.get('job_id')
    tables, persons, coarse_to_original = ans_from_s3_ans_bucket(job_id)
    bytes_xlsx = make_workbook(persons, tables)

    return send_file(bytes_xlsx, attachment_filename="seating_plan.xlsx",
                     as_attachment=True)
