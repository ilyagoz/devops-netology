### Как сдавать задания

Вы уже изучили блок «Системы управления версиями», и начиная с этого занятия все ваши работы будут приниматься ссылками на .md-файлы, размещённые в вашем публичном репозитории.

Скопируйте в свой .md-файл содержимое этого файла; исходники можно посмотреть [здесь](https://raw.githubusercontent.com/netology-code/sysadm-homeworks/devsys10/04-script-03-yaml/README.md). Заполните недостающие части документа решением задач (заменяйте `???`, ОСТАЛЬНОЕ В ШАБЛОНЕ НЕ ТРОГАЙТЕ чтобы не сломать форматирование текста, подсветку синтаксиса и прочее, иначе можно отправиться на доработку) и отправляйте на проверку. Вместо логов можно вставить скриншоты по желани.

# Домашнее задание к занятию "4.3. Языки разметки JSON и YAML"


## Обязательная задача 1
Мы выгрузили JSON, который получили через API запрос к нашему сервису:
```
    { "info" : "Sample JSON output from our service\t",
        "elements" :[
            { "name" : "first",
            "type" : "server",
            "ip" : 7175 
            }
            { "name" : "second",
            "type" : "proxy",
            "ip : 71.78.22.43
            }
        ]
    }
```

Нужно найти и исправить все ошибки, которые допускает наш сервис

```json
{
    "info" : "Sample JSON output from our service\t",
    "elements" : [
	{ "name" : "first",
          "type" : "server",
          "ip" : 7175 
	},
	{ "name" : "second",
          "type" : "proxy",
          "ip" : "71.78.22.43"
	}
    ]
}
```
Несколько подозрительно также выглядит ip-адрес 7175, но тут уж с точки зрения синтаксиса все верно. 

## Обязательная задача 2
В прошлый рабочий день мы создавали скрипт, позволяющий опрашивать веб-сервисы и получать их IP. К уже реализованному функционалу нам нужно добавить возможность записи JSON и YAML файлов, описывающих наши сервисы. Формат записи JSON по одному сервису: `{ "имя сервиса" : "его IP"}`. Формат записи YAML по одному сервису: `- имя сервиса: его IP`. Если в момент исполнения скрипта меняется IP у сервиса - он должен так же поменяться в yml и json файле.

### Ваш скрипт:
```python
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
```

### Вывод скрипта при запуске при тестировании:
```
$ python check_services.py
drive.google.com - 173.194.222.194
mail.google.com - 142.250.74.37
google.com - 142.250.74.110
```

### json-файл(ы), который(е) записал ваш скрипт:
```json
$ cat addr.json
{
 "drive.google.com": "173.194.222.194",
 "mail.google.com": "142.250.74.37",
 "google.com": "142.250.74.110"
}
```

### yml-файл(ы), который(е) записал ваш скрипт:
```yaml
$ cat addr.yaml
- drive.google.com: 173.194.222.194
- mail.google.com: 142.250.74.37
- google.com: 142.250.74.110
```

## Дополнительное задание (со звездочкой*) - необязательно к выполнению

Так как команды в нашей компании никак не могут прийти к единому мнению о том, какой формат разметки данных использовать: JSON или YAML, нам нужно реализовать парсер из одного формата в другой. Он должен уметь:

- Принимать на вход имя файла

- Проверять формат исходного файла. Если файл не json или yml - скрипт должен остановить свою работу

- Распознавать какой формат данных в файле. Считается, что файлы *.json и *.yml могут быть перепутаны

- Перекодировать данные из исходного формата во второй доступный (из JSON в YAML, из YAML в JSON)

- При обнаружении ошибки в исходном файле - указать в стандартном выводе строку с ошибкой синтаксиса и её номер

- Полученный файл должен иметь имя исходного файла, разница в наименовании обеспечивается разницей расширения файлов
   
Преобразование 1:1 из JSON в YAML и обратно - задача нетрививальная,
так как в YAML есть особенности, которые в JSON не
поддерживаются. Например, комментарии или якоря, или наследование. При
преобразовании они неминуемо будут потеряны, если не сохранять их
где-то отдельно. Поэтому в рамках этого задания скрипт имеет ряд
ограничений. Комментарии в YAML при преобразовании в JSON не
сохраняются, порядок записей тоже, якоря, ссылки и все прочее будет
развернуто и при обратном преобразовании, естественно, автоматически
не вернутся.

Скрипт принимает один параметр - имя файла для преобразования. Тип
определяется по содержанию, расширение имеет значение, только если
файл одновременно является корректным JSON и YAML. Выходной файл
записывается с расширением `.json` или `.yml`. Если такой файл уже
есть, он копируется в резервную копию (с добавлением `~`).
Используется модуль ruamel_yaml, не входящий в комплект Python.

### Ваш скрипт:
```python
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

```

### Пример работы скрипта:
```
$ python json2yaml_yaml2json.py test.yml
Файл test.yml распознан как YAML, преобразуется в JSON test.json

$ python json2yaml_yaml2json.py test_not_a_json.json
Ошибка при попытке прочитать файл test_not_a_json.json как JSON:
 Expecting value: line 1 column 1 (char 0)
Файл test_not_a_json.json распознан как YAML, преобразуется в JSON test_not_a_json.json

$ python json2yaml_yaml2json.py err.json
Ошибка при попытке прочитать файл err.json как JSON:
 Extra data: line 1 column 39 (char 38)
Файл err.json не является ни корректным файлом YAML, ни JSON

```
