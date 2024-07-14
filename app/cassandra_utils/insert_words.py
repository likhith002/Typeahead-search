import os


from app.schemas.response import CustomException
from typing import Dict
from uuid import uuid4
from cassandra.cqlengine.query import BatchQuery, BatchStatement
from cassandra.cluster import Session


def get_output_file_paths(folder_path: str) -> list[str]:
    if not os.path.exists(folder_path):
        raise CustomException(
            detail=f"folder of name {folder_path} is not found",
            title="Unable to process outputs to cassandra",
        )

    file_paths: list[str] = []
    for filename in os.listdir(folder_path):
        if filename.startswith("part-r"):
            file_paths.append(os.path.join(folder_path, filename))

    return file_paths


def parse_chunk(words: Dict[str, int], chunk: str) -> Dict[str, int]:
    lines = chunk.split("\n")

    for line in lines:
        count_list = line.split("\t")
        if len(count_list) == 2:
            words[count_list[0]] = count_list[1]

    return words


def batch_insert_words(session: Session, words: Dict[str, int]):
    data_to_insert = [
        {"id": uuid4(), "word": word, "count": int(count)}
        for word, count in words.items()
    ]
    # Prepare batch statement
    batch = BatchStatement()

    insert_statement = session.prepare("""
        INSERT INTO word_count (id, word, count)
        VALUES (?, ?, ?)
    """)

    # Add insert operations to the batch
    for data in data_to_insert:
        batch.add(insert_statement, (data.values()))

    # Execute the batch insert
    session.execute(batch)


async def insert(session: Session, folder_path: str) -> None:
    chunk_size = 500
    file_paths = get_output_file_paths(folder_path)
    print(file_paths)
    for file_path in file_paths:
        with open(file_path, "r") as file:
            while True:
                words: Dict[str, int] = {}
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                parse_chunk(words, chunk)
                batch_insert_words(session, words)

    print("DONE")


# if __name__ == "__main__":
#     parent_path = os.getcwd()
#     folder_path = os.path.join(parent_path, "app", "static", "outputs")
#     insert(folder_path)
