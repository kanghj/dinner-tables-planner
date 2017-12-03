from flask import Flask, request, redirect

from tables import create_file_and_upload_to_s3, ans_from_s3_ans_bucket #, partition_from_fil
app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['csv'])

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 megabytes


@app.route('/')
def hello_world():
    return '''
    <!doctype html>
    <html>
    <head>
        <title>Dining Table Seating Chart Planner</title>
    <link rel="stylesheet"
    href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
    </head>
    <body>
    <h1>Upload CSV</h1>
    <p>Each column consists of a header and subsequent rows are names of people</p>
    <form method="post" enctype="multipart/form-data" action="solve">
        <fieldset>
          <input type="file" name="file">
          <label for="tables">Seats per table</label>
          <input type="number" name="size"
                    placeholder="10">
         <input type="submit" value="Upload">
        </fieldset>
    </form>
    </body>
    </html>
    '''


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
    except:
        table_size = 10

    if file.filename == '':
        return redirect(request.url)

    if not file or not allowed_file(file.filename):
        return redirect(request.url)

    # tables, persons = partition_from_file(table_size, file)

    # page_html = """
    # <!doctype html>
    # <html>
    # <head>
    #     <title>Tables</title>
    #     <link rel="stylesheet"
    # href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
    # </head>
    # {}
    # </html>
    # """.format(convert_tables_html(table_size, persons, tables))
    # return app.response_class(
    #     response=page_html,
    #     status=200,
    #     mimetype='text/html'
    # )

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
        Your ID is {}. Please go to this page after {} minutes and collect our proposed seating plan to your event.
    </body>
    """
    return app.response_class(
        response=page_html.format(job_id, '15'),
        status=200,
        mimetype='text/html'
    )

@app.route('/retrieve', methods=['GET'])
def retrieve():
    job_id = request.args.get('job_id')
    tables, persons = ans_from_s3_ans_bucket(job_id)
    table_size = max([len(seats) for seats in person.values()])
    page_html = """
    <!doctype html>
    <html>
    <head>
        <title>Tables</title>
        <link rel="stylesheet"
    href="//cdn.rawgit.com/yegor256/tacit/gh-pages/tacit-css-1.1.1.min.css"/>
    </head>
    {}
    </html>
    """.format(convert_tables_html(table_size, persons, tables))
    return app.response_class(
        response=page_html,
        status=200,
        mimetype='text/html'
    )


def convert_tables_html(table_size, persons, tables):
    num_tables = len(tables.keys())

    html = "<table>"
    headers = [str(i) for i in range(1, num_tables + 1)]
    headers_html = "<tr>" + "".join(
        ["<th> Table" + j + "</th>" for j in headers]) + "</tr>"
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

            body_html += '<td>' + person_name + '</td>'

        body_html += "</tr>"
    return html + body_html + "</table>"
