# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 12:12:17 2022

@author: ivg
"""
import os, sys, getopt

REPO_DIR = os.path.expanduser("~/Documents/Devops/devops-netology")

try:
    opts, args = getopt.getopt(sys.argv[1:], "")
except getopt.GetoptError as err:
    print(err)
    sys.exit(2)

if len(args) > 0:
    REPO_DIR = args[0]
else:
    print("Репозиторий не указан, используем репозиторий по умолчанию.")

bash_command = ["cd " + REPO_DIR, "git status"]

if os.access(REPO_DIR, os.R_OK):
    print("Локальный репозиторий: " + REPO_DIR)
else:
    print ("Локальный репозиторий " + REPO_DIR + " недоступен.")
    sys.exit(-1)

pipe = os.popen(' && '.join(bash_command))
result_os = pipe.read()
retcode = pipe.close()
if retcode != None:
    print('Git не смог проверить локальный репозиторий ' + REPO_DIR + '\nУбедитесь, что каталог задан правильно.')
    sys.exit(-1)

is_change = False
for result in result_os.splitlines():
    if result.find('modified:') != -1:
        prepare_result = result.replace('\tmodified:   ', '')
        print(prepare_result)

