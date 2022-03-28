# Домашнее задание к занятию "4.2. Использование Python для решения типовых DevOps задач"

## Обязательная задача 1

Есть скрипт:
```python
#!/usr/bin/env python3
a = 1
b = '2'
c = a + b
```

### Вопросы:
| Вопрос  | Ответ |
| ------------- | ------------- |
| Какое значение будет присвоено переменной `c`?  | Никакого. `a` и `b` - переменные разных типов.  |
| Как получить для переменной `c` значение 12?  | `c=12`, если вы хотите целочисленное значение :) Ладно, `c=str(a)+b` или `c=int(str(a)+b)`   |
| Как получить для переменной `c` значение 3?  | `c = a + int(b)`  |

## Обязательная задача 2
Мы устроились на работу в компанию, где раньше уже был DevOps Engineer. Он написал скрипт, позволяющий узнать, какие файлы модифицированы в репозитории, относительно локальных изменений. Этим скриптом недовольно начальство, потому что в его выводе есть не все изменённые файлы, а также непонятен полный путь к директории, где они находятся. Как можно доработать скрипт ниже, чтобы он исполнял требования вашего руководителя?

```python
#!/usr/bin/env python3

import os

bash_command = ["cd ~/netology/sysadm-homeworks", "git status"]
result_os = os.popen(' && '.join(bash_command)).read()
is_change = False
for result in result_os.split('\n'):
    if result.find('modified') != -1:
        prepare_result = result.replace('\tmodified:   ', '')
        print(prepare_result)
        break
```

### Ваш скрипт:
```python
import os, sys

REPO_DIR = os.path.expanduser("~/Documents/Devops/devops-netology")

bash_command = ["cd " + REPO_DIR, "git status"]

if os.access(REPO_DIR, os.R_OK):
    print("Локальный репозиторий: " + REPO_DIR)
else:
    print ("Локальный репозиторий " + REPO_DIR + " недоступен.")
    sys.exit(-1)
    
result_os = os.popen(' && '.join(bash_command)).read()

is_change = False
for result in result_os.splitlines():
    if result.find('modified:') != -1:
        prepare_result = result.replace('\tmodified:   ', '')
        print(prepare_result)

```

### Вывод скрипта при запуске при тестировании:
```
Локальный репозиторий: C:\Users\ivg/Documents/Devops/devops-netology
README.4.2.md
```

## Обязательная задача 3
1. Доработать скрипт выше так, чтобы он мог проверять не только локальный репозиторий в текущей директории, а также умел воспринимать путь к репозиторию, который мы передаём как входной параметр. Мы точно знаем, что начальство коварное и будет проверять работу этого скрипта в директориях, которые не являются локальными репозиториями.

### Ваш скрипт:
```python
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
```

### Вывод скрипта при запуске при тестировании:
```
$ python check_modified.py sdfsf
Локальный репозиторий sdfsf недоступен.

$ python check_modified.py ~/Documents/Devops/test/
Локальный репозиторий: C:/Users/ivg/Documents/Devops/test/
test1.txt
test2.txt

$ python check_modified.py ~/Documents/Devops/
Локальный репозиторий: C:/Users/ivg/Documents/Devops/
fatal: not a git repository (or any of the parent directories): .git
Git не смог проверить локальный репозиторий C:/Users/ivg/Documents/Devops/
Убедитесь, что каталог задан правильно.
```

## Обязательная задача 4
1. Наша команда разрабатывает несколько веб-сервисов, доступных по http. Мы точно знаем, что на их стенде нет никакой балансировки, кластеризации, за DNS прячется конкретный IP сервера, где установлен сервис. Проблема в том, что отдел, занимающийся нашей инфраструктурой очень часто меняет нам сервера, поэтому IP меняются примерно раз в неделю, при этом сервисы сохраняют за собой DNS имена. Это бы совсем никого не беспокоило, если бы несколько раз сервера не уезжали в такой сегмент сети нашей компании, который недоступен для разработчиков. Мы хотим написать скрипт, который опрашивает веб-сервисы, получает их IP, выводит информацию в стандартный вывод в виде: <URL сервиса> - <его IP>. Также, должна быть реализована возможность проверки текущего IP сервиса c его IP из предыдущей проверки. Если проверка будет провалена - оповестить об этом в стандартный вывод сообщением: [ERROR] <URL сервиса> IP mismatch: <старый IP> <Новый IP>. Будем считать, что наша разработка реализовала сервисы: `drive.google.com`, `mail.google.com`, `google.com`.

### Ваш скрипт:
```python
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 16:10:04 2022

@author: ivg
"""

SERVER_NAMES = ["drive.google.com", "mail.google.com", "google.com"]
ADDRESSES_FILE = "addr.json"

import os, json, ipaddress, socket, sys

old_addr = {}

if os.path.exists(ADDRESSES_FILE):
    try:
        fp = open(ADDRESSES_FILE, 'r')    
        old_addr = json.load(fp)
    except OSError as e:
        print("Ошибка открытия файла", ADDRESSES_FILE, ":\n", e)
    except ValueError as e:
        print("Ошибка в файле " + ADDRESSES_FILE + ":\n", e, "\nСравнить новые адреса со старыми не получится.")
    finally:
        fp.close()
    
else:
    pass

new_addr = {}

for s in SERVER_NAMES:
    try:
        addr = socket.gethostbyname(s)
    except OSError as e:
        print("Не удается получить адрес для сервера", s, ":", e)
        continue
    new_addr[s] = str(addr)

if len(new_addr) > 0:
    for name, addr in new_addr.items():
        print(name, '-', addr)
        if name in old_addr:
            if ipaddress.ip_address(old_addr[name]) != ipaddress.ip_address(addr):
                print("[ERROR]", name, "IP mismatch:", old_addr[name], addr)
else:
    print("Ни для одного из серверов не удалось получить адрес.")
    sys.exit(-1)

try:
    fp = open(ADDRESSES_FILE, 'w')    
    json.dump(new_addr, fp)
except OSError as e:
    print("Ошибка открытия файла", ADDRESSES_FILE, ":\n", e)
finally:
    fp.close()

```

### Вывод скрипта при запуске при тестировании:
```
$ python check_services.py
drive.google.com - 142.250.74.110
mail.google.com - 64.233.165.19
google.com - 64.233.164.101

$ python check_services.py
drive.google.com - 142.250.74.110
mail.google.com - 142.250.74.69
[ERROR] mail.google.com IP mismatch: 64.233.165.19 142.250.74.69
google.com - 64.233.164.101
```

## Дополнительное задание (со звездочкой*) - необязательно к выполнению

Так получилось, что мы очень часто вносим правки в конфигурацию своей системы прямо на сервере. Но так как вся наша команда разработки держит файлы конфигурации в github и пользуется gitflow, то нам приходится каждый раз переносить архив с нашими изменениями с сервера на наш локальный компьютер, формировать новую ветку, коммитить в неё изменения, создавать pull request (PR) и только после выполнения Merge мы наконец можем официально подтвердить, что новая конфигурация применена. Мы хотим максимально автоматизировать всю цепочку действий. Для этого нам нужно написать скрипт, который будет в директории с локальным репозиторием обращаться по API к github, создавать PR для вливания текущей выбранной ветки в master с сообщением, которое мы вписываем в первый параметр при обращении к py-файлу (сообщение не может быть пустым). При желании, можно добавить к указанному функционалу создание новой ветки, commit и push в неё изменений конфигурации. С директорией локального репозитория можно делать всё, что угодно. Также, принимаем во внимание, что Merge Conflict у нас отсутствуют и их точно не будет при push, как в свою ветку, так и при слиянии в master. Важно получить конечный результат с созданным PR, в котором применяются наши изменения. 

### Ваш скрипт:
```python
???
```

### Вывод скрипта при запуске при тестировании:
```
???
```
