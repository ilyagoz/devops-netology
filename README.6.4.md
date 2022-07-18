# Домашнее задание к занятию "6.4. PostgreSQL"

> Используя docker поднимите инстанс PostgreSQL (версию 13). Данные БД
> сохраните в volume.

```
$ docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS
 NAMES
000e655d3c21   postgres-ru:13   "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   pg
```

> Подключитесь к БД PostgreSQL используя psql.

```
psql -h control.local -U ivg -d netology
Password for user ivg:
psql (13.7 (Ubuntu 13.7-0ubuntu0.21.10.1))
Type "help" for help.

netology=# \?
```

> Найдите и приведите управляющие команды для:
>
> вывода списка БД

`\l[+]   [PATTERN]      list databases`

> подключения к БД

```
 \c[onnect] {[DBNAME|- USER|- HOST|- PORT|-] | conninfo}
                         connect to new database (currently "netology")
```

> вывода списка таблиц

` \dt[S+] [PATTERN]      list tables`

> вывода описания содержимого таблиц

`\d[S+]  NAME           describe table, view, sequence, or index`

> выхода из psql

`\q`

> Используя psql создайте БД test_database.

``` sql
CREATE ROLE postgres LOGIN;
CREATE DATABASE test_database WITH OWNER=postgres;
```

> Восстановите бэкап БД в test_database

`vagrant@control:~$ psql -h control.local -U ivg test_database < test_dump.sql`

> Перейдите в управляющую консоль psql внутри контейнера.

```
docker run -it --rm --network pg-net postgres-ru:13 psql -h control.local -U ivg -d test_database

Пароль пользователя ivg:
psql (13.7 (Debian 13.7-1.pgdg110+1))
Введите "help", чтобы получить справку.

test_database=#
```

> Используя таблицу pg_stats, найдите столбец таблицы orders с
> наибольшим средним значением размера элементов в байтах.

```sql
WITH t AS (SELECT MAX(avg_width) AS m 
FROM pg_stats WHERE tablename ='orders') 
SELECT attname,avg_width FROM pg_stats 
INNER JOIN t ON pg_stats.avg_width=t.m WHERE tablename='orders';

 attname | avg_width
---------+-----------
 title   |        16
(1 строка)
```

> Архитектор и администратор БД выяснили, что ваша таблица orders
> разрослась до невиданных размеров и поиск по ней занимает долгое
> время. Вам, как успешному выпускнику курсов DevOps в нетологии
> предложили провести разбиение таблицы на 2 (шардировать на
> orders_1 - price>499 и orders_2 - price<=499).
>
> Предложите SQL-транзакцию для проведения данной операции.

> Можно ли было изначально исключить "ручное" разбиение при
> проектировании таблицы orders?

"Наивный" способ, при котором будут созданы две независимые таблицы,
но приложению, работающему с исходной таблицей `orders`, это не
поможет.

```sql
CREATE TABLE orders_1 (LIKE orders INCLUDING ALL);
CREATE TABLE orders_2 (LIKE orders INCLUDING ALL);
INSERT INTO orders_1 SELECT * FROM orders WHERE (price>499);
INSERT INTO orders_2 SELECT * FROM orders WHERE (price<=499);
```

Можно сделать новую секционированную таблицу `orders`. Однако при этом
сломается все, что работало с первичным ключом старой таблицы, так как
ключи уже не будут уникальны в рамках всей таблицы. Простого способа
сохранить работу со сторонними ключами в PostgreSQL, к сожалению, нет.

```sql
--- Индекс в секционированной таблице должен включать ключ разбиения,
--- поэтому скопировать его из исходной нельзя.
CREATE TABLE temp (LIKE orders INCLUDING ALL EXCLUDING INDEXES)
	PARTITION BY RANGE(price);
--- цена у нас integer, поэтому можно указать 500.
CREATE TABLE orders_1 PARTITION OF temp FOR VALUES
    FROM ('500') TO (MAXVALUE);
CREATE TABLE orders_2 PARTITION OF temp FOR VALUES
    FROM (MINVALUE) TO ('500');	
ALTER TABLE temp ADD CONSTRAINT pkey PRIMARY KEY (id, price);
INSERT INTO temp SELECT * FROM orders;

ALTER TABLE orders RENAME TO orders_backup;
ALTER TABLE temp RENAME TO orders;
```

```
test_database=# select * from orders_2;
 id |        title         | price
----+----------------------+-------
  1 | War and peace        |   100
  3 | Adventure psql time  |   300
  4 | Server gravity falls |   300
  5 | Log gossips          |   123
  7 | Me and my bash-pet   |   499
(5 строк)

test_database=# select * from orders_1;
 id |       title        | price
----+--------------------+-------
  2 | My little database |   500
  6 | WAL never lies     |   900
  8 | Dbiezdmin          |   501
(3 строки)
```

> Используя утилиту pg_dump создайте бекап БД test_database.

```
docker run -it --rm --network pg-net postgres-ru:13 \
	pg_dump --dbname=postgresql://ivg:XXXX@control.local:5432/test_database > test_database.dump.sql
```

> Как бы вы доработали бэкап-файл, чтобы добавить уникальность
> значения столбца title для таблиц test_database?

Добавить строку `ALTER TABLE orders ADD CONSTRAINT title_uniq UNIQUE(title);`.
Но с секционированной таблицей нужно будет `ALTER TABLE orders ADD CONSTRAINT title_uniq UNIQUE(title,price);`.
