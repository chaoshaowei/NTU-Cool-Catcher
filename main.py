import requests
import os
from html.parser import HTMLParser
import json

from requests.api import head

#-----------------------------
# target url
#-----------------------------
HOST = 'https://cool.ntu.edu.tw'
COURSE_NUM = '4641'
PATH = '/courses/' + COURSE_NUM
URL = HOST+PATH

VIDEOHOST = 'https://lti.dlc.ntu.edu.tw'


#-----------------------------
# directories
#-----------------------------
WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
COOKIE_DIR = os.path.join(WORKING_DIR, 'cookie.txt')

HEADER_DIR = os.path.join(WORKING_DIR, 'Templates', 'request_header.txt')
VIDEO_POST_HEADER_DIR = os.path.join(WORKING_DIR, 'Templates', 'video_post_request_header.txt')
JS_GET_HEADER_DIR = os.path.join(WORKING_DIR, 'Templates', 'js_get_request_header.txt')
try:
    os.mkdir(os.path.join(WORKING_DIR, 'Templates'))
except FileExistsError:
    pass

OUTPUT1_DIR = os.path.join(WORKING_DIR, 'Responses', 'response.html')
OUTPUT2_DIR = os.path.join(WORKING_DIR, 'Responses', 'itemresponse.html')
OUTPUT3_DIR = os.path.join(WORKING_DIR, 'Responses', 'video_post_response.html')
OUTPUT4_DIR = os.path.join(WORKING_DIR, 'Responses', 'js_get_response.json')
try:
    os.mkdir(os.path.join(WORKING_DIR, 'Responses'))
except FileExistsError:
    pass

DOWNLOAD_DIR = os.path.join(WORKING_DIR, 'Download', COURSE_NUM)
DOWNLOAD_SUBDIR = 'default'
try:
    os.mkdir(os.path.join(WORKING_DIR, 'Download'))
except FileExistsError:
    pass
try:
    os.mkdir(DOWNLOAD_DIR)
except FileExistsError:
    pass

#-----------------------------
# headers
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

post_headers = {}

#-----------------------------
# get course homepage response
#-----------------------------
s = requests.Session()
'''
r = s.get(URL, headers=headers)

with open(OUTPUT1_DIR, 'w', encoding='utf-8') as f:
    f.write(r.text)
'''

with open(OUTPUT1_DIR, 'r', encoding='utf-8') as f:
    text = '\n'.join(f.readlines())

#-----------------------------
# parse homepage
#-----------------------------
class HomepageParser(HTMLParser):
    '''
    A program to handle and parse cached data.
    Target URL: https://cool.ntu.edu.tw/courses/xxxx

    Usage:
    - HompageParser().feed(URL)
    '''
    depth = 0
    
    # Module body
    # finds <div id='context_modules'>
    in_module_body = False
    module_body_depth = 0

    # Topic
    # finds <div class='item-group-condensed'>

    # Individual item
    # finds <div class='module-item-title'>
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
                    global DOWNLOAD_SUBDIR
                    DOWNLOAD_SUBDIR = attrs_dict['aria-label']
                    try:
                        os.mkdir(os.path.join(DOWNLOAD_DIR, DOWNLOAD_SUBDIR))
                    except FileExistsError:
                        pass
                # Find individual items
                elif (attrs_dict['class'] == 'module-item-title'):
                    print(f"\t\tfound {self.item_next_type}")
                    self.in_item = True
                    self.item_depth = self.depth
                    self.current_item_type = self.item_next_type
                    self.item_next_type = 'NAN'
        elif (tag == 'span'):
            # Topics name
            if 'class' in attrs_dict:
                if attrs_dict['class'] == 'type_icon':
                    self.item_next_type = attrs_dict['title']
            # Individual item
        elif (self.in_item):
            if (tag == 'a'):
                print(f"\t\t\t{attrs_dict['href']}")
                self.getItemResource(path=attrs_dict['href'], pageType=self.current_item_type)

    def handle_endtag(self, tag):
        if (self.in_item):
            if (self.depth == self.item_depth):
                self.in_item = False
        elif (self.in_module_body):
            if (self.depth == self.module_body_depth):
                self.in_module_body = False
        if (tag == 'div'):
            self.depth -= 1
    
    def getItemResource(self, path: str, pageType: str):
        itemRespond = s.get(HOST+path, headers=headers)
        
        with open(OUTPUT2_DIR, 'w', encoding='utf-8') as f:
            f.write(itemRespond.text)
        
        if pageType == 'Attachment':
            parserA = AttachmentParser()
            parserA.feed(itemRespond.text)

        if pageType == 'External Tool':
            post_headers['Referer'] = HOST+path
            parserV = VideoParser()
            parserV.feed(itemRespond.text)

#-----------------------------
# parse individual item
#-----------------------------
class VideoParser(HTMLParser):

    in_form = False
    form_action_url = ''

    form_data = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if (tag == 'form'):
            self.in_form = True
            self.form_action_url = attrs_dict['action']
        elif (tag == 'input'):
            self.form_data[attrs_dict['id']] = attrs_dict['value']

    def handle_endtag(self, tag):
        if (tag == 'form'):
            # Posting form
            print('\t\t\t\tposting form')
            with open(VIDEO_POST_HEADER_DIR, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line_args = line.split(':')
                    key = line_args[0].strip()
                    value = ':'.join(line_args[1:]).strip()
                    post_headers[key] = value
            self.in_form = False
            lms_session = requests.session()
            postRespond = lms_session.post(self.form_action_url, headers=post_headers, data=self.form_data)
            lms_cookies = {}
            for post_header_index, post_header_value in postRespond.headers.items():
                if post_header_index.lower() == 'set-cookie':
                    cookie_name, cookie_value = post_header_value.split(';')[0].split('=')
                    lms_cookies[cookie_name.strip()] = cookie_value.strip()
            with open(OUTPUT3_DIR, 'w', encoding='utf-8') as f:
                for post_header_index, post_header_value in postRespond.headers.items():
                    f.write(f'{post_header_index}:\t{post_header_value}\n')
                f.write(f'{postRespond.text}')
            video_num_str = self.form_action_url.split('/')[-2]
            # Getting JSON
            print('\t\t\t\tgetting json')
            js_get_url = f'https://lti.dlc.ntu.edu.tw/api/v1/courses/{COURSE_NUM}/videos/{video_num_str}'
            js_get_headers = {}
            with open(JS_GET_HEADER_DIR, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line_args = line.split(':')
                    key = line_args[0].strip()
                    value = ':'.join(line_args[1:]).strip()
                    js_get_headers[key] = value
            js_get_headers['Referer'] = f'{js_get_url}?roles[]=instructor&roles[]=student&roles[]=learner&roles[]=user&locale=zh-Hant'
            js_get_headers['Cookie'] = ';'.join([ f'{i}={v}' for i, v in lms_cookies.items()])
            jsGetRespond = lms_session.get(js_get_url, headers=js_get_headers)
            # Downloading Video
            jsonifiedRespond = json.loads(jsGetRespond.text)
            with open(OUTPUT4_DIR, 'w', encoding='utf-8') as f:
                f.write(f'{jsGetRespond.text}')
            videoUrl = jsonifiedRespond['video']['resolutions'][-1]['src']
            videoFilename = jsonifiedRespond['video']['title'] + '.mp4'
            print(f'\t\t\t\tdownloading {videoFilename}')
            downloadResponse = requests.get(videoUrl)
            totalbits = 0
            if downloadResponse.status_code == 200:
                with open(os.path.join(DOWNLOAD_DIR, DOWNLOAD_SUBDIR, videoFilename), 'wb') as f:
                    for chunk in downloadResponse.iter_content(chunk_size=1024):
                        if chunk:
                            totalbits += 1024
                            f.write(chunk)

class AttachmentParser(HTMLParser):
    '''
    A program to download attachment type pages
    Target URL: https://cool.ntu.edu.tw/courses/xxxx/files/yyyyyy

    Usage:
    - AttachmentParser().feed(URL)
    '''
    incomingFilename = False
    filename = os.path.join(DOWNLOAD_DIR, DOWNLOAD_SUBDIR, 'downloads')
    def handle_starttag(self, tag, attrs) -> None:
        attrs_dict = dict(attrs)
        if (tag == 'h2'):
            self.incomingFilename = True
        if (tag == 'a'):
            if('download' in attrs_dict):
                if attrs_dict['download'] == 'true':
                    path = attrs_dict['href']
                    print(f"\t\t\t\tdownloading {self.filename}")
                    
                    downloadResponse = requests.get(HOST+path, headers=headers)
                    totalbits = 0
                    if downloadResponse.status_code == 200:
                        with open(os.join(DOWNLOAD_DIR, DOWNLOAD_SUBDIR, self.filename), 'wb') as f:
                            for chunk in downloadResponse.iter_content(chunk_size=1024):
                                if chunk:
                                    totalbits += 1024
                                    f.write(chunk)
    
    def handle_data(self, data: str) -> None:
        if(self.incomingFilename):
            self.incomingFilename = False
            self.filename = data


if __name__ == '__main__':
    parser0 = HomepageParser()
    parser0.feed(text)
    #parser.feed(r.text)
