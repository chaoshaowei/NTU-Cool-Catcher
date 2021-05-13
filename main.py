import requests
import os
from html.parser import HTMLParser

#-----------------------------
# target url
#-----------------------------
HOST = 'https://cool.ntu.edu.tw'
COURSE_NUM = '4641'
PATH = '/courses/' + COURSE_NUM
URL = HOST+PATH

#-----------------------------
# directories
#-----------------------------
WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
COOKIE_DIR = os.path.join(WORKING_DIR, 'cookie.txt')
HEADER_DIR = os.path.join(WORKING_DIR, 'request_header.txt')
OUTPUT_DIR = os.path.join(WORKING_DIR, 'response.html')
OUTPUT2_DIR = os.path.join(WORKING_DIR, 'itemresponse.html')
DOWNLOAD_DIR = os.path.join('Download', COURSE_NUM)
try:
    os.mkdir(os.path.join(WORKING_DIR, 'Download'))
except FileExistsError:
    pass
try:
    os.mkdir(os.path.join(WORKING_DIR, DOWNLOAD_DIR))
except FileExistsError:
    pass

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
'''
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

    in_item = False
    item_depth = 0
    current_item_type = 'NAN'
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
                    self.in_item = True
                    self.item_depth = self.depth
                    self.current_item_type = self.item_next_type
                    self.item_next_type = 'NAN'
        if (tag == 'span'):
            if 'class' in attrs_dict:
                if attrs_dict['class'] == 'type_icon':
                    self.item_next_type = attrs_dict['title']
        if (self.in_item):
            if (tag == 'a'):
                print(f"\t\t\t{attrs_dict['href']}")
                getResources(path=attrs_dict['href'], pageType=self.current_item_type)

    def handle_endtag(self, tag):
        if (self.in_module_body):
            if (self.depth == self.module_body_depth):
                self.in_module_body = False
        if (self.in_item):
            if (self.depth == self.item_depth):
                self.in_item = False
        if (tag == 'div'):
            self.depth -= 1

    def handle_data(self, data):
        return

def getResources(path: str, pageType: str):
    itemRespond = s.get(HOST+path, headers=headers)
    with open(OUTPUT2_DIR, 'w', encoding='utf-8') as f:
        f.write(itemRespond.text)
    
    if pageType != 'Attachment':
        return
    parserA = AttachmentParser()
    parserA.feed(itemRespond.text)
    exit()



#-----------------------------
# parse individual item
#-----------------------------
class AttachmentParser(HTMLParser):
    incomingFilename = False
    filename = 'download'
    def handle_starttag(self, tag, attrs) -> None:
        attrs_dict = dict(attrs)
        if (tag == 'h2'):
            self.incomingFilename = True
        if (tag == 'a'):
            if('download' in attrs_dict):
                if attrs_dict['download'] == 'true':
                    path = attrs_dict['href']
                    print(f"Downloading {HOST}{path}")
                    
                    downloadResponse = requests.get(HOST+path, headers=headers)
                    totalbits = 0
                    if downloadResponse.status_code == 200:
                        with open(self.filename, 'wb') as f:
                            for chunk in downloadResponse.iter_content(chunk_size=1024):
                                if chunk:
                                    totalbits += 1024
                                    f.write(chunk)
    
    def handle_data(self, data: str) -> None:
        if(self.incomingFilename):
            self.incomingFilename = False
            self.filename = os.path.join(DOWNLOAD_DIR, data)


parser0 = HomepageParser()
parser0.feed(text)
#parser.feed(r.text)
