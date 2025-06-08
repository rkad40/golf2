import subprocess
import fs
import ru
from rex import Rex
from menu.cli import select_one

VERSION = '1.0.0'

print(ru.create_banner('Golf Tournament Test Coverage').rstrip())
print()
print(f'Version {VERSION}')
print()

rex = Rex()

subprocess.run(['coverage', 'run', "--source='.'", 'manage.py', 'test'])

print()
if select_one('Generate report?', ['Yes', 'No'], 'Yes') == 'Yes':

    subprocess.run(['coverage', 'html', '--skip-empty', '--omit=report.py,manage.py,master/asgi.py,master/wsgi.py,apps/access/migrations/*.py,apps/main/migrations/*.py,apps/book/migrations/*.py,apps/maven/migrations/*.py'])

    if not fs.exists('report'):
        fs.mkdir('report')

    for file in fs.files('htmlcov'):
        if fs.ext(file) != 'html': continue
        old = fs.read(file, to_string=True)
        new = rex.s(old, r',\s*created\s+at\s+\d+-\d+-\d+\s+\d+:\d+\s+\S+', '', 'sg=')
        if old != new:
            fs.write(file, new)

    fs.copy_dir_if_changed('htmlcov', 'report', verbose=2)
    fs.rmdir('htmlcov')

print('Done.')

