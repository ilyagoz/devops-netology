# Домашнее задание к занятию "3.5. Файловые системы"

> Могут ли файлы, являющиеся жесткой ссылкой на один объект, иметь
> разные права доступа и владельца? Почему?

Нет.  "...жесткие ссылки не являются особым типом файлов, просто
файловая система позволяет создавать несколько ссьmок на один файл. Не
только содержимое, но и атрибуты файла, в частности права доступа и
идентификатор владельца, являются общими для всех ссылок." [1,
стр. 165]

> (...) Данная конфигурация создаст новую виртуальную машину с двумя
> дополнительными неразмеченными дисками по 2.5 Гб.

```
vagrant@vagrant:~$ lsblk
NAME                      MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
loop0                       7:0    0 70.3M  1 loop /snap/lxd/21029
loop1                       7:1    0 55.4M  1 loop /snap/core18/2128
loop2                       7:2    0 32.3M  1 loop /snap/snapd/12704
loop3                       7:3    0 55.5M  1 loop /snap/core18/2284
loop4                       7:4    0 43.4M  1 loop /snap/snapd/14549
loop5                       7:5    0 61.9M  1 loop /snap/core20/1270
loop6                       7:6    0 67.2M  1 loop /snap/lxd/21835
loop7                       7:7    0 61.9M  1 loop /snap/core20/1328
sda                         8:0    0   64G  0 disk
├─sda1                      8:1    0    1M  0 part
├─sda2                      8:2    0    1G  0 part /boot
└─sda3                      8:3    0   63G  0 part
  └─ubuntu--vg-ubuntu--lv 253:0    0 31.5G  0 lvm  /
sdb                         8:16   0  2.5G  0 disk
sdc                         8:32   0  2.5G  0 disk
```

> Используя fdisk, разбейте первый диск на 2 раздела: 2 Гб, оставшееся
> пространство.

```
Command (m for help): p
Disk /dev/sdb: 2.51 GiB, 2684354560 bytes, 5242880 sectors
Disk model: VBOX HARDDISK
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: F476A4C6-EB85-D44D-BE0F-CC22BD2CCB06

Device       Start     End Sectors  Size Type
/dev/sdb1     2048 4196351 4194304    2G Linux filesystem
/dev/sdb2  4196352 5242846 1046495  511M Linux filesystem
```

> Используя sfdisk, перенесите данную таблицу разделов на второй диск.

```
vagrant@vagrant:~$ sudo sfdisk --dump /dev/sdb > sdb.dump
vagrant@vagrant:~$ sudo sfdisk /dev/sdc < sdb.dump
Checking that no-one is using this disk right now ... OK

Disk /dev/sdc: 2.51 GiB, 2684354560 bytes, 5242880 sectors
Disk model: VBOX HARDDISK
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes

>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Created a new GPT disklabel (GUID: F476A4C6-EB85-D44D-BE0F-CC22BD2CCB06).
/dev/sdc1: Created a new partition 1 of type 'Linux filesystem' and of size 2 GiB.
/dev/sdc2: Created a new partition 2 of type 'Linux filesystem' and of size 511 MiB.
/dev/sdc3: Done.

New situation:
Disklabel type: gpt
Disk identifier: F476A4C6-EB85-D44D-BE0F-CC22BD2CCB06

Device       Start     End Sectors  Size Type
/dev/sdc1     2048 4196351 4194304    2G Linux filesystem
/dev/sdc2  4196352 5242846 1046495  511M Linux filesystem

The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
vagrant@vagrant:~$
```

> Соберите mdadm RAID1 на паре разделов 2 Гб.

```
vagrant@vagrant:~$ sudo mdadm --create /dev/md/raid1 --level=1 -n 2 /dev/sdb1 /dev/sdc1
mdadm: Note: this array has metadata at the start and
    may not be suitable as a boot device.  If you plan to
    store '/boot' on this device please ensure that
    your boot-loader understands md/v1.x metadata, or use
    --metadata=0.90
Continue creating array? y
mdadm: Defaulting to version 1.2 metadata
mdadm: array /dev/md/raid1 started.
vagrant@vagrant:~$ lsblk
(...)
sdb                         8:16   0  2.5G  0 disk
├─sdb1                      8:17   0    2G  0 part
│ └─md127                   9:127  0    2G  0 raid1
└─sdb2                      8:18   0  511M  0 part
sdc                         8:32   0  2.5G  0 disk
├─sdc1                      8:33   0    2G  0 part
│ └─md127                   9:127  0    2G  0 raid1
└─sdc2                      8:34   0  511M  0 part
```

> Соберите mdadm RAID0 на второй паре маленьких разделов.

```
vagrant@vagrant:~$ sudo mdadm --create /dev/md/raid0 --level=0 -n 2 /dev/sdb2 /dev/sdc2
mdadm: Defaulting to version 1.2 metadata
mdadm: array /dev/md/raid0 started.
vagrant@vagrant:~$
```

> Создайте 2 независимых PV на получившихся md-устройствах.

```
vagrant@vagrant:~$ sudo pvcreate /dev/md/raid1
  Physical volume "/dev/md/raid1" successfully created.
vagrant@vagrant:~$ sudo pvcreate /dev/md/raid0
  Physical volume "/dev/md/raid0" successfully created.
```

> Создайте общую volume-group на этих двух PV.

(можно было обойтись без предыдущей команды)

```
vagrant@vagrant:~$ sudo vgcreate vg /dev/md/raid1 /dev/md/raid0
  Volume group "vg" successfully created
```

> Создайте LV размером 100 Мб, указав его расположение на PV с RAID0.

```
vagrant@vagrant:~$ sudo lvcreate -L 100mb vg /dev/md/raid0
  Logical volume "lvol0" created.
```

> Создайте mkfs.ext4 ФС на получившемся LV.

```
vagrant@vagrant:~$ sudo mkfs.ext4 /dev/vg/lvol0
mke2fs 1.45.5 (07-Jan-2020)
Creating filesystem with 25600 4k blocks and 25600 inodes

Allocating group tables: done
Writing inode tables: done
Creating journal (1024 blocks): done
Writing superblocks and filesystem accounting information: done
```

> Смонтируйте этот раздел в любую директорию, например, /tmp/new.

```
vagrant@vagrant:~$ sudo mount /dev/vg/lvol0 /mnt/
```

> Поместите туда тестовый файл, например wget
> https://mirror.yandex.ru/ubuntu/ls-lR.gz -O /tmp/new/test.gz.

```
vagrant@vagrant:~$ sudo wget https://mirror.yandex.ru/ubuntu/ls-lR.gz -O /mnt/test.gz
--2022-01-31 16:38:52--  https://mirror.yandex.ru/ubuntu/ls-lR.gz
Resolving mirror.yandex.ru (mirror.yandex.ru)... 213.180.204.183, 2a02:6b8::183
Connecting to mirror.yandex.ru (mirror.yandex.ru)|213.180.204.183|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 22018280 (21M) [application/octet-stream]
Saving to: ‘/mnt/test.gz’

/mnt/test.gz                  100%[=================================================>]  21.00M  2.35MB/s    in 9.1s

2022-01-31 16:39:01 (2.31 MB/s) - ‘/mnt/test.gz’ saved [22018280/22018280]
```

> Прикрепите вывод lsblk.

```
vagrant@vagrant:~$ lsblk
NAME                      MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
loop0                       7:0    0 70.3M  1 loop  /snap/lxd/21029
loop1                       7:1    0 55.4M  1 loop  /snap/core18/2128
loop2                       7:2    0 32.3M  1 loop  /snap/snapd/12704
loop3                       7:3    0 55.5M  1 loop  /snap/core18/2284
loop4                       7:4    0 43.4M  1 loop  /snap/snapd/14549
loop5                       7:5    0 61.9M  1 loop  /snap/core20/1270
loop6                       7:6    0 67.2M  1 loop  /snap/lxd/21835
loop7                       7:7    0 61.9M  1 loop  /snap/core20/1328
sda                         8:0    0   64G  0 disk
├─sda1                      8:1    0    1M  0 part
├─sda2                      8:2    0    1G  0 part  /boot
└─sda3                      8:3    0   63G  0 part
  └─ubuntu--vg-ubuntu--lv 253:0    0 31.5G  0 lvm   /
sdb                         8:16   0  2.5G  0 disk
├─sdb1                      8:17   0    2G  0 part
│ └─md127                   9:127  0    2G  0 raid1
└─sdb2                      8:18   0  511M  0 part
  └─md126                   9:126  0 1017M  0 raid0
    └─vg-lvol0            253:1    0  100M  0 lvm   /mnt
sdc                         8:32   0  2.5G  0 disk
├─sdc1                      8:33   0    2G  0 part
│ └─md127                   9:127  0    2G  0 raid1
└─sdc2                      8:34   0  511M  0 part
  └─md126                   9:126  0 1017M  0 raid0
    └─vg-lvol0            253:1    0  100M  0 lvm   /mnt
```

> Протестируйте целостность файла:

```
vagrant@vagrant:~$ gzip -tv /mnt/test.gz
/mnt/test.gz:    OK
```

> Используя pvmove, переместите содержимое PV с RAID0 на RAID1.

```
vagrant@vagrant:~$ sudo pvmove /dev/md/raid0 /dev/md/raid1
  /dev/md/raid0: Moved: 8.00%
  /dev/md/raid0: Moved: 100.00%
```

> Сделайте --fail на устройство в вашем RAID1 md.

```
vagrant@vagrant:~$ sudo mdadm /dev/md/raid1 --fail /dev/sdc1
mdadm: set /dev/sdc1 faulty in /dev/md/raid1
```

> Подтвердите выводом dmesg, что RAID1 работает в деградированном
> состоянии.

```
[197411.940663] md/raid1:md127: Disk failure on sdc1, disabling device.
                md/raid1:md127: Operation continuing on 1 devices.
```

> Протестируйте целостность файла, несмотря на "сбойный" диск он
> должен продолжать быть доступен:

```
vagrant@vagrant:~$ gzip -tv /mnt/test.gz
/mnt/test.gz:    OK
```

> Погасите тестовый хост, vagrant destroy.

```
$ vagrant.exe destroy
    default: Are you sure you want to destroy the 'default' VM? [y/N] y
==> default: Forcing shutdown of VM...
==> default: Destroying VM and associated drives...
```

Литература

1. Немет, Эви, Снайдер, Гарт, Хейн, Трент, Уэйли, Бен, Макни, Дэн.
Uпix и Linux: руководство системного администратора, 5-е изд.: Пер. с
англ. - СПб. : ООО "Диалектика", 2020
