import urllib.request
import json
import fs
from jinja2 import Environment
import yaml
import ru
from menu.cli import select_one

print(ru.create_banner('Create Handouts'))

teams = {}

urls = {
    'Local  (http://localhost)':   'http://127.0.0.1:8000/team/info/mkjb3f453e2jpxdjp8dy',
    'Remote (http://rockne.golf)': 'http://rockne.golf/team/info/mkjb3f453e2jpxdjp8dy',
}

url = urls[select_one('Select a site.', [key for key in urls], list(urls.keys())[1])]
print(f'Using {url} ...')

with urllib.request.urlopen(url) as response:
   teams = json.loads(response.read().decode())['teams']

print(r'''
 _____                      _   _                 _             _
|_   _|__  __ _ _ __ ___   | | | | __ _ _ __   __| | ___  _   _| |_ ___
  | |/ _ \/ _` | '_ ` _ \  | |_| |/ _` | '_ \ / _` |/ _ \| | | | __/ __|
  | |  __/ (_| | | | | | | |  _  | (_| | | | | (_| | (_) | |_| | |_\__ \
  |_|\___|\__,_|_| |_| |_| |_| |_|\__,_|_| |_|\__,_|\___/ \__,_|\__|___/

''')

if True:
    txt = fs.read('HandoutTemplate.html', to_string=True)
    env = Environment()
    template = env.from_string(txt)
    txt = template.render(teams=teams)
    print(fs.fwriteif('../Handout.html', txt))

print(r'''
 _          _          _      
| |    __ _| |__   ___| |___ 
| |   / _` | '_ \ / _ \ / __|   
| |__| (_| | |_) |  __/ \__ \  
|_____\__,_|_.__/ \___|_|___/ 

''')

for n in [5, 7]:
    n2 = n * 2
    labels = []
    teams2 = ru.clone(teams)
    while len(teams2) % n2 != 0:
        name = f'D{len(teams2):02d}'
        teams2[name] = {}
    i = 0
    for name in teams2:
        data = ru.clone(teams2[name])
        data['index'] = i
        data.update(dict(begin=False, end=False, left=False, right=False))
        if i % n2 == 0:
            data['begin'] = True
            if i != 0: data['end'] = True
        if i % 2 == 0: data['left'] = True
        else: data['right'] = True
        labels.append(data)
        i += 1

    txt = fs.read(f'BigLabelsTemplate2x{n}.html', to_string=True)
    env = Environment()
    template = env.from_string(txt)
    txt = template.render(teams=labels)
    print(fs.fwriteif(f'../BigLabels2x{n}.html', txt))

print("Hit Enter to exit.")
input()
