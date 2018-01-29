import subprocess
import urllib.parse
import boto3
import os
import sys
import asyncio


# os.environ['PATH'] = os.environ['PATH'] + ':' + os.environ['LAMBDA_TASK_ROOT']

print('Loading function')

s3 = boto3.client('s3')

job_done = False

async def solve_by_clingo(atoms):
    global job_done
    print('Going to start clingo')

    clingo_path = '/usr/local/bin/clingo-5.2.2-linux-x86_64/clingo'
    os.chmod(clingo_path, 0o555)

    with open('input.txt', 'w+') as infile:
        infile.write(atoms)

    proc = await asyncio.create_subprocess_exec(clingo_path, '-t 8',
                             '--time-limit=36000',
                            stdout=open('output.txt', 'w+'), stdin=open('input.txt', 'r'), stderr=subprocess.PIPE, encoding='utf8')
    returncode = await proc.wait()
    print('clingo is done')

    job_done = True



def stream_output(atoms, path_to_file):
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(solve_by_clingo(atoms)),
        asyncio.ensure_future(update_s3(path_to_file)),
        ]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()


async def update_s3(path_to_file):
    while not job_done:
        await asyncio.sleep(5)
        ans_bucket = 'dining-tables-solved'
        filename = path_to_file.split('/')[-1]
        ans_key = urllib.parse.unquote_plus(filename + '.ans', encoding='utf-8')
        try:
            with open('output.txt') as infile:
                body = infile.read()
            s3.put_object(Bucket=ans_bucket, Key=ans_key, Body=body)
        except Exception as e:
            print(e)
            print('Cannot write to s3')

            raise e


def get_file_and_solve():
    # print("Received event: " + json.dumps(event, indent=2))

    bucket = 'dining-tables-chart'
    path_to_file = sys.argv[1]
    key = urllib.parse.unquote_plus(path_to_file, encoding='utf-8')
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

    stream_output(atoms, path_to_file)

    # final write
    ans_bucket = 'dining-tables-solved'
    filename = path_to_file.split('/')[-1]
    ans_key = urllib.parse.unquote_plus(filename + '.ans', encoding='utf-8')
    try:
        with open('output.txt') as infile:
            body = infile.read()
        s3.put_object(Bucket=ans_bucket, Key=ans_key, Body=body)
    except Exception as e:
        print(e)
        print('Cannot write file')
        raise e
    print('done')

print( os.path.dirname(os.path.realpath(__file__)))
get_file_and_solve()