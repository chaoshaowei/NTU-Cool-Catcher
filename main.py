import requests
import os
from html.parser import HTMLParser

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
HOST = 'https://cool.ntu.edu.tw'
PATH = '/courses/4641'
URL = HOST+PATH

'''
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
r = s.get(URL, headers=headers)

with open(OUTPUT_DIR, 'w', encoding='utf-8') as f:
    f.write(r.text)

'''

with open(OUTPUT_DIR, 'r', encoding='utf-8') as f:
    text = '\n'.join(f.readlines())

#-----------------------------
# parse homepage
#-----------------------------
class HomepageParser(HTMLParser):
    depth = 0
    in_module_body = False
    module_body_depth = 0

    item_next_type = 'NAN'

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if (tag == 'div'):
            self.depth += 1
            # Find module
            if 'id' in attrs_dict:
                if (attrs_dict['id'] == 'context_modules'):
                    self.in_module_body = True
                    self.module_body_depth = self.depth
                    print(f'found module at div depth ({self.depth})')
            if 'class' in attrs_dict:
                # Find topics
                if (attrs_dict['class'].startswith('item-group-condensed')):
                    print(f"\tTopic: {attrs_dict['aria-label']}")
                # Find individual items
                elif (attrs_dict['class'] == 'module-item-title'):
                    print(f"\t\tfound {self.item_next_type}")
                    self.item_next_type = 'NAN'
        if (tag == 'span'):
            if 'class' in attrs_dict:
                if attrs_dict['class'] == 'type_icon':
                    self.item_next_type = attrs_dict['title']

    def handle_endtag(self, tag):
        if (self.in_module_body):
            if (self.depth == self.module_body_depth):
                self.in_module_body = False
        if (tag == 'div'):
            self.depth -= 1

    def handle_data(self, data):
        return

parser = HomepageParser()
parser.feed(text)
#parser.feed(r.text)
