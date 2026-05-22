# 4DreamTeam

Языки: [English](README.md) | [Русский](README.ru.md)

4DreamTeam - это навык для Codex, который помогает превращать сырые идеи, незавершенную работу, устаревшую документацию и давление перед релизом в понятный и проверяемый workflow.

Вместо того чтобы просить одного AI-агента держать все в одном длинном чате, 4DreamTeam дает Codex небольшую команду ролей: product, analytic, developer, quality, wiki, marketing, devops и release. Работа становится видимой в файлах: epics, tasks, developer reports, quality reports, source-backed docs и release plans.

Смысл не в бюрократии. Смысл в непрерывности: можно вернуться позже, увидеть что произошло, понять что принято, и выбрать следующий безопасный шаг.

## Главное обещание

```txt
idea -> epic -> task -> implementation -> quality review -> documentation -> release
```

Главная точка входа:

```txt
$4DreamTeam
```

Не нужно запоминать имена ролей. Lead сам выбирает маршрут.

## Реальные ситуации

### Есть идея, но нет ТЗ

```txt
Я хочу систему записи для маленькой йога-студии.
Сейчас все ведется в WhatsApp, и изменения теряются.
```

4DreamTeam превращает сырую идею в epic с пользователями, объемом работ, non-goals, task candidates и acceptance criteria до того, как Codex прыгнет в код.

### Вы вернулись через неделю

```txt
Продолжи проект. Что дальше?
```

4DreamTeam читает role board, reports, wiki и optional memory, а затем предлагает следующий безопасный шаг вместо того, чтобы притворяться, что весь прошлый контекст все еще в чате.

### Нужно понять, готова ли работа

```txt
Фича реализована, но я не уверен, что она действительно готова.
```

4DreamTeam отправляет работу в `quality`, проверяет результат по acceptance criteria и сохраняет accepted или rejected quality report.

### Документация, вероятно, устарела

```txt
Приложение изменилось, а документация, скорее всего, уже неправильная.
```

4DreamTeam может проверить или синхронизировать source-backed wiki из явно approved source paths, не читая лишние файлы и не выдумывая недостающие факты.

### Нужно безопасно выпустить изменения

```txt
Подготовь принятую работу к релизу.
```

4DreamTeam проверяет accepted evidence, dirty files, changelog needs и предлагает точный staging plan до любого git commit.

## Что он делает

- Превращает продуктовую идею в scoped epic и task candidates.
- Делает из approved work технические задачи, готовые к реализации.
- Реализует scoped changes через developer workflow.
- Запускает independent quality review до приемки.
- Поддерживает source-backed project wikis с source maps и local indexes.
- Использует optional local 4DT Memory для continuity, но оставляет wiki/tasks/reports источником истины.
- Готовит README positioning, launch copy, release narratives и claim audits из confirmed sources.
- Документирует infrastructure facts и runbooks с DevOps safety gates.
- Упаковывает accepted work в changelog entries и commit plans после explicit approval.
- Улучшает сам 4DreamTeam через тот же controlled workflow.

## Роли

| Роль | Задача |
|---|---|
| `product` | Уточняет пользователей, цели, scope, non-goals и product acceptance. |
| `analytic` | Превращает intent в implementation-ready tasks с risks и checks. |
| `developer` | Реализует approved tasks и записывает developer evidence. |
| `quality` | Независимо принимает или отклоняет работу по criteria. |
| `wiki` | Создает и поддерживает source-backed project knowledge bases. |
| `marketing` | Делает source-backed public messaging и claim reviews. |
| `devops` | Документирует servers, deployments, diagnostics и operational facts. |
| `release` | Готовит changelogs, commit plans и approved git commits. |

## Почему файлы важны

4DreamTeam хранит состояние workspace в файлах:

```txt
tasks/
reports/
docs/
```

Это значит:

- решения и assumptions живут дольше одного чата;
- задачи можно продолжить без угадывания;
- developer work и quality review разделены;
- rejected work имеет понятный путь исправления;
- знания проекта хранятся в Markdown;
- release plans показывают, что будет staged, до git changes.

## Быстрый старт

Откройте новый чат и напишите: установи скилл из [Tsmar/4DreamTeam](https://github.com/Tsmar/4DreamTeam/tree/main/4dreamteam).

Перезапустите Codex и проверьте, что skill доступен:

```txt
Is the 4DreamTeam skill available?
```

Из любой папки:

```txt
Run $4DreamTeam.
```

Если папка пустая или еще не является 4DreamTeam workspace, skill сначала спросит разрешение перед созданием файлов.

## Частые команды

```txt
$4DreamTeam init workspace
$4DreamTeam status
$4DreamTeam continue
$4DreamTeam validate workspace
$4DreamTeam connect project <project-name> from <source-path>
$4DreamTeam check docs for <project-name>
$4DreamTeam search docs for <project-name> <query>
$4DreamTeam prepare release for <project-name>
$4DreamTeam improve 4DreamTeam itself from your local checkout of https://github.com/Tsmar/4DreamTeam, for example /Users/Tsmar/Projects/4DreamTeam
```

`status`, `continue` и `validate workspace` по умолчанию работают read-only. Release staging, commits, pushes, tags, deploys, migrations и destructive actions требуют explicit approval.

## Документация

Подробная документация находится в [docs/](docs/) и ведется на английском:

- [Examples](docs/examples.md) - реалистичные end-to-end ситуации.
- [Workflows](docs/workflows.md) - product, task, quality, wiki, release, DevOps, marketing и self-improvement flows.
- [Workspace](docs/workspace.md) - workspace shape, role board, reports и safety gates.
- [Wiki Index](docs/wiki-index.md) - source maps, generated indexes и source-boundary navigation.
- [4DT Memory](docs/memory.md) - local memory storage, recall, safety, degraded mode и benchmark behavior.
- [Development](docs/development.md) - структура репозитория и заметки для разработки.

## Гарантии безопасности

4DreamTeam специально устроен консервативно:

- он не обходит framework workflow, когда запрос относится к 4DreamTeam;
- он не пропускает independent quality review для implementation work;
- approved source paths считаются жесткими границами;
- secrets, credentials, `.env` contents и private keys не раскрываются;
- destructive, infrastructure, release и publication actions требуют explicit approval;
- marketing или DevOps claims не выдумываются без confirmed sources.

## Статус

Текущая документированная версия: `0.2.0`.

История изменений: [CHANGELOG.md](CHANGELOG.md).
