import csv
import uuid
from collections import defaultdict
import subprocess
import os
import re

from werkzeug.utils import secure_filename


def convert(path, num_tables, table_size):

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

    facts.append('total_persons({}).'.format(len(persons)))
    facts.append('total_tables({}).'.format(num_tables))
    facts.append('cliques({}).'.format(len(community.keys())))
    clique_list = [clique for clique in community.keys()]

    facts.append('#const table_size = {}.'.format(table_size))
    for community_name, members in community.items():
        for member in members:
            facts.append('in_clique({}, {}).'.format(
                member, clique_list.index(community_name) + 1))

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


def save_file(file, filename, job_id):
    uniq_filename = filename + '_' + job_id
    path = os.path.join('/tmp/', uniq_filename)
    file.save(path)
    return path


def solve_by_clingo(facts, job_id):
    facts_file = 'facts_' + job_id + '.lp'
    with open(facts_file, 'w+') as lp_file:
        for fact in facts:
            lp_file.write(fact + '\n')
    proc = subprocess.Popen(['exec/clingo', '-t 4',
                             facts_file, 'clingo/enc.lp'],
                            stdout=subprocess.PIPE)
    resp_text = []
    for line in proc.stdout:
        resp_text.append(line.decode('utf-8'))

    os.remove(facts_file)
    return resp_text


def partition_to_tables(num_tables, table_size, csv_file):
    job_id = str(uuid.uuid4())

    path = save_file(csv_file, secure_filename(csv_file.filename), job_id)

    facts, persons = convert(path, num_tables, table_size)
    os.remove(path)

    resp_text = solve_by_clingo(facts, job_id)

    return parse_clingo_out(resp_text), persons
