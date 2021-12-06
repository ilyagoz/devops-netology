Строчка добавлена для задания №3 к занятию 2.2.

# Занятие 2.1 Системы контроля версий
## Задание №1 - Создать и настроить репозиторий для дальнейшей работы на курсе

Благодаря добавленному `.gitignore` будут игнорироваться файлы:
- `**/.terraform/*` - в этом и всех подкаталогах будут игнорироваться
каталоги с именем .terraform со всем содержимым.
- `*.tfstate` - файлы состояния Terraform (c расширением tfstate),
а также каталоги с названием *.tfstate, если кто-то их вдруг создаст.
- `*.tfstate.*` - ...и файлы состояния Terraform c другими расширениями
(бекапы, в частности). 
- `crash.log` - файлы (и каталоги) с именем crash.log
- `*.tfvars` - файлы (и каталоги) с расширением tfvars 
- `override.tf` - файлы (и каталоги) с именем override.tf
- `override.tf.json` - файлы (и каталоги) с именем override.tf.json
- `*_override.tf` - файлы (и каталоги) с именем, заканчивающимся на _override.tf  
- `*_override.tf.json` - файлы (и каталоги) с именем, заканчивающимся на *_override.tf.json
- `.terraformrc` - файлы (и каталоги) с именем .terraformrc 
- `terraform.rc` - файлы (и каталоги) с именем .terraform.rc
