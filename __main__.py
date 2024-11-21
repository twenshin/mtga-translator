import asyncio
import logging
import sys

from translator.card_database_translator import CardDatabaseTranslator
from translator.client_localization_translator import ClientLocalizationTranslator
from ui.form import Form


async def run():
    """Точка входа"""
    form: Form = await Form.ask()
    kwargs = {
        "loc_path": form.rus_path,
        "target_path": form.latest_path,
        "locale_to_replace": form.locale_to_replace,
        "locale_source": form.locale_source,
        "custom_path": form.custom_path,
    }
    client_localization_translator = ClientLocalizationTranslator(**kwargs)
    await client_localization_translator.translate()
    logging.info(
        f"Локализация клиента готова! Обработано {client_localization_translator.processed_count} строк из {client_localization_translator.total_count}"
    )
    card_database_translator = CardDatabaseTranslator(**kwargs)
    await card_database_translator.translate()
    logging.info(
        f"Локализация карт готова! Обработано {card_database_translator.processed_count} строк из {card_database_translator.total_count}"
    )


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    root.addHandler(handler)

    asyncio.run(run())
