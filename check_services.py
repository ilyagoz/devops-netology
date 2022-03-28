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
