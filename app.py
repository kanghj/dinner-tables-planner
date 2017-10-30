
import os
from flask import Flask, request, redirect
from werkzeug.utils import secure_filename
import uuid
import csv
from collections import defaultdict
import itertools
import subprocess
import json

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/'

ALLOWED_EXTENSIONS = set(['csv'])

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
                community[key].append(persons.index(value))

        knows_all_communities = []
        for community_name, members in community.items():
            knows = itertools.product(members, members)
            knows_without_self_relations = filter(
                lambda pair: pair[0] != pair[1], knows)

            knows_all_communities.extend(knows_without_self_relations)

    facts.append('total_persons({}).'.format(len(persons)))
    facts.append('total_tables({}).'.format(num_tables))

    facts.append('#const table_size = 10.')
    for know in knows_all_communities:
        facts.append('knows' + str(know) + '.')

    return facts


@app.route('/solve', methods=['POST'])
def solve():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        job_id = str(uuid.uuid4())

        uniq_filename = filename + '_' + job_id
        path = os.path.join(app.config['UPLOAD_FOLDER'], uniq_filename)
        file.save(path)

        facts = convert(path, request.form['tables'])

        facts_file = 'facts_' + job_id + '.lp'
        with open(facts_file, 'w+') as lp_file:
            for fact in facts:
                lp_file.write(fact + '\n')

        proc = subprocess.Popen(['exec/clingo', facts_file],
                                stdout=subprocess.PIPE)
        resp_text = []
        for line in proc.stdout:
            resp_text.append(line)

        os.remove(facts_file)

    result_dict = {
        'status': [x.decode('utf-8') for x in resp_text]
    }

    return app.response_class(
        response=json.dumps(result_dict),
        status=200,
        mimetype='application/json'
    )
