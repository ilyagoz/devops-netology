> Для выполнения заданий в этом разделе давайте склонируем репозиторий с исходным кодом терраформа https://github.com/hashicorp/terraform

> В виде результата напишите текстом ответы на вопросы и каким образом эти ответы были получены.

> Найдите полный хеш и комментарий коммита, хеш которого начинается на aefea.

    $ git show aefea -s --format=oneline
    aefead2207ef7e2aa5dc81a34aedf0cad4c32545 Update CHANGELOG.md

> Какому тегу соответствует коммит 85024d3?

    $ git show 85024d3 -s --format=oneline
    85024d3100126de36331c6982bfaac02cdab9e76 (tag: v0.12.23) v0.12.23

Тег ``v0.12.23``.

> Сколько родителей у коммита b8d720? Напишите их хеши.

    $ git show b8d720 --format=short
    commit b8d720f8340221f2146e4e4870bf2ee0bc48f2d5
    Merge: 56cd7859e 9ea88f22f
    Author: Chris Griggs <cgriggs@hashicorp.com>

Два: ``56cd7859e`` и ``9ea88f22f``. Или так:

    $ git rev-list --parents -n 1 b8d720
    b8d720f8340221f2146e4e4870bf2ee0bc48f2d5 56cd7859e05c36c06b56d013b55a252d0bb7e158 9ea88f22fc6269854151c571162c5bcf958bee2b

> Перечислите хеши и комментарии всех коммитов которые были сделаны между тегами v0.12.23 и v0.12.24.

    $ git log v0.12.23..v0.12.24 --oneline
    33ff1c03b (tag: v0.12.24) v0.12.24
    b14b74c49 [Website] vmc provider links
    3f235065b Update CHANGELOG.md
    6ae64e247 registry: Fix panic when server is unreachable
    5c619ca1b website: Remove links to the getting started guide's old location
    06275647e Update CHANGELOG.md
    d5f9411f5 command: Fix bug when using terraform login on Windows
    4b6d06cc5 Update CHANGELOG.md
    dd01a3507 Update CHANGELOG.md
    225466bc3 Cleanup after v0.12.23 release

> Найдите коммит в котором была создана функция func providerSource, ее определение в коде выглядит так func providerSource(...) (вместо троеточего перечислены аргументы).

    $ git log -G 'func\s+providerSource' --oneline
    f5012c12d command/cliconfig: Installation methods, not installation sources
    5af1e6234 main: Honor explicit provider_installation CLI config when present
    8c928e835 main: Consult local directories as potential mirrors of providers

Коммит ``8c928e835``. Регулярное выражение на всякий случай - вдруг в определении функции был лишний пробел?

> Найдите все коммиты в которых была изменена функция globalPluginDirs.

    $ git grep -G -E "func\s+globalPluginDirs"
    plugins.go:func globalPluginDirs() []string {

    $ git log -L :globalPluginDirs:plugins.go --format=oneline -s
    78b12205587fe839f10d946ea3fdc06719decb05 Remove config.go and update things using its aliases
    52dbf94834cb970b510f2fba853a5b49ad9b1a46 keep .terraform.d/plugins for discovery
    41ab0aef7a0fe030e84018973a64135b11abcd70 Add missing OS_ARCH dir to global plugin paths
    66ebff90cdfaa6938f26f908c7ebad8d547fea17 move some more plugin search path logic to command
    8364383c359a6b738a436d1b7745ccdce178df47 Push plugin discovery down into command package

> Кто автор функции synchronizedWriters?

    $ git log -G 'func\s+synchronizedWriters' --oneline
    bdfea50cc remove unused
    5ac311e2a main: synchronize writes to VT100-faker on Windows
    $ git show 5ac311e2a --format=short -s
    commit 5ac311e2a91e381e2f52234668b49ba670aa0fe5
    Author: Martin Atkins <mart@degeneration.co.uk>

        main: synchronize writes to VT100-faker on Windows

Martin Atkins <mart@degeneration.co.uk>
