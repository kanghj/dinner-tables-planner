
import json
import subprocess
import urllib.parse
import boto3
import shutil
import os

# os.environ['PATH'] = os.environ['PATH'] + ':' + os.environ['LAMBDA_TASK_ROOT']

print('Loading function')

s3 = boto3.client('s3')

def solve_by_clingo(atoms):
    clingo_path = '/usr/local/bin/clingo-5.2.2-linux-x86_64/clingo'
    os.chmod(clingo_path, 0o555)

    proc = subprocess.Popen([clingo_path, '-t 4',
                             '--time-limit=18000', '--stat'],
                            stdout=subprocess.PIPE,  stdin=subprocess.PIPE, encoding='utf8')

    return proc.communicate(input = atoms)


def get_file_and_solve():
    # print("Received event: " + json.dumps(event, indent=2))

    bucket = 'dining-tables-chart'
    key = urllib.parse.unquote_plus('lp/6_big.lp', encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print(response)
        print("CONTENT TYPE: " + response['ContentType'])
        
        atoms = response['Body'].read().decode('utf-8')
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.' +
              'Make sure they exist and your bucket is ' +
              'in the same region as this function.'.format(key, bucket))
        raise e

    print('======') 
    print('Atoms')
    print(atoms)

    ans, stderr = solve_by_clingo(atoms)

    ans_bucket = 'dining-tables-solved'
    ans_key = urllib.parse.unquote_plus('6_big.ans', encoding='utf-8')
    try:
        s3.put_object(Bucket=ans_bucket, Key=ans_key, Body=ans)
    except Exception as e:
        print(e)
        print('Cannot write file')
        raise e
    print('done')

print( os.path.dirname(os.path.realpath(__file__)))
get_file_and_solve()
