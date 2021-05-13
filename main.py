import requests
import os

#-----------------------------
# directories
#-----------------------------
WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
COOKIE_DIR = os.path.join(WORKING_DIR, 'cookie.txt')
HEADER_DIR = os.path.join(WORKING_DIR, 'request_header.txt')
OUTPUT_DIR = os.path.join(WORKING_DIR, 'response.html')

#-----------------------------
# target url
#-----------------------------
url = 'https://cool.ntu.edu.tw/courses/4641'


#-----------------------------
# directories
#-----------------------------
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


#-----------------------------
# get course homepage response
#-----------------------------
s = requests.Session() 
r = s.get(url, headers=headers)

with open(OUTPUT_DIR, 'w', encoding='utf-8') as f:
    f.write(r.text)

