# 4DreamTeam

Языки: [English](README.md) | [Русский](README.ru.md)

4DreamTeam - это навык для Codex, созданный для людей, у которых есть идеи и которым нужна помощь, чтобы превратить их в понятную, проверяемую и доведенную до результата работу.

Вместо того чтобы просить одного AI-агента сделать все в одном длинном диалоге, 4DreamTeam дает Codex небольшую команду ролей: product, analytic, developer, quality, wiki, marketing и devops. В результате идеи превращаются в продуктовые описания, описания - в задачи, задачи - в проверенную работу, а важные знания остаются в файлах, а не теряются в истории чата.

## Зачем он нужен

Большинство людей не начинают с идеального технического задания. Обычно запрос звучит ближе к этому:

```txt
У меня есть идея.
Можно ли это сделать?
Что должно произойти сначала?
Как понять, что работа готова?
Можно ли объяснить это пользователям понятнее?
Можно ли поддерживать документацию в актуальном состоянии?
```

4DreamTeam помогает Codex замедлиться ровно настолько, чтобы сделать работу конкретной:

- чего мы хотим добиться;
- для кого это делается;
- что входит в текущий объем работ;
- что может подождать;
- какие файлы или системы затронуты;
- как результат будет проверен;
- что нужно задокументировать после приемки.

Поэтому 4DreamTeam полезен основателям, продуктовым специалистам, операторам, разработчикам и любым людям с идеями, которым нужна структура без необходимости сначала становиться менеджером проекта.

## Главное обещание

4DreamTeam превращает идею в прослеживаемый рабочий процесс:

```txt
idea -> product brief -> technical task -> implementation -> quality review -> documentation
```

Он также помогает с базами знаний проектов, инфраструктурными заметками, позиционированием README, пресс-релизами, публичными материалами и продолжением работы между сессиями.

Главная точка входа - `$4DreamTeam`. Не нужно запоминать имена ролей: ведущая роль сама выбирает нужный маршрут.

## Почему в Codex он называется 4DreamTeam

Идентификатор навыка - `4dreamteam`, а продукт называется 4DreamTeam.

В Codex отображаемое имя - `4DreamTeam`, чтобы его было быстро выбирать после ввода `$`: на многих клавиатурах `$` находится на клавише `4`, поэтому повторное нажатие `4` сразу ведет к нужному навыку.

## Для кого это

4DreamTeam подходит:

- людям с продуктовыми идеями, которым нужен понятный следующий шаг;
- тем, кто хочет, чтобы Codex не прыгал сразу в код;
- сопровождающим проектов, которым важно, чтобы задачи, отчеты и документация жили дольше одного чата;
- командам, которым нужны критерии приемки и независимая проверка качества перед завершением работы;
- операторам, которым нужны аккуратные DevOps-заметки на основе проверенных фактов;
- проектам, которым нужны README, запуск или продуктовое сообщение, основанные на реальных возможностях.

Он особенно полезен, когда работа достаточно важна, чтобы решения, предположения и приемка были видимыми.

## Что умеет 4DreamTeam

4DreamTeam помогает Codex:

- превращать сырую идею или бизнес-запрос в продуктовое описание;
- декомпозировать функцию в задачу, готовую к реализации;
- выполнять ограниченные изменения через процесс разработки;
- запускать независимую проверку качества до приемки;
- создавать, проверять, синхронизировать и углублять документацию проекта;
- суммировать и проверять workspace;
- обновлять правила workspace после обновления навыка;
- улучшать сам 4DreamTeam через тот же контролируемый жизненный цикл;
- готовить пресс-релизы, позиционирование README, продуктовые сообщения и аналитические материалы для внешней аудитории;
- документировать серверы, деплой, SSH-доступ, диагностику, миграции и runbook с DevOps-предохранителями.

## Роли

| Роль | Что делает |
|---|---|
| `product` | Уточняет, что нужно построить, для кого, зачем, что входит в объем работ и как принять результат с продуктовой точки зрения. |
| `analytic` | Превращает продуктовые описания или прямые запросы в технические задачи с затронутыми областями, требованиями, рисками и проверяемыми критериями приемки. |
| `developer` | Реализует одобренные задачи, обновляет тесты при необходимости, запускает проверки и пишет отчеты о реализации. |
| `quality` | Независимо проверяет реализацию и документацию по критериям приемки. |
| `wiki` | Создает и поддерживает проектные базы знаний, основанные на подтвержденных источниках. |
| `marketing` | Превращает подтвержденную продуктовую ценность в пресс-релизы, позиционирование README, продуктовые сообщения, материалы запуска и рыночную аналитику. |
| `devops` | Ведет инфраструктурную документацию, карточки серверов, диагностику деплоя, правила SSH-доступа и операционные runbook. |

## Типичный путь

Начните с идеи:

```txt
Run $4DreamTeam.

Goal:
I want to build a lightweight booking system for a small studio.

Context:
The owner takes reservations manually and loses track of changes.
```

4DreamTeam может превратить это в:

1. продуктовое описание с пользователями, объемом работ, сценариями и критериями приемки;
2. техническую задачу с требованиями к реализации;
3. изменения в коде и отчет разработчика;
4. независимый отчет качества;
5. обновление документации, если принятое поведение меняет проект.

В `controlled` mode 4DreamTeam останавливается на важных этапах, чтобы пользователь мог подтвердить следующий шаг.

## Почему файлы важны

4DreamTeam намеренно хранит состояние работы в файлах:

```txt
tasks/
reports/
docs/
```

Это дает:

- продуктовые описания, которые можно проверить до реализации;
- технические задачи, к которым можно вернуться позже;
- отчеты разработчика отдельно от отчетов качества;
- отклоненную работу с понятными путями исправления;
- знания проекта в Markdown;
- DevOps-факты, задокументированные только после проверки.

Смысл не в бюрократии. Смысл в непрерывности, проверяемости и меньшем количестве скрытых предположений.

## Быстрый старт

Установите этот репозиторий как навык Codex из GitHub-репозитория или локальной копии.

После установки перезапустите Codex и проверьте, что навык доступен:

```txt
Is the 4DreamTeam skill available?
```

Затем используйте его из любой папки:

```txt
Run $4DreamTeam.
```

Если папка пустая или еще не является 4DreamTeam workspace, навык должен спросить перед созданием файлов workspace.

## Быстрые команды

Используйте эти короткие запросы, когда workspace уже содержит артефакты 4DreamTeam:

```txt
$4DreamTeam init workspace
$4DreamTeam connect project <project-name> from <source-path>
$4DreamTeam status
$4DreamTeam continue
$4DreamTeam validate workspace
$4DreamTeam self-update workspace
$4DreamTeam check docs for <project-name>
$4DreamTeam write a press release for <project-name>
$4DreamTeam improve README positioning for <project-name>
$4DreamTeam improve <project-name>
$4DreamTeam improve 4DreamTeam itself from ../codex/4DreamTeam
```

`status`, `continue` и `validate workspace` по умолчанию работают в режиме чтения. 4DreamTeam должен объяснить следующий шаг жизненного цикла и дождаться подтверждения перед изменением файлов.

`self-update workspace` заменяет только корневой `AGENTS.md` workspace из шаблона установленного навыка, а затем просит пользователя перезапустить Codex.

## Структура workspace

Обычный 4DreamTeam workspace не содержит директорию `skill/`. После инициализации он содержит:

```txt
AGENTS.md
docs/index.md
tasks/
  product/
  pending/
  in-progress/
  done/
  rejected/
reports/
  product/
  tasks/
  quality/
```

Документация проекта находится здесь:

```txt
docs/<project-name>/
```

DevOps-документация проекта находится здесь:

```txt
docs/<project-name>/devops/
  servers/
  runbooks/
```

`runbooks/` используется только когда задача явно просит сохранить runbook.

## Основные workflow

### Product To Implementation

Используйте это, когда запрос начинается с бизнес-намерения, продуктового направления или идеи функции:

```txt
Run $4DreamTeam.

Mode:
controlled

Goal:
Develop the product in the direction of <direction>.

Context:
<what is known about users, the problem, and constraints>

Expected result:
Product brief, then task specification, implementation, quality review, and docs update if needed.
```

В `controlled` mode 4DreamTeam останавливается для подтверждения после этапов product и analytic.

### Direct Task

Используйте это, когда запрос уже похож на задачу реализации:

```txt
Run $4DreamTeam.

Mode:
controlled

Goal:
Add support for X in module Y.

Constraints:
Do not change the public API.
Do not add dependencies unless necessary.

Expected result:
X works, is covered by tests, and quality review is accepted.
```

Обычный маршрут:

```txt
analytic -> developer -> quality -> wiki if needed
```

`quality` не является необязательным этапом для процесса реализации.

### Workspace Status

Используйте это, когда возвращаетесь к workspace или решаете, что делать дальше:

```txt
Run $4DreamTeam status.
```

Проверка статуса суммирует предварительную проверку workspace, продуктовые описания, задачи в состояниях pending/in-progress/done/rejected, отчеты разработчика, отчеты качества, известные wiki проектов, отсутствующие `sources.md`, блокеры и рекомендуемое следующее действие.

Статус по умолчанию не меняет файлы.

### Workspace Validation

Используйте это, чтобы найти структурные проблемы или проблемы жизненного цикла в workspace:

```txt
Run $4DreamTeam validate workspace.
```

Validation проверяет обязательные папки, согласованность задач и отчетов, отчеты без задач, отклоненные задачи без применимых отчетов качества, wiki проектов без `sources.md`, недопустимые статусы страниц и отсутствующий `wiki-meta` на управляемых страницах.

Validation возвращает найденные проблемы и план исправления. Он не исправляет файлы, пока пользователь явно не подтвердит конкретные изменения.

### Workspace Self-Update

Используйте это после установки или обновления навыка 4DreamTeam и перед продолжением работы в существующем workspace:

```txt
Run $4DreamTeam self-update workspace.
```

Self-update намеренно узкий. Он заменяет только корневой `AGENTS.md` workspace из шаблона установленного навыка:

```txt
assets/templates/workspace/AGENTS.md
```

Он не должен менять `docs/`, `tasks/`, `reports/`, `keys/`, одобренные репозитории-источники или файлы установленного навыка.

После замены `AGENTS.md` перезапустите Codex, чтобы обновленные инструкции навыка и workspace загрузились в чистой сессии. После перезапуска можно выполнить `$4DreamTeam validate workspace`, если нужно проверить workspace.

### Wiki Bootstrap

Используйте это, чтобы создать проектную базу знаний из одобренных путей к источникам:

```txt
Run $4DreamTeam: wiki bootstrap.

Knowledge base name:
northstar-ledger

Sources:
- ../northstar-ledger/src
- ../northstar-ledger/tests
- ../northstar-ledger/package.json
```

Навык рассматривает каждый одобренный source path как жесткую границу чтения. Он не должен сам выводить доступ к родительским директориям, соседним проектам, `.env` files, secrets, dumps или unrelated user files.

Путь результата:

```txt
docs/<project-name>/
```

### Wiki Audit

Используйте это для проверки существующей документации по одобренным источникам в режиме чтения:

```txt
Run $4DreamTeam wiki audit for northstar-ledger.

Documentation:
- docs/northstar-ledger

Sources:
- ../northstar-ledger/src
- ../northstar-ledger/tests
```

### Marketing

Используйте маршрут marketing для внешних коммуникаций и продуктового нарратива:

```txt
Run $4DreamTeam marketing.

Goal:
Rewrite the README so new users understand what the product is, who it is for, why it matters, and how to try it.

Sources:
- docs/northstar-ledger
- ../northstar-ledger/README.md
```

Marketing может создавать пресс-релизы, анонсы запуска, позиционирование README, продуктовые сообщения, FAQ, кейсы и аналитические материалы для внешней аудитории.

Marketing должен опираться на подтвержденные источники. Он не должен выдумывать метрики, клиентов, бенчмарки, сертификации, security claims или обязательства по roadmap.

### Self-Improvement

Используйте это, когда 4DreamTeam workspace управляет улучшениями самого навыка `4DreamTeam`:

```txt
Run $4DreamTeam.

Goal:
Improve 4DreamTeam itself.

Knowledge base:
4DreamTeam

Approved source:
../codex/4DreamTeam
```

Self-improvement следует обычному контролируемому жизненному циклу:

```txt
product -> analytic -> developer -> quality
```

Исходный repository является одобренной границей источников. Типичные цели для записи: `skill/SKILL.md`, `skill/references/`, `skill/assets/templates/`, `skill/agents/openai.yaml`, `README.md` и репозиторный `AGENTS.md`.

Markdown-документация и шаблоны в репозитории навыка остаются English-only, если правила репозитория явно не изменены.

### DevOps

Используйте маршрут DevOps для инфраструктурной работы:

```txt
Run $4DreamTeam devops.

Project:
northstar-ledger

Goal:
Inspect the production server and update the server card with verified facts only.
```

Документация серверов хранится здесь:

```txt
docs/<project-name>/devops/servers/
```

SSH-ключи ищутся только в корне workspace:

```txt
keys/
```

`keys/` - локальная секретная область. Навык не должен печатать содержимое ключей, копировать ключи в документацию или коммитить их.

DevOps следует более строгой операционной последовательности:

```txt
inspect -> explain -> wait for approval -> change -> verify -> document
```

Рискованные операции всегда требуют явного подтверждения, включая деплой, перезапуски, миграции, изменения окружения, изменения nginx/systemd/Docker, записи в базу данных, изменения firewall и DNS.

## Гарантии безопасности

4DreamTeam построен вокруг консервативных операционных правил:

- не писать файлы, пока предварительная проверка workspace не пройдена или пользователь не подтвердил workspace;
- не обходить рабочий процесс, когда применим маршрут 4DreamTeam;
- не пропускать независимую проверку качества для работы по реализации;
- не обновлять post-acceptance wiki docs до принятого отчета качества;
- не читать вне одобренных source paths;
- не раскрывать secrets в задачах, отчетах, документации или чате;
- не запускать migrations или destructive commands без явного подтверждения;
- документировать для DevOps только проверенные факты;
- не выдумывать marketing claims без одобренных источников.

## Структура репозитория

Этот репозиторий содержит сам навык:

```txt
4DreamTeam/
  AGENTS.md
  README.md
  README.ru.md
  skill/
    SKILL.md
    agents/
      openai.yaml
    references/
    assets/
      templates/
```

Важные файлы:

- `skill/SKILL.md` - metadata навыка, trigger surface, entrypoint и hard guarantees.
- `skill/references/` - подробные правила ролей и рабочих процессов.
- `skill/assets/templates/` - шаблоны, которые копируются или адаптируются в пользовательские workspace.
- `skill/agents/openai.yaml` - UI metadata для Codex.
- `AGENTS.md` - правила разработки для этого repository.

## Разработка

Этот репозиторий предназначен для разработки навыка `4DreamTeam`, а не для запуска задач внешних проектов через сам 4DreamTeam.

Перед изменением навыка проверьте, какой слой затронут:

- `skill/SKILL.md` для trigger surface и hard guarantees;
- `skill/agents/openai.yaml` для UI metadata Codex;
- `skill/references/` для подробного поведения ролей;
- `skill/assets/templates/` для генерируемых артефактов workspace;
- `README.md` для пользовательской документации навыка;
- `AGENTS.md` для правил разработки repository.

Держите `SKILL.md` коротким и переносите подробное поведение в references. Держите templates согласованными с правилами, которые на них ссылаются.
