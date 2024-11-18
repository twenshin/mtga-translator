import questionary

from ui.locales import locales


class Form:
    """Форма ввода данных"""

    rus_path: str = None
    latest_path: str = None
    locale_to_replace: str = None

    @classmethod
    async def ask(cls):
        locale_choices = [
            questionary.Choice(f"{k} ({v})", k) for k, v in locales.items()
        ]
        answers = await questionary.form(
            rus_path=questionary.path(
                "Укажите папку с файлами локализации в старом (русском) клиенте",
                only_directories=True,
            ),
            latest_path=questionary.path(
                "Укажите папку с последней версией клиента",
                only_directories=True,
            ),
            custom_path=questionary.path(
                "Укажите папку с кастомным переводом (формат - в README.md)",
                only_directories=True,
            ),
            locale_to_replace=questionary.select(
                "Какую локаль заменить?",
                choices=locale_choices,
            ),
            locale_source=questionary.text(
                "На какую локаль заменить?",
                instruction="""
                    Примеры:
                        ru-RU (русский)
                        zh-CN (chinese)
                    Проверьте файлы локализации (откройте текстовым редактором), 
                    чтобы проверить доступность локали.
                """,
                default="ru-RU",
            ),
        ).ask_async()

        cls.rus_path = answers["rus_path"]
        cls.latest_path = answers["latest_path"]
        cls.locale_to_replace = answers["locale_to_replace"]
        cls.locale_source = answers["locale_source"]
        cls.custom_path = answers["custom_path"]
        return cls
