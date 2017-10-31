from flask import Flask, request, redirect

from tables import partition_to_tables

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['csv'])

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 megabytes


@app.route('/')
def hello_world():
    return '''
    <!doctype html>
    <title>Table Seating Planner</title>
    <h1>Upload csv file of relationships</h1>
    <form method="post" enctype="multipart/form-data" action="solve">
      <p><input type="file" name="file">
          <input type="number" name="tables" placeholder="Number of tables">
          <input type="number" name="size"
                    placeholder="Number of seats in a table">
         <input type="submit" value="Upload">
    </form>
    '''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/solve', methods=['POST'])
def solve():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    num_tables = int(request.form['tables'])
    table_size = int(request.form['size'])

    if file.filename == '':
        return redirect(request.url)

    if not file or not allowed_file(file.filename):
        return redirect(request.url)

    tables, persons = partition_to_tables(num_tables, table_size, file)

    return app.response_class(
        response=convert_tables_html(num_tables, table_size, persons, tables),
        status=200,
        mimetype='text/html'
    )


def convert_tables_html(num_tables, table_size, persons, tables):
    html = "<table>"
    headers = [str(i) for i in range(1, num_tables + 1)]
    headers_html = "<tr>" + "".join(
        ["<th> Table" + j + "</th>" for j in headers]) + "</tr>"
    html += headers_html
    body_html = ""
    for i in range(0, table_size):
        body_html += "<tr>"
        # for table_num, person_ids in tables.items():
        for table_num in range(1, num_tables + 1):
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
    html += body_html + "</table>"
    return html
