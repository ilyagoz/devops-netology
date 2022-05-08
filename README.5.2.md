# Домашнее задание к занятию "5.2. Применение принципов IaaC в работе с виртуальными машинами"

> Опишите своими словами основные преимущества применения на практике
> IaaC паттернов.  Какой из принципов IaaC является основополагающим?

Применение принципов IaC призвано снизить затраты, повысить скорость
работы и снизить риски. Это достигается, в числе прочего, благодаря:

- снижению объема требуемого для обслуживания инфраструктуры труда;
- ускорению  предоставления инфраструктуры благодаря автоматизации;
- повышению стабильности и единообразия среды, устранения дрейфа конфигураций;
- ускорению и упрощению восстановления после сбоев;
- упрощению поиска ошибок.
 
 Основным принципом IaC можно назвать воспроизводимость. (Мне, как
 физику, а не математику, больше нравится термин "воспроизводимость
 (эксперимента)", чем "идемпотентность"). Теоретически, описание
 инфраструктуры в виде кода позволяет воссоздать ее целиком в том же
 виде, что и раньше. При условии, разумеется, что все операции,
 предусмотренные кодом, будут выполнены успешно, и что используемые
 инструменты (например, python) за это время не поменялись неожиданным
 для автора оригинального кода образом.

> Чем Ansible выгодно отличается от других систем управление
> конфигурациями?

Ansible не использует специальных агентов на управляемых хостах и
требует лишь возможности связи с ними по SSH. Таким образом, хост не
тратит никаких ресурсов в промежутках между сеансами. Аналогичный
подход используется в `cdist`, которому не требуется даже Python на
управляемом хосте. Впрочем, это менее популярная система и не может
похвастаться таким же широким набором модулей.

> Какой, на ваш взгляд, метод работы систем конфигурации более
> надёжный push или pull?

Push проще, более предсказуем и в нем меньше потенциала для
ошибок. Если понимать надежность как предсказуемость и прозрачность,
то push будет надежнее. Однако если речь идет о конфигурировании
систем, которые могут работать по своему графику, с которыми нет
предсказуемого канала связи и т.д. - например, это пользовательские
ПК, то возможен только метод pull.

> Установить на личный компьютер:
>
> - VirtualBox
> - Vagrant
> - Ansible
>
> Приложить вывод команд установленных версий каждой из программ, оформленный в markdown.

```
	$ VBoxManage.exe --version
    6.1.34r150636
    $ VBoxManage.exe list runningvms
    "ubuntu-2110_default_1651834196207_3531" {7421ed85-1ed1-4890-bf9c-6897e00a9dfe}
    "vm_default_1651868199612_46508" {70554cca-5601-4f87-8570-124afc284cb6}

	$ vagrant.exe --version
	Vagrant 2.2.19
	
	$ vagrant.exe ssh
Welcome to Ubuntu 21.10 (GNU/Linux 5.13.0-22-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sun May  8 10:41:06 AM UTC 2022

  System load:  0.0                Users logged in:          1
  Usage of /:   15.1% of 30.83GB   IPv4 address for docker0: 172.17.0.1
  Memory usage: 13%                IPv4 address for eth0:    10.0.2.15
  Swap usage:   0%                 IPv4 address for eth1:    192.168.56.3
  Processes:    114


This system is built by the Bento project by Chef Software
More information can be found at https://github.com/chef/bento
Last login: Sun May  8 09:20:10 2022 from 192.168.56.3

	vagrant@control:~$ ansible --version
	ansible [core 2.12.5]
	config file = /etc/ansible/ansible.cfg

    configured module search path = ['/home/vagrant/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
    ansible python module location = /usr/lib/python3/dist-packages/ansible
    ansible collection location = /home/vagrant/.ansible/collections:/usr/share/ansible/collections
    executable location = /usr/bin/ansible
    python version = 3.9.7 (default, Sep 10 2021, 14:59:43) [GCC 11.2.0]
    jinja version = 2.11.3
    libyaml = True
```

> Воспроизвести практическую часть лекции самостоятельно.
>
> Создать виртуальную машину.
> Зайти внутрь ВМ, убедиться, что Docker установлен с помощью команды
> ``` shell> 
> docker ps
> ```

К сожалению, Ansible установлен в виртуальной машине, Vagrant с
VirtualBox на хосте, поэтому непосредственно при развертывании
виртуалки ее нельзя настроить.

    vagrant@control:~$ ansible-playbook -i ./inventory install_docker.yml

    PLAY [host0] ***********************************************************************************************************

    TASK [Gathering Facts] *************************************************************************************************
    ok: [host0]

    TASK [Create diresctory for ssh keys.] *********************************************************************************
    ok: [host0]

    TASK [Adding rsa-key in /root/.ssh/authorized_keys] ********************************************************************
    ok: [host0]

    TASK [Installing tools.] ***********************************************************************************************
    ok: [host0] => (item=git)
    ok: [host0] => (item=curl)

    TASK [Installing docker.] **********************************************************************************************
    changed: [host0]

    TASK [Adding user to docker group.] ************************************************************************************
    changed: [host0]

    PLAY RECAP *************************************************************************************************************
    host0                      : ok=6    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

    vagrant@control:~$ ssh 192.168.56.8
    Welcome to Ubuntu 21.10 (GNU/Linux 5.13.0-22-generic x86_64)

     * Documentation:  https://help.ubuntu.com
     * Management:     https://landscape.canonical.com
     * Support:        https://ubuntu.com/advantage

      System information as of Sun May  8 10:00:50 AM UTC 2022

      System load:  0.18               Users logged in:          1
      Usage of /:   13.4% of 30.83GB   IPv4 address for docker0: 172.17.0.1
      Memory usage: 25%                IPv4 address for eth0:    10.0.2.15
      Swap usage:   0%                 IPv4 address for eth1:    192.168.56.8
      Processes:    120


    This system is built by the Bento project by Chef Software
    More information can be found at https://github.com/chef/bento
    Last login: Sun May  8 09:58:12 2022 from 192.168.56.3
    vagrant@host:~$ docker ps
    CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES


