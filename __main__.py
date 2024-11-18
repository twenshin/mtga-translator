import asyncio
import logging
import sys

from translator.translator import Translator
from ui.form import Form


async def run():
    """Точка входа"""
    form: Form = await Form.ask()
    translator = Translator(
        loc_path=form.rus_path,
        target_path=form.latest_path,
        locale_to_replace=form.locale_to_replace,
        locale_source=form.locale_source,
        custom_path=form.custom_path,
    )
    await translator.translate()
    logging.info(
        f"Готово! Обработано {translator.processed_count} строк из {translator.total_count}"
    )


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    root.addHandler(handler)

    asyncio.run(run())
