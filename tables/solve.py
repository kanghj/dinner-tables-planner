import csv
import uuid
from collections import defaultdict
import subprocess
import os
import math
import re
import tempfile
import boto3
import pickle
from werkzeug.utils import secure_filename

from .coarser import coarse_local

s3 = boto3.client('s3')

def represent_in_asp(coarse_to_original, new_community, new_table_sz, num_persons, persons, presolved, table_size):
    facts = []
    for key, members in coarse_to_original.items():
        facts.append('person({}).'.format(key))
    num_tables = math.ceil(num_persons / table_size)
    facts.append('total_tables({}).'.format(num_tables))
    facts.append('cliques({}).'.format(len(new_community.keys())))
    clique_list = [clique for clique in new_community.keys()]
    for table_num, table_sz in enumerate(new_table_sz):
        facts.append('table_size({}, {}).'.format(table_num, table_sz))
    for community_name, members in new_community.items():
        for member in members:
            facts.append('in_clique({}, {}).'.format(
                member, clique_list.index(community_name) + 1))
    for presolved_fact in presolved:
        facts.append('{}({},{}).'.format(
            presolved_fact[0], presolved_fact[1], presolved_fact[2]))
    return facts, persons, coarse_to_original


def community_and_persons_from_file(path):
    persons = []
    with open(path, 'r') as csvfile:

        reader = csv.DictReader(csvfile, delimiter=',')
        community = defaultdict(list)
        clique_names = []
        for row in reader:
            for key, value in row.items():
                clique_names.append(key)

                if value not in persons:
                    persons.append(value)
                community[clique_names.index(key) + 1].append(
                    persons.index(value) + 1)
    return community, persons


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


def save_file(tmpdir_path, file, filename, job_id):
    uniq_filename = filename + '_' + job_id

    path = os.path.join(tmpdir_path, uniq_filename)
    file.save(path)
    return path


def write_facts_to_file(facts, job_id):
    facts_file = 'facts_' + job_id + '.lp'
    with open(facts_file, 'w+') as lp_file:
        for fact in facts:
            lp_file.write(fact + '\n')
    return facts_file


def get_clingo_output(facts_file):
    proc = subprocess.Popen(['exec/clingo', '-t 8',
                             '--time-limit=25',
                             facts_file, 'clingo/enc.lp'],
                            stdout=subprocess.PIPE)
    resp_text = []
    for line in proc.stdout:
        resp_text.append(line.decode('utf-8'))
    return resp_text


def solve_by_clingo(facts, job_id):
    facts_file = write_facts_to_file(facts, job_id)

    resp_text = get_clingo_output(facts_file)

    os.remove(facts_file)
    return resp_text


def partition_from_file(table_size, csv_file):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmpdir:
        path = save_file(tmpdir, csv_file,
                         secure_filename(csv_file.filename), job_id)

        community, persons = community_and_persons_from_file(path)

    return partition(community, job_id, persons, table_size)


def create_file_and_upload_to_s3(table_size, csv_file):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmpdir:
        path = save_file(tmpdir, csv_file,
                         secure_filename(csv_file.filename), job_id)

        community, persons = community_and_persons_from_file(path)

    num_persons = len(persons)
    new_table_sz, new_community, coarse_to_original, presolved = \
        coarse_local(community, table_size)
    facts, persons, coarse_nodes_to_persons = represent_in_asp(
        coarse_to_original, new_community, new_table_sz,
        num_persons, persons, presolved, table_size)
    # facts_file = write_facts_to_file(facts, job_id)

    s3.Bucket('dining-tables-chart').put_object(Key='lp/{}.lp'.format(job_id),
                                                Body='\n'.join(facts))

    s3.Bucket('dining-tables-solved')
        .put_object(Key='pickles/{}'.format(job_id),
                    Body=pickle.dump(coarse_nodes_to_persons))
    return job_id


def get_tables_and_persons_from_clingo_out(resp_text, coarse_nodes_to_persons):
    coarse_tables = parse_clingo_out(resp_text)
    tables = {}
    for table_num, nodes in coarse_tables.items():
        original_persons = []
        for node in nodes:
            original_persons.extend(coarse_nodes_to_persons[int(node)])
        tables[table_num] = original_persons
    return tables, persons


def partition(community, job_id, persons, table_size):
    num_persons = len(persons)
    new_table_sz, new_community, coarse_to_original, presolved = \
        coarse_local(community, table_size)
    facts, persons, coarse_nodes_to_persons = represent_in_asp(
        coarse_to_original, new_community, new_table_sz,
        num_persons, persons, presolved, table_size)
    resp_text = solve_by_clingo(facts, job_id)
    return get_tables_and_persons_from_clingo_out(resp_text, coarse_nodes_to_persons)


def ans_from_s3_ans_bucket(job_id):
    readfile = s3.Bucket('dining-tables-solved')
        .get_object(Key='{}.lp.ans'.format(job_id))['Body'].read().decode('utf-8')
    coarse_to_original = pickle.load(
        s3.Bucket('dining-tables-solved').get_object(Key='pickles/{}'.format(job_id))['Body'].read())
    return get_tables_and_persons_from_clingo_out(readfile, coarse_to_original)
