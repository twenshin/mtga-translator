import logging
import os
from glob import glob
from typing import List

import orjson as json


def find_localization_file(directory: os.PathLike, prefix: str) -> str:
    """Находит файл локализации по префиксу"""
    candidates = glob(f"{directory}/{prefix}*.mtga")
    if not candidates:
        raise FileNotFoundError("File not found")

    return candidates[0]


def open_localization_file(directory: os.PathLike, prefix: str) -> List[dict]:
    """Находит по префиксу и открывает файл локализации
    :param directory: Папка для поиска
    :param prefix: Префикс для поиска
    :returns: Содержимое файла локализации
    """
    target = find_localization_file(directory, prefix)
    with open(os.path.join(directory, target), "rb") as fp:
        return json.loads(fp.read().decode("utf-8"))


def prepare_localization(localization: List[dict], locale: str) -> dict:
    """Преобразует структуру файла локализации в формат:
    ```
    {
        "{key}": "{russian_translation}",
        ...
    }
    ```
    :param localization: Открытый файл с локализацией (см. utils.open_localization_file)
    :returns: Словарь, где ключ - ключ строки, а значение - строка на русском языке.
    """
    result = {}
    for entity in localization:
        key = entity["key"]
        translated_string = next(
            x["translation"] for x in entity["translations"] if x["locale"] == locale
        )
        result[key] = translated_string

    return result

def prepare_data(localization: List[dict], source_locale: str) -> dict:
    needed_loc = next(x["keys"] for x in localization if x["isoCode"] == source_locale)
    if not needed_loc:
        raise ValueError()

    return {x["id"]: x["text"] for x in needed_loc}



def open_custom_localization_file(bundle_path: os.PathLike, bundle: str) -> dict:
    """Открывает файл с кастомной локализацией
    В отличие от официальных файлов локализации, здесь используется конкретный
    формат файлов, поэтому поиск не требуется.
    :param bundle: Тип бандла локализации
    :returns: Словарь с ключом локализации в роли ключа
    и русской переведённой строкой в роли значения
    """
    bundle_file_path = os.path.join(bundle_path, f"{bundle}.json")
    try:
        with open(bundle_file_path, "r") as fp:
            return json.loads(fp.read())

    except FileNotFoundError:
        logging.warning(
            f"Файл с бандлом {bundle} не был найден по адресу {bundle_file_path}. Он будет пропущен."
        )
        return {}
