# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 21:56:32 2022

@author: ivg
"""
import json, sys, argparse, os
try:
    from ruamel_yaml import YAML
    yaml=YAML(typ='safe')
except ModuleNotFoundError:
    print("Please install module ruamel.yaml: pip install ruamel.yaml, or equivalent for your system.")
    sys.exit(2)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="имя файла для преобразования.")
args = parser.parse_args()

try:
    fp = open(args.filename, 'r')    
except OSError as e:
    print("Ошибка открытия файла", args.filename, ":\n", e)
    sys.exit(-1)

data = None
(root, ext) = os.path.splitext(args.filename)

# Поскольку любой файл JSON является также и файлом YAML (c версии 1.2),
# нам нужно сначала проверить файл на соответствие JSON.

valid_json = True
try:
    data = json.load(fp)    
except ValueError as e:
    valid_json = False
    if ext == ".json":
        print("Ошибка при попытке прочитать файл", args.filename, "как JSON:\n", e)

fp.seek(0)

valid_yaml = True
if not valid_json:
    try:
        data = yaml.load(fp)    
    except:
        valid_yaml = False
        if ext in [".yaml", ".yml"]:
            print("Ошибка при попытке прочитать файл", args.filename, "как YAML.")
    
    if data is None:
        valid_yaml = False

fp.close()

if not (valid_json or valid_yaml):
    print("Файл", args.filename, "не является ни корректным файлом YAML, ни JSON")
    sys.exit(0)

if (valid_json and valid_yaml):
    if ext in [".yaml", ".yml"]:
        valid_json = False
    elif ext == ".json":
        valid_yaml = False
    else:
        print("Файл", args.filename, "является корректным файлом JSON и YAML, считаем его JSON.")
        valid_yaml = False

if (valid_json and (not valid_yaml)):
    new_filename = root + ".yml"
    print("Файл", args.filename, "распознан как JSON, преобразуется в YAML", new_filename)
    # сконвертировать в YAML и выйти.

    if os.path.exists(new_filename):
        os.replace(new_filename, new_filename + '~')

    try:
        fp = open(new_filename, 'w')
    except OSError as e:
        print("Ошибка при попытке записи в файл", new_filename, "\n", e)
        sys.exit(-1)
    yaml.dump(data, fp)
    fp.close()
    sys.exit(0)
    
if valid_yaml:
    new_filename = root + ".json"
    print("Файл", args.filename, "распознан как YAML, преобразуется в JSON", new_filename)
    # сконвертировать в JSON и выйти.
    if os.path.exists(new_filename):
        os.replace(new_filename, new_filename + '~')
 
    try:
        fp = open(new_filename, 'w')
    except OSError as e:
        print("Ошибка при попытке записи в файл", new_filename, "\n", e)
        sys.exit(-1)
    json.dump(data, fp, indent=1)
    fp.close()
    sys.exit(0)

