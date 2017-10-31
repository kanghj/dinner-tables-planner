
import os
from flask import Flask, request, redirect
from werkzeug.utils import secure_filename
import uuid
import csv
from collections import defaultdict
import itertools
import subprocess
import re

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/'

ALLOWED_EXTENSIONS = set(['csv'])

TABLE_SIZE = 10

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 megabytes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello_world():
    return '''
    <!doctype html>
    <title>Table Seating Planner</title>
    <h1>Upload csv file of relationships</h1>
    <form method="post" enctype="multipart/form-data" action="solve">
      <p><input type="file" name="file">
          <input type="number" name="tables">
         <input type=submit value=Upload>
    </form>
    '''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert(path, num_tables):

    facts = []

    persons = []
    with open(path, 'r') as csvfile:

        reader = csv.DictReader(csvfile, delimiter=',')
        community = defaultdict(list)
        for row in reader:
            for key, value in row.items():
                if value not in persons:
                    persons.append(value)
                community[key].append(persons.index(value) + 1)

        knows_all_communities = []
        for community_name, members in community.items():
            knows = itertools.product(members, members)
            knows_without_self_relations = filter(
                lambda pair: pair[0] != pair[1], knows)

            knows_all_communities.extend(knows_without_self_relations)

    facts.append('total_persons({}).'.format(len(persons)))
    facts.append('total_tables({}).'.format(num_tables))

    facts.append('#const table_size = {}.'.format(TABLE_SIZE))
    for know in knows_all_communities:
        facts.append('knows' + str(know) + '.')

    return facts, persons


def parse_clingo_out(output):

    pattern = 'in_table\((\d+),(\d+)\)'
    if isinstance(output, list):
        output_full = '\n'.join(output)
    else:
        output_full = output

    last_answer = output_full.rfind('Answer:')
    output_last = output_full[last_answer:]

    results = re.findall(pattern, output_last)

    tables = defaultdict(list)
    for result in results:
        person, table = result
        tables[table].append(person)
    return tables


@app.route('/solve', methods=['POST'])
def solve():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    num_tables = int(request.form['tables'])

    if file.filename == '':
        return redirect(request.url)

    if not file or not allowed_file(file.filename):
        return redirect(request.url)

    job_id = str(uuid.uuid4())

    path = save_file(file, secure_filename(file.filename), job_id)

    facts, persons = convert(path, num_tables)
    os.remove(path)

    resp_text = solve_by_clingo(facts, job_id)

    tables = parse_clingo_out(resp_text)

    return app.response_class(
        response=convert_tables_html(num_tables, persons, tables),
        status=200,
        mimetype='text/html'
    )


def save_file(file, filename, job_id):
    uniq_filename = filename + '_' + job_id
    path = os.path.join(app.config['UPLOAD_FOLDER'], uniq_filename)
    file.save(path)
    return path


def solve_by_clingo(facts, job_id):
    facts_file = 'facts_' + job_id + '.lp'
    with open(facts_file, 'w+') as lp_file:
        for fact in facts:
            lp_file.write(fact + '\n')
    proc = subprocess.Popen(['exec/clingo', facts_file, 'clingo/enc.lp'],
                            stdout=subprocess.PIPE)
    resp_text = []
    for line in proc.stdout:
        resp_text.append(line.decode('utf-8'))

    os.remove(facts_file)
    return resp_text


def convert_tables_html(num_tables, persons, tables):
    html = "<table>"
    headers = [str(i) for i in range(1, num_tables + 1)]
    headers_html = "<th>" + "".join(
        ["<td> Table" + j + "</td>" for j in headers]) + "</th>"
    html += headers_html
    body_html = ""
    for i in range(0, TABLE_SIZE):
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
