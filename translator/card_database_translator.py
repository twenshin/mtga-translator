import logging
import os

from sqlalchemy import func, select, update
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.exc import NoResultFound

from db.models import CardLocalizationModel
from db.utils import session_factory
from translator.translator import Translator
from utils import (
    find_localization_file,
    open_custom_localization_file,
    open_localization_file,
    prepare_data,
)


class CardDatabaseTranslator(Translator):
    def __init__(
        self,
        loc_path: os.PathLike,
        target_path: os.PathLike,
        custom_path: os.PathLike,
        locale_to_replace: str,
        locale_source: str,
    ) -> None:
        """Механизм перевода клиента
        :param loc_path: Путь к файлам локализации старого (русского) клиента
        :param target_path: Путь к файлам локализации нового клиента (без русского языка)
        :param custom_path: Путь к кастомной локализации
        :param locale_to_replace: Заменяемая локаль
        :param locale_source: Какой локалью необходимо заменить
        """
        loc_path = os.path.join(loc_path, "data")
        if custom_path:
            custom_path = os.path.join(custom_path, "data")

        super().__init__(
            loc_path, target_path, custom_path, locale_to_replace, locale_source
        )

        self.target_db_filename = find_localization_file(
            self.target_path,
            "Raw_CardDatabase_",
        )
        self.session_factory = session_factory(self.target_db_filename)

    async def translate(self) -> None:
        tables = [
            # Некоторые не нужно переводить (Cards, Versions, Enums)
            # Некоторые - неизвестно, стоит ли (SearchLocalizations)
            # ("SearchLocalizations", "loc"),
            # "Versions",
            # ("Cards", "cards"),
            # ("Abilities", "abilities"),
            # ("Enums", "enums"),
            # ("Prompts", "prompts"),
            ("Localizations", "loc"),
        ]

        for table in tables:
            await self._translate_table(*table)

    async def _translate_table(
        self, _, old_style_file
    ):  # FIXME: Может, убрать названия таблиц нового клиента?
        query_batch = []
        raw_localization = open_localization_file(
            self.loc_path, f"data_{old_style_file}"
        )
        localization = prepare_data(raw_localization, self.locale_source)
        if self.custom_path:
            custom_localization = open_custom_localization_file(
                self.custom_path, old_style_file
            )
            localization.update(custom_localization)

        # Старый стиль - ru-RU, новый - ruRU
        new_style_locale = self.locale_to_replace.replace("-", "")

        session = self.session_factory()
        total_count_query = await session.execute(
            select(func.count()).select_from(CardLocalizationModel)
        )
        self.total_count = total_count_query.scalars().one()
        for loc_id, translation in localization.items():
            """Новые версии переводов вычищаются, поэтому некоторых
            строк в последней версии может не быть.
            SQLAlchemy ругается на попытки обновления несуществующих ключей,
            поэтому введена проверка на существование ключа в БД.
            """

            """ FIXME: WARNING!!! WARNING!!! WARNING!!!
            Необходимо отыскать аналог поля Formatted в старом клиенте
            и перепилить эту часть кода чтобы формат учитывался.
            В новом клиенте текст разных форматов отличается форматированием
            и переносом (и запретом переноса) строк.
            В плохом случае, с текущим алгоритмом, когда Formatted откидывается,
            поедет текст в игре.
            Пример:
            (LocId=276, Formatted=0) Target specified for out-of-range target index.
            (LocId=276, Formatted=1) Target specified for <nobr>out-of</nobr>-range target index.
            (LocId=276, Formatted=2) Target specified for out-of-range target index.
            """
            if translation == "#NoTranslationNeeded":
                continue

            to_update_cur: ChunkedIteratorResult = await session.execute(
                select(CardLocalizationModel).where(
                    CardLocalizationModel.LocId == loc_id
                )
            )
            for loc in to_update_cur.scalars():
                logging.debug(f"{getattr(loc, new_style_locale)} -> {translation}")
                query_batch.append(
                    {
                        "LocId": loc.LocId,
                        "Formatted": loc.Formatted,
                        new_style_locale: translation,
                    }
                )
                self.processed_count += 1

        await session.execute(
            update(CardLocalizationModel),
            query_batch,
        )
        await session.commit()
