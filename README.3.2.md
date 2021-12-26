# Домашнее задание к занятию "3.2. Работа в терминале, лекция 2"

>1. Какого типа команда cd? Попробуйте объяснить, почему она именно
> такого типа; опишите ход своих мыслей, если считаете что она могла
> бы быть другого типа.
```
$ type cd
cd is a shell builtin
```

Команда `cd` - встроенная, потому что ей нужно модифицировать
окружение процесса, в котором она запущена, а именно, "сделать
указанный каталог отправной точкой для поиска путей для путей, не
начинающихся с '/'"
([POSIX](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/cd.html)). Внешние
команды исполняются в своем окружении и не могут (в общем случае),
воздействовать на родительский процесс. Поэтому ей надо быть
встроенной, как [обнаружили еще Деннис Ричи с
коллегами](https://unix.stackexchange.com/questions/38808/why-is-cd-not-a-program):

> In the midst of our jubilation, it was discovered that the chdir
> (change current directory) command had stopped working. There was
> much reading of code and anxious introspection about how the
> addition of fork could have broken the chdir call. Finally the truth
> dawned: in the old system chdir was an ordinary command; it adjusted
> the current directory of the (unique) process attached to the
> terminal. Under the new system, the chdir command correctly changed
> the current directory of the process created to execute it, but this
> process promptly terminated and had no effect whatsoever on its
> parent shell! It was necessary to make chdir a special command,
> executed internally within the shell. It turns out that several
> command-like functions have the same property, for example login.

Однако во FreeBSD, OS X и некоторых других системах внешняя `cd` есть,
так как POSIX требует, чтобы эта команда, в числе других, была исполняемой:

> [C.1.7 Built-In Utilities](https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap01.html#tag_23_01_07)
>
> All of these utilities can be exec-ed. 

```
$ uname -a
FreeBSD  12.3-RELEASE FreeBSD 12.3-RELEASE r371126 GENERIC  amd64
$ which cd
/usr/bin/cd
```

Впрочем, во FreeBSD она не делает ничего полезного, кроме возврата кода об
ошибке, если каталог не существует или недоступен. 

> 2. Какая альтернатива без pipe команде grep <some_string> <some_file> |
> wc -l?

`grep -c <some_string> <some_file>`

> 3. Какой процесс с PID 1 является родителем для всех процессов в вашей
> виртуальной машине Ubuntu 20.04?

```
   p pidlist
              Select by process ID.  Identical to -p and --pid.
```

Попробуем.

```
$ ps -p 1
    PID TTY          TIME CMD
      1 ?        00:00:02 systemd
$ ps p 1
    PID TTY      STAT   TIME COMMAND
      1 ?        Ss     0:02 /sbin/init
```

Ага, identical. init, хотя на самом деле это ссылка на systemd.

> 4. Как будет выглядеть команда, которая перенаправит вывод stderr ls
>    на другую сессию терминала?


