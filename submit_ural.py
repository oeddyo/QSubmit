from pyquery import PyQuery as pq
import requests
import sys
import time

# configuration.
judge_id = "74814MC"
user_name = "masque"

language_mapping = {
        'cpp': 21,
        'java': 12,
        'py': 16,
        'rb': 18,
        }

source_file_name = sys.argv[1]
dot_position = source_file_name.find(".")

if dot_position==-1:
    raise('Invalid source file name...')

name_extension = source_file_name[source_file_name.find(".")+1:]

if name_extension not in language_mapping:
    raise("Not supporting " + name_extension + "file yet... modify me please (it's easy!)")

source = open(source_file_name, 'r').read()
data = {'Source': source, 
        'JudgeID': judge_id,
        'ProblemNum': source_file_name[:-(len(name_extension)+1)],
        'Action': 'submit', 
        'SpaceID': 1, 
        'Language': language_mapping[name_extension] 
        }

session = requests.session()
url = "http://acm.timus.ru/submit.aspx?space=1"

print 'Posting source code...'
r = requests.post(url, data=data)
print 'Succesfully posted your code... Waiting for result!'

result_url = "http://acm.timus.ru/status.aspx?space=1"
retry_countdown = 10

wait_chars = ["[->     ]", "[-->    ]", "[--->   ]", "[---->  ]", "[-----> ]"]  
wait_char_idx = 0

while True:
    
    sec = 0 
    while sec<=4:
        s = wait_chars[sec]
        sys.stdout.write('%s\r' % s)
        sys.stdout.flush()
        time.sleep(1) 
        sec += 1
    
    retry_countdown -= 1
    if retry_countdown <= 0:
        print 'Giving up... network problem. Maybe submit later.'
        break

    r = requests.get(result_url)
    html = r.text
    d = pq(html)
    should_refresh = False
    result_buf = []

    status_board = []
    for i in range(len(d('.even'))):
        status_board.append( d('.even')[i])
        status_board.append( d('.odd')[i])

    for n, row in enumerate( status_board):
        current_jquery_obj = pq(row)
        coder = current_jquery_obj('.coder').text()
        status = current_jquery_obj('td').eq(5).text()

        if coder == user_name:
            if status=='Compiling' or status == 'Running':
                #print "Still running or compling... Wait a little bit I'm refreshing"
                should_refresh = True
                break
            result_buf.append(current_jquery_obj.text()) 
    
    if not should_refresh:
        print '\n\n'
        if result_buf[0].find("Accept")!=-1:
            print '->Congrats! Accepted!'
        else:
            print '->Not Accepted'
        print '\n\n'
        print result_buf[0]
        break

    time.sleep(5)
    print 'Network slow.... refreshing status..., retry = ' + str(retry_countdown)
