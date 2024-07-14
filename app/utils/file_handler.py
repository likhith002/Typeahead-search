import os
import logging

FILE_NAME = "text.txt"

log = logging.getLogger(__name__)


def get_file_path() -> str:
    current_dir = os.path.dirname(__file__)

    root_dir = os.path.dirname(current_dir)

    static_dir = os.path.join(root_dir, "static")
    return os.path.join(static_dir, FILE_NAME)


def check_file_exists(file_path: str) -> bool:
    return os.path.isfile(file_path)


def create_file(file_path: str) -> None:
    try:
        open(file_path, "w").close()
    except Exception as e:
        print(e)


def write_data_to_file(data: str, file_path: str) -> None:
    with open(file_path, "a") as file:
        file.write(data + " ")
        file.close()


def write_to_file(q: str) -> None:
    try:
        file_path = get_file_path()
        if check_file_exists(file_path):
            print(f"File '{file_path}' is present")

        else:
            create_file(file_path)
            print(f"File '{file_path}' created successfully")
        write_data_to_file(q, file_path)
    except Exception as e:
        log.error(e)
