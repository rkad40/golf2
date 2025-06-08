"""
# Description

Create Nexus project skeleton.
"""
import fs, ru, sys, subprocess
from menu.simple import select_one

banner = r"""
  ____                _         ____            _           _
 / ___|_ __ ___  __ _| |_ ___  |  _ \ _ __ ___ (_) ___  ___| |_
| |   | '__/ _ \/ _` | __/ _ \ | |_) | '__/ _ \| |/ _ \/ __| __|
| |___| | |  __/ (_| | ||  __/ |  __/| | | (_) | |  __/ (__| |_
 \____|_|  \___|\__,_|\__\___| |_|   |_|  \___// |\___|\___|\__|
                                             |__/
 ____  _        _      _
/ ___|| | _____| | ___| |_ ___  _ __
\___ \| |/ / _ \ |/ _ \ __/ _ \| '_ \
 ___) |   <  __/ |  __/ || (_) | | | |
|____/|_|\_\___|_|\___|\__\___/|_| |_|
"""

print(banner)

try:
    bin_dir = fs.get_abs_path('.')
    top_dir = fs.get_abs_path('..')

    venv_dir = fs.get_abs_path('../venv')
    print(fs.create_dir(venv_dir))

    proj_dir = fs.get_abs_path('..')
    print(fs.create_dir(proj_dir))

    file = fs.join_names(top_dir,'start_venv.bat')
    content = """@ECHO OFF
    CD "{}"
    PowerShell.exe -Command "& {{Start-Process PowerShell.exe -ArgumentList '-ExecutionPolicy Bypass -noexit -File ""{}\\start_venv.ps1""' -Verb RunAs}}"
    """.format(bin_dir, bin_dir)
    print(fs.write_file_if_changed(file, content))

    file = fs.join_names(bin_dir,'start_venv.ps1')
    content = """Set-Location -Path "{}"
    $command = '"{}\\Scripts\\activate.ps1"'
    iex "& $command"
    """.format(proj_dir, venv_dir)
    print(fs.write_file_if_changed(file, content))

    fs.change_dir(venv_dir)
    answer = select_one("Create virtual environnement?", ['Yes', 'No'], 'Yes')
    if answer == 'Yes':
        exe = fs.join_names(fs.get_dir_name(sys.executable), 'Scripts', 'virtualenv')
        subprocess.call([exe, "."])
except Exception as err:
    print(err)
    
print('Hit <Enter> to exit.')
input()

