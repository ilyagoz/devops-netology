# Домашнее задание к занятию "6.2. SQL"

> Задача 1
>
> Используя docker поднимите инстанс PostgreSQL (версию 12) c 2 volume,
> в который будут складываться данные БД и бэкапы.
>
> Приведите получившуюся команду или docker-compose манифест.

`Dockerfile` для смены локали:

```
FROM postgres:12
RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG ru_RU.utf8
```

 ``` shell
 #!/bin/bash

POSTGRES_PASSWORD="XXXX"
POSTGRES_USER="ivg"
POSTGRES_DB="netology"

docker volume create pg-data
docker volume create pg-backup

docker run --rm \
       --name pg \
       -p 5432:5432 \
       -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
       -e POSTGRES_USER=$POSTGRES_USER \
       -e POSTGRES_DB=$POSTGRES_DB \
       -e PGDATA=/var/lib/postgresql/data/pgdata \
       -v pg-data:/var/lib/postgresql/data \
       -v pg-backup:/var/lib/postgresql/backup \
       -d \
       postgres-ru:12
 ```
```

$ /c/Program\ Files/PostgreSQL/14/bin/psql.exe -h control.local -U ivg -d netology
Password for user ivg:
psql (14.4, server 12.11 (Debian 12.11-1.pgdg110+1))
WARNING: Console code page (65001) differs from Windows code page (1251)
         8-bit characters might not work correctly. See psql reference
         page "Notes for Windows users" for details.
Type "help" for help.

netology=# select version();
                                                            version
-------------------------------------------------------------------------------------------------------------------------------
 PostgreSQL 12.11 (Debian 12.11-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
(1 row)

```

> Задача 2
>
> В БД из задачи 1:
>
> создайте пользователя test-admin-user и БД test_db

```
$ createuser.exe -h control.local -P test-admin-user 
```

``` sql
CREATE DATABASE "test-db" WITH ENCODING 'UTF8' LC_COLLATE='ru_RU.UTF-8' LC_CTYPE='ru_RU.utf8' TEMPLATE template0;
```


> в БД test_db создайте таблицу orders и clients (спeцификация таблиц
> ниже)

``` sql
CREATE TABLE orders (
	id SERIAL PRIMARY KEY, 
	title TEXT,
	price INTEGER);

CREATE TABLE clients (
	id SERIAL PRIMARY KEY, 
	name TEXT,
	country TEXT, 
	"order" INTEGER,
	FOREIGN KEY ("order") REFERENCES orders(id));
```

> - предоставьте привилегии на все операции пользователю test-admin-user на таблицы БД test_db
> - создайте пользователя test-simple-user
> - предоставьте пользователю test-simple-user права на SELECT/INSERT/UPDATE/DELETE данных таблиц БД test_db

С такими правами test-simple-user не сможет вставлять данные в таблицы. Ему нужны еще права на sequence.

``` sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA "public" TO "test-admin-user";
CREATE USER "test-simple-user" WITH PASSWORD 'simplepass';
GRANT SELECT, INSERT, UPDATE, DELETE ON orders, clients TO "test-simple-user";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to "test-simple-user";
```

> Приведите:
>
>     итоговый список БД после выполнения пунктов выше,

```
test-db-# \l
                                  List of databases
   Name    | Owner | Encoding |   Collate   |   Ctype    |     Access privileges
-----------+-------+----------+-------------+------------+---------------------------
 postgres  | ivg   | UTF8     | en_US.utf8  | en_US.utf8 |
 template0 | ivg   | UTF8     | en_US.utf8  | en_US.utf8 | =c/ivg                   +
           |       |          |             |            | ivg=CTc/ivg
 template1 | ivg   | UTF8     | en_US.utf8  | en_US.utf8 | =c/ivg                   +
           |       |          |             |            | ivg=CTc/ivg
 test-db   | ivg   | UTF8     | ru_RU.UTF-8 | ru_RU.utf8 | =Tc/ivg                  +
           |       |          |             |            | ivg=CTc/ivg              +
           |       |          |             |            | "test-admin-user"=CTc/ivg
(4 rows)
```

> описание таблиц (describe)

```
test-db-# \d orders
                            Table "public.orders"
 Column |  Type   | Collation | Nullable |              Default
--------+---------+-----------+----------+------------------------------------
 id     | integer |           | not null | nextval('orders_id_seq'::regclass)
 title  | text    |           |          |
 price  | integer |           |          |
Indexes:
    "orders_pkey" PRIMARY KEY, btree (id)
Referenced by:
    TABLE "clients" CONSTRAINT "clients_order_fkey" FOREIGN KEY ("order") REFERENCES orders(id)
	
test-db-# \d clients
                             Table "public.clients"
 Column  |  Type   | Collation | Nullable |               Default
---------+---------+-----------+----------+-------------------------------------
 id      | integer |           | not null | nextval('clients_id_seq'::regclass)
 name    | text    |           |          |
 country | text    |           |          |
 order   | integer |           |          |
Indexes:
    "clients_pkey" PRIMARY KEY, btree (id)
Foreign-key constraints:
    "clients_order_fkey" FOREIGN KEY ("order") REFERENCES orders(id)
```

> SQL-запрос для выдачи списка пользователей с правами над таблицами test_db

``` sql
SELECT DISTINCT ON (grantee) grantor,grantee FROM information_schema.table_privileges WHERE table_catalog = 'test-db';
```

> список пользователей с правами над таблицами test_db
```
 grantor |     grantee
---------+------------------
 ivg     | PUBLIC
 ivg     | ivg
 ivg     | test-admin-user
 ivg     | test-simple-user
(4 rows)
```

> Задача 3
>
> Используя SQL синтаксис - наполните таблицы следующими тестовыми данными:

``` sql
INSERT INTO clients (name, country) VALUES ('Иванов Иван Иванович', 'USA');
...
```

```
test-db=> select * from orders;
 id |  title  | price 
----+---------+-------
  1 | Гитара  |  4000
  2 | Монитор |  7000
  3 | Книга   |   500
  4 | Принтер |  3000
  5 | Шоколад |    10
(5 rows)
```

> Используя SQL синтаксис:
>
> вычислите количество записей для каждой таблицы

```
test-db=> select count(*) from orders;
 count 
-------
     5
(1 row)

test-db=> select count(*) from clients;
 count 
-------
     5
(1 row)
```

> Задача 4
>
> Часть пользователей из таблицы clients решили оформить заказы из таблицы orders.
>
> Используя foreign keys свяжите записи из таблиц, согласно таблице

```
test-db=> UPDATE clients SET "order" = (SELECT id FROM orders WHERE title = 'Книга') WHERE name = 'Иванов Иван Иванович';
UPDATE clients SET "order" = (SELECT id FROM orders WHERE title = 'Монитор') WHERE name = 'Петров Петр Петрович';
UPDATE clients SET "order" = (SELECT id FROM orders WHERE title = 'Гитара') WHERE name = 'Иоганн Себастьян Бах';
UPDATE 1
UPDATE 1
UPDATE 1
```

> Приведите SQL-запрос для выдачи всех пользователей, которые
> совершили заказ, а также вывод данного запроса.

```
test-db=> select * from clients where "order" is not NULL;
 id |         name         | country | order 
----+----------------------+---------+-------
 10 | Иванов Иван Иванович | USA     |     3
  9 | Петров Петр Петрович | Canada  |     2
  8 | Иоганн Себастьян Бах | Japan   |     1
(3 rows)
```

> Задача 5
>
> Получите полную информацию по выполнению запроса выдачи всех
> пользователей из задачи 4 (используя директиву EXPLAIN).
>
> Приведите получившийся результат и объясните что значат полученные значения.

```
test-db=> explain verbose select * from clients where "order" is not NULL;
QUERY PLAN                                              
-----------------------------------------------------------------------------------------------------
 Seq Scan on clients  (cost=0.00..18.10 rows=806 width=72) (actual time=0.013..0.015 rows=3 loops=1)
   Filter: ("order" IS NOT NULL)
   Rows Removed by Filter: 2
 Planning Time: 0.061 ms
 Execution Time: 0.031 ms
(5 rows)
```

Используется Seq Scan — последовательное чтение данных таблицы
clients, так как индекса там не создано. Планировщик предполагал, что
придется прочитать 806 строк. Фактически прочитано 3, отфильтровано 2,
за один проход (loops). Дальше указано время планирования и
фактического выполнения запроса.

> Задача 6
>
> Создайте бэкап БД test_db и поместите его в volume, предназначенный для бэкапов (см. Задачу 1).
>
> Остановите контейнер с PostgreSQL (но не удаляйте volumes).
>
> Поднимите новый пустой контейнер с PostgreSQL.
>
> Восстановите БД test_db в новом контейнере.
>
> Приведите список операций, который вы применяли для бэкапа данных и восстановления.

```
$ docker inspect pg-backup
[
    {
        "CreatedAt": "2022-07-01T13:43:57Z",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/pg-backup/_data",
        "Name": "pg-backup",
        "Options": {},
        "Scope": "local"
    }
]

$ pg_dumpall -h control.local -U ivg | sudo tee /var/lib/docker/volumes/pg-backup/_data/backup.001
$ docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED       STATUS       PORTS                                       NAMES
709dfca11670   postgres-ru:12   "docker-entrypoint.s…"   4 hours ago   Up 4 hours   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   pg
$ docker stop pg
pg
```

Чтобы новая база была пустой, ей нужны другие volume. run-docker-pg.sh соответственно изменен.

```
$ docker volume create pg-data2
pg-data2
$ docker volume create pg-backup2
pg-backup2
$ ./run-docker-pg.sh
1438ac4058d3fbe7e1c0080b06eb4998f4fe59b71285582ab8a9167e931d70ed
$ sudo psql -h control.local -U ivg -d postgres -f /var/lib/docker/volumes/pg-backup/_data/backup.001

$ psql -h control.local -U test-simple-user -d test-db
Password for user test-simple-user: 
psql (13.7 (Ubuntu 13.7-0ubuntu0.21.10.1), server 12.11 (Debian 12.11-1.pgdg110+1))
Type "help" for help.

test-db=> select * from clients where "order" is not NULL;
 id |         name         | country | order 
----+----------------------+---------+-------
 10 | Иванов Иван Иванович | USA     |     3
  9 | Петров Петр Петрович | Canada  |     2
  8 | Иоганн Себастьян Бах | Japan   |     1
(3 rows)

test-db=> exit
```
