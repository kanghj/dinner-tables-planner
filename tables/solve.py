import csv
import uuid
from collections import defaultdict
import subprocess
import os
import re
import tempfile
import boto3
import json

import math

from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
from openpyxl import load_workbook

from .coarser import coarse_local

s3 = boto3.client('s3')


def represent_in_asp(coarse_to_original, new_community,
                     new_table_sz, persons, presolved,
                     clique_weights, table_size):
    facts = []
    for key, members in coarse_to_original.items():
        facts.append('person({}).'.format(key))
        already_assigned_to_table = any(
            [x[0] == 'in_table' and x[1] == key for x in presolved])
        facts.append('person_size({}, {}).'.format(
            key, 1 if already_assigned_to_table else len(members)))

    # facts.append('total_tables({}).'.format(len(new_table_sz)))
    num_original_persons = len(
        [value for values in coarse_to_original.values()
         for value in values])

    facts.append('total_tables_min({}).'.format(
        min(math.ceil(num_original_persons / table_size), len(new_table_sz))))
    facts.append('total_tables_max({}).'.format(
        max(math.ceil(num_original_persons / table_size), len(new_table_sz))))
    facts.append('cliques({}).'.format(len(new_community.keys())))
    clique_list = [clique for clique in new_community.keys()]
    for table_num, table_sz in enumerate(new_table_sz):
        facts.append('table_size({}, {}).'.format(table_num, table_sz))

    for community_name, members in new_community.items():
        clique_number = clique_list.index(community_name) + 1

        weight = clique_weights[community_name] \
            if community_name in clique_weights else 1

        clique_weight_fact = 'clique_weight({}, {}).'.format(
            clique_number, weight)
        if clique_weight_fact not in facts:
            facts.append(clique_weight_fact)
        clique_size_fact = 'clique_size({}, {}).'.format(
            clique_number, len(members))
        if clique_size_fact not in facts:
            facts.append(clique_size_fact)

        for member in members:
            fact = 'in_clique({}, {}).'.format(
                member, clique_number)
            if fact not in facts:
                facts.append(fact)

    for presolved_fact in presolved:
        if len(presolved_fact) > 2:
            fact = '{}({},{}).'.format(
                presolved_fact[0], presolved_fact[1], presolved_fact[2])
        else:
            fact = '{}({}).'.format(
                presolved_fact[0], presolved_fact[1])
        if fact not in facts:
            facts.append(fact)

    return facts, persons, coarse_to_original


def community_and_persons_from_file(path, filetype):
    persons = []

    community = defaultdict(list)

    if filetype.endswith('csv'):

        with open(path, 'r') as csvfile:

            reader = csv.DictReader(csvfile, delimiter=',')
            clique_names = []
            for row in reader:
                for key, value in row.items():
                    if key not in clique_names:
                        clique_names.append(key)

                    if len(value) == 0:
                        continue

                    if value not in persons:
                        persons.append(value)
                    community[clique_names.index(key) + 1].append(
                        persons.index(value) + 1)
    elif filetype.endswith('xlsx'):
        wb = load_workbook(path)
        sheet = wb.get_active_sheet()

        clique_names = []
        for i, column in enumerate(sheet.columns):
            col_name = None
            for j, cell in enumerate(column):
                if j == 0:
                    col_name = cell.value
                    clique_names.append(col_name)
                    continue
                if cell.value is None or \
                        (isinstance(cell.value, str) and
                         len(cell.value) == 0):
                    continue
                if cell.value not in persons:
                    persons.append(cell.value)
                community[clique_names.index(col_name) + 1].append(
                    persons.index(cell.value) + 1)

    assert len(clique_names) == len(set(clique_names))
    return community, persons, clique_names


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
    uniq_filename = job_id + '_' + filename

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


def add_solving_atoms(facts):
    new_facts = facts.copy()
    with open('clingo/enc.lp') as enc_file:
        for line in enc_file:
            new_facts.append(line)
    return new_facts


def create_staging_file_and_upload_to_s3(table_size, uploaded_file):

    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmpdir:
        filename, file_extension = os.path.splitext(uploaded_file.filename)
        path = save_file(tmpdir, uploaded_file,
                         secure_filename(uploaded_file.filename), job_id)

        community, persons, clique_names = community_and_persons_from_file(
            path, file_extension)

    s3.put_object(
        Bucket='dining-tables-chart',
        Key='pickles/{}'.format(job_id),
        Body=json.dumps((community, persons, clique_names, table_size)))

    return job_id, community, persons, clique_names


def create_file_and_upload_to_s3(job_id, clique_weights_raw):

    community, persons, clique_names, table_size = json.loads(
        s3.get_object(
            Bucket='dining-tables-chart',
            Key='pickles/{}'.format(job_id))['Body'].read().decode('utf-8'))

    # convert keys of clique_weights to use the clique numbers instead
    clique_weights = {str(clique_names.index(key) + 1): int(values)
                      for key, values in clique_weights_raw.items()}

    new_table_sz, new_community, coarse_to_original, presolved = \
        coarse_local(community, table_size, clique_weights)

    facts, persons, coarse_nodes_to_persons = represent_in_asp(
        coarse_to_original, new_community, new_table_sz,
        persons, presolved, clique_weights, table_size)

    facts = add_solving_atoms(facts)
    s3.put_object(Bucket='dining-tables-chart',
                  Key='lp/{}.lp'.format(job_id),
                  Body='\n'.join(facts))

    s3.put_object(
            Bucket='dining-tables-solved',
            Key='pickles/{}'.format(job_id),
            Body=json.dumps((persons, coarse_nodes_to_persons,
                             clique_names, new_community)))
    return job_id


def get_tables_from_clingo_out(resp_text, coarse_nodes_to_persons):
    coarse_tables = parse_clingo_out(resp_text)
    tables = {}
    for table_num, nodes in coarse_tables.items():
        original_persons = []
        for node in nodes:
            try:
                original_persons.extend(coarse_nodes_to_persons[int(node)])
            except KeyError as e:
                original_persons.extend(coarse_nodes_to_persons[node])
        tables[table_num] = original_persons
    return tables


def partition(community, job_id, persons, table_size, clique_weights):
    new_table_sz, new_community, coarse_to_original, presolved = \
        coarse_local(community, table_size, clique_weights)
    facts, persons, coarse_nodes_to_persons = represent_in_asp(
        coarse_to_original, new_community, new_table_sz,
        persons, presolved, clique_weights, table_size)

    resp_text = solve_by_clingo(facts, job_id)

    return get_tables_from_clingo_out(
        resp_text, coarse_nodes_to_persons), persons


def ans_from_s3_ans_bucket(job_id):
    try:
        readfile = s3.get_object(
            Bucket='dining-tables-solved',
            Key='{}.lp.ans'.format(job_id))['Body'].read().decode('utf-8')
    except ClientError as ex:
        if ex.response['Error']['Code'] == 'NoSuchKey':
            return None, None, None, None, None

    persons, coarse_to_original, clique_names, new_community = json.loads(
        s3.get_object(
            Bucket='dining-tables-solved',
            Key='pickles/{}'.format(job_id))['Body'].read().decode('utf-8'))

    return get_tables_from_clingo_out(readfile, coarse_to_original), \
        persons, coarse_to_original, new_community, clique_names


def delete_job(job_id):
    """
    Deletes s3 files relating to job_id.
    TODO Should kill any Batch program too
    :param job_id:
    :return:
    """
    s3.delete_object(Bucket='dining-tables-solved',
                     Key='{}.lp.ans'.format(job_id))
    s3.delete_object(Bucket='dining-tables-solved',
                     Key='pickles/{}'.format(job_id),)
    s3.delete_object(Bucket='dining-tables-chart',
                     Key='lp/{}.lp'.format(job_id))
