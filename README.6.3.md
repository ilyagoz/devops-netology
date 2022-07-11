# Домашнее задание к занятию "6.3. MySQL"

> Используя docker поднимите инстанс MySQL (версию 8). Данные БД
> сохраните в volume.

``` shell
#!/bin/bash

MYSQL_ROOT_PASSWORD="XXXX"

docker volume create msql-data

docker run --rm \
       --name mysql \
       -p 3306:3306 \
       -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
       -v msql-data:/var/lib/mysql \
       -d \
       mysql:8
```
```
$ docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED       STATUS       PORTS                                                  NAMES
de202a7cea48   mysql:8   "docker-entrypoint.s…"   2 hours ago   Up 2 hours   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysql	   
```

> Изучите бэкап БД и восстановитесь из него.

```
mysql> CREATE DATABASE IF NOT EXISTS netology;
Query OK, 1 row affected (0.02 sec)

mysql> USE netology;
Database changed
mysql> source test_dump.sql
...
Query OK, 5 rows affected (0.00 sec)
Records: 5  Duplicates: 0  Warnings: 0
...
```

> Перейдите в управляющую консоль mysql внутри контейнера.

```
$ docker exec -it mysql mysql -u root -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 12
Server version: 8.0.29 MySQL Community Server - GPL

Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
```

> Найдите команду для выдачи статуса БД и приведите в ответе из ее
> вывода версию сервера БД.

```
mysql> \s
--------------
mysql  Ver 8.0.29 for Linux on x86_64 (MySQL Community Server - GPL)
```

> Подключитесь к восстановленной БД и получите список таблиц из этой
> БД.

``` sql
mysql> USE netology;
Database changed
mysql> SHOW TABLES;
+--------------------+
| Tables_in_netology |
+--------------------+
| orders             |
+--------------------+
1 row in set (0.01 sec)
```

> Приведите в ответе количество записей с price > 300.

``` sql
mysql> SELECT COUNT(*) FROM orders WHERE (price >300);
+----------+
| count(*) |
+----------+
|        1 |
+----------+
1 row in set (0.00 sec)
```

> Создайте пользователя test в БД c паролем test-pass, используя:
>
>     плагин авторизации mysql_native_password
>     срок истечения пароля - 180 дней
>     количество попыток авторизации - 3
>     максимальное количество запросов в час - 100
>     аттрибуты пользователя:
>         Фамилия "Pretty"
>         Имя "James"

```sql
CREATE USER 
'test'@'localhost' IDENTIFIED WITH mysql_native_password BY 'test_pass' 
WITH MAX_QUERIES_PER_HOUR 100
PASSWORD EXPIRE INTERVAL 180 DAY 
FAILED_LOGIN_ATTEMPTS 3
PASSWORD_LOCK_TIME 1
ATTRIBUTE '{"fname": "James", "lname": "Pretty"}';
```

> Предоставьте привелегии пользователю test на операции SELECT базы test_db.

```sql
GRANT SELECT ON test_db.* TO 'test'@'localhost';
```

> Используя таблицу INFORMATION_SCHEMA.USER_ATTRIBUTES получите данные
> по пользователю test и приведите в ответе к задаче.

```
mysql> SELECT * FROM INFORMATION_SCHEMA.USER_ATTRIBUTES WHERE user='test';
+------+-----------+---------------------------------------+
| USER | HOST      | ATTRIBUTE                             |
+------+-----------+---------------------------------------+
| test | localhost | {"fname": "James", "lname": "Pretty"} |
+------+-----------+---------------------------------------+
1 row in set (0.00 sec)
```

> Установите профилирование SET profiling = 1. Изучите вывод
> профилирования команд SHOW PROFILES; 
>
> Исследуйте, какой engine используется в таблице БД test_db и
> приведите в ответе.

(в задании до сих пор не говорилось, что нужно создать БД test_db, так
что она называется netology :)

```
mysql> select engine from information_schema.tables where table_schema='netology';
+--------+
| ENGINE |
+--------+
| InnoDB |
+--------+
1 row in set (0.01 sec)
```

> Измените engine и приведите время выполнения и запрос на изменения
> из профайлера в ответе:

> на MyISAM

```
mysql> show profiles;
+----------+------------+--------------------------------------------------+
| Query_ID | Duration   | Query                                            |
+----------+------------+--------------------------------------------------+
...
|       26 | 0.12281475 | ALTER TABLE orders ENGINE = MyISAM               |
|       27 | 0.00043400 | select * from orders                             |
|       28 | 0.00035125 | show profiles limit 3                            |
+----------+------------+--------------------------------------------------+
15 rows in set, 1 warning (0.00 sec)
```

> на InnoDB

```
mysql> show profiles;
+----------+------------+-------------------------------------------------+
| Query_ID | Duration   | Query                                           |
+----------+------------+-------------------------------------------------+
...
|       29 | 0.05130750 | ALTER TABLE orders ENGINE = InnoDB              |
|       30 | 0.00070750 | select * from orders                            |
+----------+------------+-------------------------------------------------+
15 rows in set, 1 warning (0.00 sec)
```

> Изучите файл my.cnf в директории /etc/mysql.

Его там нет. Он в /etc.

> Измените его согласно ТЗ (движок InnoDB):
>
>     Скорость IO важнее сохранности данных
>     Нужна компрессия таблиц для экономии места на диске
>     Размер буффера с незакомиченными транзакциями 1 Мб
>     Буффер кеширования 30% от ОЗУ
>     Размер файла логов операций 100 Мб
>
> Приведите в ответе измененный файл my.cnf

Лучше не трогать `/etc/my.cnf`, а подставить файл с особыми настройками
в `/etc/mysql/conf.d/` при запуске контейнера через `-v`

``` ini
[mysqld]

# Скорость IO важнее сохранности данных
innodb_flush_method = O_DSYNC
innodb_flush_log_at_trx_commit = 2
# У нас также есть компрессия, и это даст небольшой выигрыш.
innodb_log_compressed_pages = OFF

# Нужна компрессия таблиц для экономии места на диске
innodb_compression_level = 8

# Размер буффера с незакомиченными транзакциями 1 Мб
innodb_log_buffer_size = 1MB

# Буффер кеширования 30% от ОЗУ
# ОЗУ на этой виртуальной машине 2 Гб.
innodb_buffer_pool_size = 600MB

# Размер файла логов операций 100 Мб
innodb_log_file_size = 100MB
```
