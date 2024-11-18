# mtga-translator
Утилита для переноса локализации клиента MTG Arena со старых версий на новые.  
Создана в ответ на удаление WotC русского языка из клиента.  
Может переносить не только русский язык, а любой, который когда-либо был в клиенте.  
Проверено на версии `3397.845979` в качестве источника и {забыл версию, последняя на 18.11.2024} в качестве целевой.  
**PR приветствуются.** 
## Использование
В теории, утилита работает на любой платформе, где работает интерпретатор CPython.  
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

## ToDo
- [x] Поддержка любых локалей (не только русской) в качестве источника  
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

</details>

## Кастомный перевод
Утилита поддерживает дополнение локализации собственным переводом.  
Для этого необходимо завести папку с json-файлами, названными как бандлы:
- `AbilityHanger`
- `Binary`
- `Decks`
- `DuelScene`
- `Enum`
- `Events`
- `Internal`
- `MainNav_BattlePass`
- `MainNav_Carousel`
- `MainNav_Deck`
- `MainNav_Profile`
- `MainNav_Store`
- `NPE`
- `Quests`
- `Rewards`
- `Social`