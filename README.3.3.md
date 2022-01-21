# Домашнее задание к занятию "3.3. Операционные системы, лекция 1"

> Какой системный вызов делает команда cd?

```
$ strace /bin/bash -c 'cd /tmp' 2>&1 | grep tmp
execve("/bin/bash", ["/bin/bash", "-c", "cd /tmp"], 0x7ffe3cc46230 /* 23 vars */) = 0
stat("/tmp", {st_mode=S_IFDIR|S_ISVTX|0777, st_size=4096, ...}) = 0
chdir("/tmp")
```
`cd` делает системный вызов `chdir()` (а также `stat()`, чтобы узнать, существует ли заданный каталог).

>chdir() changes the current working directory of the calling process
>to the directory specified in path.

> Используя strace выясните, где находится база данных file на
> основании которой она делает свои догадки.

На всякий случай будем трассировать все возможные вызовы: `open, openat, stat, lstat`.

```
$ strace -e open,openat,stat,lstat file ./test
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libmagic.so.1", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/liblzma.so.5", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libbz2.so.1.0", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libz.so.1", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libpthread.so.0", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/usr/lib/locale/locale-archive", O_RDONLY|O_CLOEXEC) = 3
stat("/home/ivg/.magic.mgc", 0x7ffd7ab78220) = -1 ENOENT (No such file or directory)
stat("/home/ivg/.magic", 0x7ffd7ab78220) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/magic.mgc", O_RDONLY) = -1 ENOENT (No such file or directory)
stat("/etc/magic", {st_mode=S_IFREG|0644, st_size=111, ...}) = 0
openat(AT_FDCWD, "/etc/magic", O_RDONLY) = 3
openat(AT_FDCWD, "/usr/share/misc/magic.mgc", O_RDONLY) = 3
openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/gconv/gconv-modules.cache", O_RDONLY) = 3
lstat("./test", {st_mode=S_IFREG|0664, st_size=82, ...}) = 0
openat(AT_FDCWD, "./test", O_RDONLY|O_NONBLOCK) = 3
./test: UTF-8 Unicode text, with CRLF line terminators
+++ exited with 0 +++
```
Интересными строчками являются:

```
stat("/home/ivg/.magic.mgc", 0x7ffd7ab78220) = -1 ENOENT (No such file or directory)
stat("/home/ivg/.magic", 0x7ffd7ab78220) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/magic.mgc", O_RDONLY) = -1 ENOENT (No such file or directory)
stat("/etc/magic", {st_mode=S_IFREG|0644, st_size=111, ...}) = 0
openat(AT_FDCWD, "/etc/magic", O_RDONLY) = 3
openat(AT_FDCWD, "/usr/share/misc/magic.mgc", O_RDONLY) = 3
```

Как выясняется, `file` смотрит в нескольких местах: `~/.magic.mgc`,
`~/.magic`, `/etc/magic.mgc`, `/etc/magic` и
`/usr/share/misc/magic.mgc`, но находит только в двух последних.

> Предположим, приложение пишет лог в текстовый файл. Этот файл
> оказался удален (deleted в lsof), однако возможности сигналом
> сказать приложению переоткрыть файлы или просто перезапустить
> приложение – нет. Так как приложение продолжает писать в удаленный
> файл, место на диске постепенно заканчивается. Основываясь на
> знаниях о перенаправлении потоков предложите способ обнуления
> открытого удаленного файла (чтобы освободить место на файловой
> системе).



Смоделируем приложение.
```
import time
i=0
with open("123.txt", "w") as f:
    while True:
        f.write("{0} Hello there.\n".format(i))
        f.flush()
        time.sleep(3)
        i=i+1
```
Запускаем.

```
$ python3 openforwrite.py &
[1] 6422

$ rm 123.txt 
ivg@vagrant:~$  lsof | grep 123
python3   6422                           ivg    3w      REG              253,0     1050     524519 /home/ivg/123.txt (deleted)
```
Теперь мы знаем дескриптор и pid. К сожалению, трюк `echo -n > /proc/5359/fd/3` не сработает по причинам, изложенным здесь: [Файл дескриптор в Linux с примерами](https://habr.com/ru/post/471038/). Файл открыт в режиме "w". Поэтому применим трюк с отладчиком.

```
$ gdb -p 6422
$ gdb -p 6422
GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2
(...)
(gdb) call lseek(3, 0, 0)
$1 = 0
(gdb) quit
(...)
$ echo -n > /proc/6422/fd/3
$  lsof | grep 123
python3   6422                           ivg    3w      REG              253,0      102     524519 /home/ivg/123.txt (deleted)

```
Теперь файл надежно обнулен (хотя программа успела в него кое-что записать, но уже с самого начала).

> Занимают ли зомби-процессы какие-то ресурсы в ОС (CPU, RAM, IO)?
