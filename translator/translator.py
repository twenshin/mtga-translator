import os
import shutil


class TranslateResult:
    """Результат перевода"""

    rows_updated = 0
    rows_kept = 0

    def __init__(self, rows_updated, rows_remaining) -> None:
        self.rows_updated = rows_updated
        self.rows_remaining = rows_remaining


class Translator:
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
        self.loc_path = loc_path
        self.target_path = target_path
        self.custom_path = custom_path
        self.locale_to_replace = locale_to_replace
        self.locale_source = locale_source

        # Для статистики
        self.total_count = 0
        self.processed_count = 0

    async def translate(self) -> None:
        raise NotImplementedError()

    @staticmethod
    def backup(source_path):
        """Делает резервную копию файла с локализацией
        в папке {папка со скриптом}/backups
        :param source_path: Путь к файлу с локализацией
        """
        target_path = os.path.join(os.getcwd(), "backups")
        os.makedirs(target_path, exist_ok=True)
        target_filename = os.path.basename(source_path)
        shutil.copy(
            source_path,
            os.path.join(target_path, target_filename),
        )
