# mtga-translator
Скрипт для переноса локализации клиента MTG Arena со старых версий на новые.
Создан в ответ на удаление WotC русского языка из клиента.
Может переносить не только русский язык, а любой, который когда-либо был в клиенте.
Проверено на версии `3397.845979` в качестве источника и {забыл версию, последняя на 18.11.2024} в качестве целевой.
**PR приветствуются.**
## Использование
В теории, скрипт работает на любой платформе, где работает интерпретатор CPython.
Проверено на Ubuntu 24.10 и Python 3.12
### Требуемое для запуска ПО
* Python (3.8+)
* Git (опционально)
### Запуск
```bash
git clone https://github.com/twenshin/mtga-translator.git
cd mtga-translator
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
python ./__main__.py
```

## Известные баги
- (bash/zsh) Не резолвятся пути вида `~/dir/dir/dir`.
Временное решение - писать пути полностью.
- Если создать пустой JSON-файл локализации и запустить скрипт, вылетит ошибка парсинга JSON.

## ToDo
- [x] Поддержка любых локалей (не только русской) в качестве источника
- [ ] Поддержка алиасов (в случае, если строка с локализацией переехала (поменяла ID), можно указать откуда брать перевод)
- [ ] Образ для Докера?
- [ ] Исполняемый файл для Windows?
- [ ] Предлагайте

## Принцип работы
1. Обработка файлов локализации старой версии
2. Дополнение локализации строками из кастомного перевода
3. Резервное копирование оригинального файла локализации (папка `backups` внутри папки с утилитой)
4. Замена строк в выбранной локали на нужные
<details>
  <summary>Подробности для задротов</summary>

  В версии клиента `3397.845979` файлы локализации были в формате `json` и разделены на бандлы. Пример ниже:
  ```json
  [
    {
        "key": "AbilityHanger/Color/Green",
        "bundle": "AbilityHanger",
        "description": "",
        "translations": [
        {
            "locale": "en-US",
            "translation": "green"
        },
        {
            "locale": "pt-BR",
            "translation": "de cor verde"
        },
        {
            "locale": "fr-FR",
            "translation": "vert"
        },
        {
            "locale": "it-IT",
            "translation": "verde"
        },
        {
            "locale": "de-DE",
            "translation": "grün"
        },
        {
            "locale": "es-ES",
            "translation": "verde"
        },
        {
            "locale": "ru-RU",
            "translation": "зеленый"
        },
        {
            "locale": "ja-JP",
            "translation": "緑"
        },
        {
            "locale": "ko-KR",
            "translation": "녹색"
        }
        ]
    },
  ]
  ```

  В текущей версии для локализации используется БД SQLite, содержащие единую таблицу `Loc` со следующей структурой:

  | Key                       | Bundle        | enUS  | ptBR         | frFR | itIT  | deDE | esES  | jaJP | koKR |
  |---------------------------|---------------|-------|--------------|------|-------|------|-------|------|------|
  | AbilityHanger/Color/Green | AbilityHanger | green | de cor verde | vert | verde | grün | verde | 緑   | 녹색 |

  ToDo: Дополнить структурами `CardDatabase`

</details>

## Кастомный перевод
Скрипт поддерживает дополнение локализации собственным переводом.
Для этого необходимо завести папку с двумя вложенными папками:
- `data`
- `loc`

В папке `data` может быть файл, названный `loc.json`. Пока имеет смысл только он, позже могут появиться другие.
Этот файл отвечает за обновление таблицы `CardDatabase.Localizations`.
Требуемая структура файла:
```json
{
    "{LocId}": "{RussianTranslatedString}",
    ...
}
```
Файлы папки `loc` отвечают за перевод таблицы `ClientLocalization.Loc`.
Названия файлов должны совпадать с названиями бандлов в этом файле.
Ниже описаны возможные названия файлов, взятые из бандлов текущего клиента.
- `AbilityHanger.json`
- `Binary.json`
- `Decks.json`
- `DuelScene.json`
- `Enum.json`
- `Events.json`
- `Internal.json`
- `MainNav_BattlePass.json`
- `MainNav_Carousel.json`
- `MainNav_Deck.json`
- `MainNav_Profile.json`
- `MainNav_Store.json`
- `NPE.json`
- `Quests.json`
- `Rewards.json`
- `Social.json`

Пример формата файла для перевода `ClientLocalization.Loc`:
```json
{
    "DuelScene/RuleText/TreasureSpentToCast": "Потрачено маны из сокровища: {treasureManaSpent}"
}
```

Пустые файлы лучше не держать во избежание ошибок (позже исправлю).

Далее, необходимо вооружиться любым клиентом СУБД `SQLite` (например, [https://sqlitebrowser.org/](SQLite Browser)), искать непереведённые строки в файле локализации нового клиента, переводить их и складывать в JSON-файлы в формате ключ-значение.
