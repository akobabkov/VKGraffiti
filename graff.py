# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
перетащи каринку или аудио или скопируй на них ссылку и введи пир/выбери беседу
"""
import vk
import sys
import requests as req
import clipboard
import pickle

try:
    with open('cache.pickle', 'rb') as f:
        cache = pickle.load(f)
except:
    cache = {}

token = 'TOKEN' #скопируй сюда свой токен из VK
ap = vk.API(vk.Session(token), 109, v='5.60')
pe = 2000000000
peer = 0
if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = clipboard.paste()
    if not arg.startswith('http'):
        arg = input('Укажите путь к файлу или ссылку на него: ')
        if arg.startswith('"'):
            arg = arg[1:-1]
if arg in ('--help', 'help'):
    print(__doc__)
    exit()


path = arg

if '://' in path[3:] and ('.mp3' in path or '.ogg' in path or '.flac' in path or '.m4a' in path or '.wav' in path or '.amr' in path):
    type = 'audio_message'
    ext = '.mp3'
elif path.endswith('.mp3') or path.endswith('.flac') or path.endswith('.ogg') or path.endswith('.m4a') or path.endswith('.wav') or path.endswith('.amr'):
    type = 'audio_message'
    ext = '.' + path.split('.')[-1]
else:
    type = 'graffiti'
    ext = '.png'


def get_title(prof):
    return prof.get('first_name', '') + prof.get('name', ' ') + prof.get('last_name', '')

def upload_goose(path, type, ext):
    if path not in cache:
        if '://' in path[3:]:
            a = req.get(path).content
        else:
            with open(path, 'rb') as f:
                a = f.read()
        serv = ap.docs.getUploadServer(type=type)['upload_url']
        print('file uploading...')
        ab = req.post(serv, files={"file": ("mickle_doc"+ext, a)})
        print('file uploaded. saving...')
        if 'error' in ab.json(): 
        	print(ab.json()['error'])
        	if not input('>> retry? '):
        		return upload_goose(path, type, ext)
        	exit()
        att = ap.docs.save(file=ab.json()['file'], title='mickle_doc'+ext)[0]
        att = 'doc{owner_id}_{id}'.format(**att)
        cache[path] = att
        with open('cache.pickle', 'wb') as f:
            pickle.dump(cache, f)
    else:
        att = cache[path]
    print('success')
    return att

att = upload_goose(path, type, ext)

if not peer:
    a = ap.messages.getDialogs(count=5, extended=1, preview_length=50)
    profs = a['groups'] + a['profiles']

    dialogs = [x['message']['user_id'] if 'chat_id' not in x['message'] else pe + x['message']['chat_id'] for x in a['items']]
    for i in a['items']:
        m = i['message']
        prof = [x for x in profs if x['id']==abs(m['user_id'])][0]
        title = m['title'] if 'chat_id' in m else get_title(prof)
        print('{i})\t{t}\n\t{body}'.format(t=title, i=a['items'].index(i)+1, **m).encode('cp866', errors='xmlcharrefreplace').decode('cp866', errors='xmlcharrefreplace'), end='\n-----------\n')

    arg = input('Укажите адресата: ').strip()

if arg.isdigit():
    peer = int(arg)
    if peer <= len(dialogs):
        peer = dialogs[peer-1]
    elif peer < 1000:
        peer += pe
elif 'c' in arg:
    peer = pe + int(arg[1:])

ap.messages.send(peer_id=peer, attachment=att)
