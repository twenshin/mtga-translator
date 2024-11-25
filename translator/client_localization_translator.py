import os

from sqlalchemy import func, select, update
from sqlalchemy.exc import NoResultFound

from db.models import ClientLocalizationModel as LocalizationModel
from db.utils import session_factory
from translator.translator import Translator
from utils import (
    find_localization_file,
    open_custom_localization_file,
    open_localization_file,
    prepare_localization,
)


class ClientLocalizationTranslator(Translator):
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
        loc_path = os.path.join(loc_path, "loc")
        if custom_path:
            custom_path = os.path.join(custom_path, "loc")

        super().__init__(
            loc_path, target_path, custom_path, locale_to_replace, locale_source
        )

        self.target_db_filename = find_localization_file(
            self.target_path,
            "Raw_ClientLocalization_",
        )
        self.session_factory = session_factory(self.target_db_filename)

    async def translate(self) -> None:
        self.backup(self.target_db_filename)
        bundles = [
            "AbilityHanger",
            "Binary",
            "Decks",
            "DuelScene",
            "Enum",
            "Events",
            "Internal",
            "MainNav_BattlePass",
            "MainNav_Carousel",
            "MainNav_Deck",
            "MainNav_Profile",
            "MainNav_Store",
            "NPE",
            "Quests",
            "Rewards",
            "Social",
        ]

        for bundle in bundles:
            await self._translate_bundle(bundle)

    async def _translate_bundle(self, bundle):
        query_batch = []
        raw_localization = open_localization_file(self.loc_path, f"loc_{bundle}")
        localization = prepare_localization(raw_localization, self.locale_source)
        if self.custom_path:
            custom_localization = open_custom_localization_file(
                self.custom_path, bundle
            )
            localization.update(custom_localization)

        # Старый стиль - ru-RU, новый - ruRU
        new_style_locale = self.locale_to_replace.replace("-", "")

        session = self.session_factory()
        total_count_query = await session.execute(
            select(func.count()).select_from(LocalizationModel)
        )
        self.total_count = total_count_query.scalars().one()
        for key, translation in localization.items():
            """Новые версии переводов вычищаются, поэтому некоторых
            строк в последней версии может не быть.
            SQLAlchemy ругается на попытки обновления несуществующих ключей,
            поэтому введена проверка на существование ключа в БД.
            """
            check = await session.execute(
                select(LocalizationModel).where(LocalizationModel.Key == key)
            )
            try:
                check.scalars().one()
            except NoResultFound:
                continue

            query_batch.append({"Key": key, new_style_locale: translation})
            self.processed_count += 1

        await session.execute(
            update(LocalizationModel),
            query_batch,
        )
        await session.commit()
