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

Проделаем трюк с подменой дескриптора файла.
```
$ python3 ./openforwrite.py &
[1] 2332
$ lsof | grep 123
python3   2332                            ivg    3w      REG              253,0     1930     529891 /home/ivg/123.txt
$ rm 123.txt 
$ lsof | grep 123
python3   2332                            ivg    3w      REG              253,0     2134     529891 /home/ivg/123.txt (deleted)

$ gdb -p 2332
(...)
Attaching to process 2332
(...)
(gdb) call open("/home/ivg/123_new.txt", 00001101,0666)
$2 = 4
(gdb) shell ls -la /proc/2332/fd/
total 0
dr-x------ 2 ivg ivg  0 Jan 21 16:25 .
dr-xr-xr-x 9 ivg ivg  0 Jan 21 16:25 ..
lrwx------ 1 ivg ivg 64 Jan 21 16:25 0 -> /dev/pts/1
lrwx------ 1 ivg ivg 64 Jan 21 16:25 1 -> /dev/pts/1
lrwx------ 1 ivg ivg 64 Jan 21 16:25 2 -> /dev/pts/1
l-wx------ 1 ivg ivg 64 Jan 21 16:25 3 -> '/home/ivg/123.txt (deleted)'
l-wx------ 1 ivg ivg 64 Jan 21 16:35 4 -> /home/ivg/123_new.txt
(gdb) call (int)dup2(4,3)
$3 = 3
(gdb) shell ls -la /proc/2332/fd/
total 0
dr-x------ 2 ivg ivg  0 Jan 21 16:25 .
dr-xr-xr-x 9 ivg ivg  0 Jan 21 16:25 ..
lrwx------ 1 ivg ivg 64 Jan 21 16:25 0 -> /dev/pts/1
lrwx------ 1 ivg ivg 64 Jan 21 16:25 1 -> /dev/pts/1
lrwx------ 1 ivg ivg 64 Jan 21 16:25 2 -> /dev/pts/1
l-wx------ 1 ivg ivg 64 Jan 21 16:25 3 -> /home/ivg/123_new.txt
l-wx------ 1 ivg ivg 64 Jan 21 16:35 4 -> /home/ivg/123_new.txt
(gdb) call close(4)
$4 = 0
(gdb) quit
(...)
$ lsof | grep 123
python3   2332                            ivg    3w      REG              253,0      255     525387 /home/ivg/123_new.txt
```
Файл 123.txt успешно удален.

> Занимают ли зомби-процессы какие-то ресурсы в ОС (CPU, RAM, IO)?

Да, какие-то занимают. Дескриптор зомби-процесса остается в списке задач ядра. Размер дескриптора - это размер структуры `task_struct`, который зависит от архитектуры и может быть порядка 2 кб. Какое-то количество тактов процессора тратится на его обработку. Кроме того, зомби занимает pid, которых на 32-битной Linux всего 32768, а у нас 
```
$ cat /proc/sys/kernel/pid_max 
4194304
```

> В iovisor BCC есть утилита opensnoop:

> `root@vagrant:~# dpkg -L bpfcc-tools | grep sbin/opensnoop`
>
> `/usr/sbin/opensnoop-bpfcc`

> На какие файлы вы увидели вызовы группы open за первую секунду работы утилиты? 
```
vagrant@vagrant:~$ sudo opensnoop-bpfcc
PID    COMM               FD ERR PATH
636    irqbalance          6   0 /proc/interrupts
636    irqbalance          6   0 /proc/stat
636    irqbalance          6   0 /proc/irq/20/smp_affinity
636    irqbalance          6   0 /proc/irq/0/smp_affinity
636    irqbalance          6   0 /proc/irq/1/smp_affinity
636    irqbalance          6   0 /proc/irq/8/smp_affinity
636    irqbalance          6   0 /proc/irq/12/smp_affinity
636    irqbalance          6   0 /proc/irq/14/smp_affinity
636    irqbalance          6   0 /proc/irq/15/smp_affinity
807    vminfo              4   0 /var/run/utmp
629    dbus-daemon        -1   2 /usr/local/share/dbus-1/system-services
629    dbus-daemon        20   0 /usr/share/dbus-1/system-services
629    dbus-daemon        -1   2 /lib/dbus-1/system-services
629    dbus-daemon        20   0 /var/lib/snapd/dbus-1/system-services/
380    systemd-udevd      14   0 /sys/fs/cgroup/unified/system.slice/systemd-udevd.service/cgroup.procs
380    systemd-udevd      14   0 /sys/fs/cgroup/unified/system.slice/systemd-udevd.service/cgroup.threads
807    vminfo              4   0 /var/run/utmp
629    dbus-daemon        -1   2 /usr/local/share/dbus-1/system-services
629    dbus-daemon        20   0 /usr/share/dbus-1/system-services
629    dbus-daemon        -1   2 /lib/dbus-1/system-services
629    dbus-daemon        20   0 /var/lib/snapd/dbus-1/system-services/
```

> Какой системный вызов использует uname -a? Приведите цитату из man
> по этому системному вызову, где описывается альтернативное
> местоположение в /proc, где можно узнать версию ядра и релиз ОС.
```
$ strace uname -a
(...)

uname({sysname="Linux", nodename="vagrant", ...}) = 0

(...)
```

> Part of the utsname information is also accessible via
> /proc/sys/kernel/{ostype, hostname, osrelease, version, domainname}.

```
$ uname -a
Linux vagrant 5.4.0-91-generic #102-Ubuntu SMP Fri Nov 5 16:31:28 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
$ cat  /proc/sys/kernel/{ostype,hostname,osrelease,version,domainname}
Linux
vagrant
5.4.0-91-generic
#102-Ubuntu SMP Fri Nov 5 16:31:28 UTC 2021
(none)
```

> Чем отличается последовательность команд через ; и через && в bash? Например:
>

```
root@netology1:~# test -d /tmp/some_dir; echo Hi
Hi
root@netology1:~# test -d /tmp/some_dir && echo Hi
root@netology1:~#
```

Команды, перечисленные через `;`, будут исполнены одна за другой,
независимо от кода возврата предыдущей. Если в цепочке команд,
связанных через `&&`, какая-то завершится с кодом не 0, bash прервет
исполнение цепочки.

> Есть ли смысл использовать в bash &&, если применить set -e?

Казалось бы, `set -e` заставит выполнение скрипта прекратиться, если
какая-то команда завершится с ошибкой, точно так же, как и `&&`. Но это не совсем так, например, оно не срабатывает при подстановке команд (если только не запускать `bash --posix`). Есть много разных особенностей `set -e`, см. [Why doesn't set -e (or set -o errexit, or trap ERR) do what I expected?](http://mywiki.wooledge.org/BashFAQ/105/)

Пример `test.sh`:
``` shell
#!/bin/bash 
set -e

a=$(rm -f /tmp/no_such_file; test -r /tmp/no_such_file; ls -l /tmp/no_such_file; echo "All is well.")
echo $a
```
```
$ ./test.sh
ls: cannot access '/tmp/no_such_file': No such file or directory
All is well.
```
Команды в скобках выполнились.
Пример `test2.sh`:
``` shell
#!/bin/bash 
set -e

a=$(rm -f /tmp/no_such_file && test -r /tmp/no_such_file && ls -l /tmp/no_such_file && echo "All is well.")
echo $a
```
```
$ ./test2.sh
$ 
```
Команды в скобках не выполнились. Так что смысл иногда есть.

> Из каких опций состоит режим bash set -euxo pipefail и почему его
> хорошо было бы использовать в сценариях?

Это так называемый [Bash Strict
Mode](http://redsymbol.net/articles/unofficial-bash-strict-mode/). Опции
делают следующее: -e заставит выполнение скрипта прекратиться, если
какая-то команда завершится с ошибкой (см. выше), -u делает ошибкой
использование неинициализированных переменных, -x выводит команды с
аргументами по мере их исполнения, -o pipefail делает кодом возврата
из пайплайна код возврата последней команды, завершившейся с
ошибкой. Предполагается, что набор этих опций поможет не пропускать
ошибки при выполнении сценариев.

> Используя -o stat для ps, определите, какой наиболее часто
> встречающийся статус у процессов в системе. В man ps ознакомьтесь
> (/PROCESS STATE CODES) что значат дополнительные к основной
> заглавной буквы статуса процессов. Его можно не учитывать при
> расчете (считать S, Ss или Ssl равнозначными).

```
$ ps -eo stat= | sort | uniq -c | sort -g
      1 R+
      1 Sl
      1 SLsl
      1 S<s
      2 SN
      3 S+
      3 Ss+
      6 Ssl
      7 S<
     10 I
     15 Ss
     31 S
     40 I<
 ```

Или, не учитывая дополнительные буквы:

```
$ ps -eo stat= | cut -c 1 | sort | uniq -c | sort -g
      1 R
     49 I
     71 S
```
Большинство процессов в interruptible sleep, ждут сигналов.
