# Домашнее задание к занятию "5.3. Введение. Экосистема. Архитектура. Жизненный цикл Docker контейнера"

> Задача 1

```
$ docker pull nginx:1.21

$ cat Dockerfile
FROM nginx
COPY index.html /usr/share/nginx/html

$ docker build -t netology-nginx ./
Sending build context to Docker daemon  3.072kB
Step 1/2 : FROM nginx
 ---> de2543b9436b
Step 2/2 : COPY index.html /usr/share/nginx/html
 ---> Using cache
 ---> cf826d7dfda4
Successfully built cf826d7dfda4
Successfully tagged netology-nginx:latest

$ docker run -d -p 80:80 netology-nginx
610b0ce9f6c716e7fff6321695ca35e5fa5c16cbbb602dbff416bcf596008e99

$ curl localhost

<html>
<head>
Hey, Netology
</head>
<body>
<h1>I’m DevOps Engineer!</h1>
</body>
</html>
```


> Опубликуйте созданный форк в своем репозитории и предоставьте ответ
> в виде ссылки

<https://hub.docker.com/r/ilyagoz/netology/tags>

> Задача 2
>
> Посмотрите на сценарий ниже и ответьте на вопрос: "Подходит ли в
> этом сценарии использование Docker контейнеров или лучше подойдет
> виртуальная машина, физическая машина? Может быть возможны разные
> варианты?"
>
> Детально опишите и обоснуйте свой выбор.

> Высоконагруженное монолитное java веб-приложение;

Контейнеризация приложений на Java вполне возможна. Настройка работы
JVM в контейнере имеет ряд нетривиальных моментов
[[1](https://habr.com/ru/company/hh/blog/450954/),
[2](https://developers.redhat.com/blog/2017/03/14/java-inside-docker),
[3](https://www.tutorialworks.com/docker-java-best-practices/)], но
удобство разработки может это компенсировать. Расходы на
контейнеризацию малы по сравнению с расходами на виртуальную машину.

> Nodejs веб-приложение;

Возможно и достаточно широко используется.

> Мобильное приложение c версиями для Android и iOS;

Теоретическая возможность запуска приложения для Android в контейнере
существует [[4](https://github.com/CGCL-codes/Android-Container),
[5](https://gist.github.com/FreddieOliveira/efe850df7ff3951cb62d74bd770dce27)],
но не на iOS. В любом случае, преимущества Docker в таком сценарии неясны.

> Шина данных на базе Apache Kafka;

Опять же, возможно и широко используется для организации кластеров Kafka.

> Elasticsearch кластер для реализации логирования продуктивного
> веб-приложения - три ноды elasticsearch, два logstash и две ноды
> kibana;

Да, широко используется и поддерживается [Elastic.co](https://www.elastic.co/guide/en/elastic-stack-get-started/current/get-started-stack-docker.html)

> Мониторинг-стек на базе Prometheus и Grafana;

Серверы Prometheus и Grafana хорошо работают в контейнерах
[[6](https://grafana.com/blog/2019/05/07/ask-us-anything-should-i-run-prometheus-in-a-container/)],
но экспортеры - только с ограничениями
[[7](https://github.com/prometheus/node_exporter)].

> MongoDB, как основное хранилище данных для java-приложения;

С точки зрения java-приложения, работа с контейнеризованной MongoDB
ничем не отличается от работы с обычной MongoDB. Сама MongoDB
совместима с контейнерами Docker
[[8](https://www.mongodb.com/compatibility/docker)]. 

> Gitlab сервер для реализации CI/CD процессов и приватный (закрытый)
> Docker Registry.

Да, конечно, подходит. Gitlab сервер работает с Docker
[[9](https://docs.gitlab.com/ee/install/docker.html)] и позволяет
получить обычные преимущества простоты развертывания и управления.

> Задача 3
>
> Запустите первый контейнер из образа centos c любым тэгом в фоновом
> режиме, подключив папку /data из текущей рабочей директории на
> хостовой машине в /data контейнера;

```
$ docker run -it -d -v ~/data:/data debian
ceeb091ccf74f2c2e3e491d0cd0965b310f43a2c97fffb707f0b3e67ab0a804b

$ docker run -it -d -v ~/data:/data centos
f30ef09392f43594d3270c3a23124e95ab20744cf0109955d48363aba2933a70

$ docker exec f3 bash -c "echo Hello docker > /data/hello.txt"

$ echo Hello debian > data/hello_debian.txt

$ docker exec ce bash -c "ls  /data"
hello.txt
hello_debian.txt

$ docker exec ce bash -c "cat /data/*"
Hello docker
Hello debian
```
