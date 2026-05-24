# 4DreamTeam

Языки: [English](README.md) | [Русский](README.ru.md)

4DreamTeam - это волшебная палочка для тех, кто хочет работать с реальными проектами с AI-суперсилами, но не хочет превращать каждый проект в один бесконечный хрупкий чат.

Скажите Codex, что вы хотите построить, исправить, проверить, задокументировать или выпустить. 4DreamTeam превращает этот запрос в маленькую рабочую команду: product думает о цели, analytic формирует задачу, developer меняет код, quality проверяет результат, wiki хранит память проекта, а release помогает безопасно довести изменения до выпуска.

Вы приносите идею, хаос, недоделанную фичу или ощущение "а это вообще правда готово?". 4DreamTeam дает работе маршрут, записывает что произошло, поддерживает документацию живой и спрашивает перед опасными действиями.

## Когда Это Полезно

- У вас есть идея, но нет ТЗ.
- Вы открыли старый проект и забыли, что дальше.
- Вы хотите, чтобы Codex изменил код, но еще хотите отдельную проверку, действительно ли работа готова.
- Документация устарела, и ей уже никто не доверяет.
- Вы близко к релизу и хотите чистый план до любых действий с git.
- Вы хотите AI-помощь, которая ощущается не как один перегруженный чат, а как аккуратная проектная команда.

## Простое Обещание

```txt
idea -> plan -> implementation -> quality -> wiki -> release
```

4DreamTeam не заставляет запоминать процесс. Вы начинаете с:

```txt
$4DreamTeam
```

Lead сам направляет работу к нужной роли и держит следующий шаг видимым.

## Почему Это Ощущается Иначе

### У Codex появляется проектная память

Работа живет не только в прокрутке чата. 4DreamTeam хранит tasks, decisions, reports, quality results, docs и release plans в workspace, чтобы проект можно было продолжить позже.

### Выполнение отделено от проверки

Роль developer реализует scoped work. Роль quality независимо принимает или отклоняет результат по задаче. Так "готово" меньше зависит от ощущения на глаз.

### Документация остается рядом с реальностью

Роль wiki поддерживает source-backed project knowledge base. Подробную документацию можно экспортировать в `docs/` через `4dt-wiki export`, поэтому README остается простым, а проектная документация - полезной.

### Управление остается у вас

4DreamTeam спрашивает перед рискованными переходами, file writes, release steps, infrastructure changes, destructive commands, commits, pushes, tags и publication. Можно двигаться быстро, не отдавая руль.

## Реальные Ситуации

### "Есть идея, но нет ТЗ."

```txt
Я хочу систему записи для маленькой йога-студии.
Сейчас все ведется в WhatsApp, и изменения теряются.
```

4DreamTeam превращает идею в users, goals, scope, non-goals, task candidates и acceptance criteria до того, как Codex прыгнет в код.

### "Я вернулся через неделю."

```txt
Продолжи проект. Что дальше?
```

4DreamTeam читает board, timeline evidence, wiki и memory, когда она доступна, а затем говорит следующий безопасный шаг.

### "Нужно понять, правда ли это готово."

```txt
Фича реализована, но я не уверен, что она действительно готова.
```

4DreamTeam отправляет работу в quality, проверяет ее по acceptance criteria и сохраняет accepted или rejected result.

### "Документация, наверное, устарела."

```txt
Приложение изменилось, а документация, скорее всего, уже неправильная.
```

4DreamTeam может audit, sync, deepen и export source-backed docs, не читая лишние файлы и не выдумывая недостающие факты.

### "Нужно выпустить без хаоса."

```txt
Подготовь принятую работу к релизу.
```

4DreamTeam проверяет accepted evidence, смотрит changed files, обновляет release documentation когда нужно и предлагает точный план до любых git actions.

## Что Вы Получаете

- Product shaping для сырых идей.
- Technical task planning перед реализацией.
- Developer work с видимыми evidence.
- Independent quality review.
- Source-backed project wiki.
- Экспортированную документацию в `docs/`.
- README positioning, launch copy, release narratives и claim audits.
- DevOps notes и runbooks с safety gates.
- Release plans и changelog preparation после explicit approval.
- Способ улучшать сам 4DreamTeam через тот же controlled workflow.

## Быстрый Старт

Установите пакет скила `4dreamteam/` из [Tsmar/4DreamTeam](https://github.com/Tsmar/4DreamTeam/tree/main/4dreamteam).

Перезапустите Codex, затем спросите:

```txt
Is the 4DreamTeam skill available?
```

Из любой папки проекта:

```txt
Run $4DreamTeam.
```

Если папка еще не является 4DreamTeam workspace, 4DreamTeam спросит перед созданием workspace-файлов.

### Работа С Существующим Проектом

Сложная настройка не нужна. Создайте чистую папку для 4DreamTeam workspace, положите репозиторий проекта внутрь `sources/`, затем запустите `$4DreamTeam`.

```txt
my-4dt-workspace/
  sources/
    your-project/
```

После инициализации 4DreamTeam может построить project knowledge base из approved source folder, и вы готовы работать: попросите его понять проект, спланировать изменения, проверить работу, обновить документацию или подготовить принятый релиз.

## Полезные Запросы

```txt
$4DreamTeam status
$4DreamTeam continue
$4DreamTeam validate workspace
$4DreamTeam turn this idea into a plan
$4DreamTeam check whether this feature is really done
$4DreamTeam update the project docs from source
$4DreamTeam prepare this accepted work for release
```

Read-only status и validation безопасны по умолчанию. Release staging, commits, pushes, tags, deployments, migrations и destructive actions требуют explicit approval.

## Документация

Этот README - landing page. Он объясняет, почему стоит попробовать 4DreamTeam.

Подробная документация живет в [docs/](docs/) и экспортируется из managed 4DreamTeam wiki:

- [Workspace Overview](docs/overview.md)
- [Product Overview](docs/product/overview.md)
- [Task Lifecycle Flow](docs/flows/task-lifecycle.md)
- [Wiki Workflow](docs/flows/wiki-workflow.md)
- [Workspace Tools Contract](docs/contracts/workspace-tools.md)
- [Source Boundaries Domain](docs/domains/source-boundaries.md)

## Безопасность Простыми Словами

4DreamTeam устроен так, чтобы быть полезным без лишней безрассудности:

- он не пропускает quality review для implementation work;
- approved source paths считаются жесткими границами;
- он не раскрывает `.env` files, secrets, credentials или private keys;
- он спрашивает перед risky file writes, infrastructure changes, release actions и publication;
- он не выдумывает marketing, DevOps или security claims без confirmed sources.

## Статус

Текущая документированная версия: `0.5.1`.

История изменений: [CHANGELOG.md](CHANGELOG.md).
