# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 16:10:04 2022

@author: ivg
"""

SERVER_NAMES = ["drive.google.com", "mail.google.com", "google.com"]
ADDRESSES_FILE_JSON = "addr.json"
ADDRESSES_FILE_YAML = "addr.yaml"

import json, ipaddress, socket, sys, yaml

old_addr = {}

try:
    fp = open(ADDRESSES_FILE_JSON, 'r')    
    old_addr = json.load(fp)
except OSError as e:
    print("Ошибка открытия файла", ADDRESSES_FILE_JSON, ":\n", e)
except ValueError as e:
    print("Ошибка в файле " + ADDRESSES_FILE_JSON + ":\n", e, "\nСравнить новые адреса со старыми не получится.")
    fp.close()


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

# В задании указан формат `- имя сервиса: его IP`. Это немного нелогичный формат,
# так как означает список словарей, по одному словарю на сервис, вместо одного
# словаря на все сервисы. Поэтому придется сделать так. Но можно, конечно, вручную
# писать в файл.
addr_for_yaml = []
for name, addr in new_addr.items():
    d = {}
    d[name]=addr
    addr_for_yaml.append(d)

fp_json = None
try:
    fp_json = open(ADDRESSES_FILE_JSON, 'w')    
except OSError as e:
    print("Ошибка открытия файла", ADDRESSES_FILE_JSON, ":\n", e)

json.dump(new_addr, fp_json, indent=1)

if fp_json is not None:
    fp_json.close()

fp_yaml = None
try:
    fp_yaml = open(ADDRESSES_FILE_YAML, 'w')    
except OSError as e:
    print("Ошибка открытия файла", ADDRESSES_FILE_JSON, ":\n", e)

yaml.dump(addr_for_yaml, fp_yaml)

if fp_yaml is not None:
    fp_yaml.close()

