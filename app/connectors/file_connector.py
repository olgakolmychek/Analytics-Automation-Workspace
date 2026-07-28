from pathlib import Path


def get_latest_file(folder_path):
    """
    Находит самый новый файл в папке.
    """

    folder = Path(folder_path)

    files = list(folder.glob("*.xlsx"))

    if not files:
        raise FileNotFoundError("Excel файлы не найдены")

    latest_file = max(
        files,
        key=lambda file: file.stat().st_mtime
    )

    return latest_file