import requests
import os

s = requests.Session() 
# all cookies received will be stored in the session object

#-----------------------------
# directories
#-----------------------------
WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
COOKIE_DIR = os.path.join(WORKING_DIR, 'cookie.txt')
HEADER_DIR = os.path.join(WORKING_DIR, 'request_header.txt')
OUTPUT_DIR = os.path.join(WORKING_DIR, 'response.html')

url = 'https://cool.ntu.edu.tw/courses/4641'

headers = {}
with open(HEADER_DIR, 'r') as f:
    lines = f.readlines()
    for line in lines:
        line_args = line.split(':')
        key = line_args[0].strip()
        value = ':'.join(line_args[1:]).strip()
        headers[key] = value
    with open(COOKIE_DIR, 'r') as f:
        raw_cookie = ''.join(f.readlines())
        headers['Cookie'] = raw_cookie

r = s.get(url, headers=headers)

with open(OUTPUT_DIR, 'w', encoding='utf-8') as f:
    f.write(r.text)

for key, value in r.headers.items():
    print(f'{key}: {value}')