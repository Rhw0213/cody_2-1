import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterator

from .models import Transaction

class TransactionRepository:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.file_path = self.data_dir / "transactions.jsonl"
        self.file_path.touch(exist_ok=True)

    def add(self, transaction: Transaction) -> None:
        with self.file_path.open("a", encoding="utf-8") as file:
            json.dump(asdict(transaction), file, ensure_ascii=False)
            file.write("\n")  

    def get_all(self) -> Iterator[Transaction]:
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    data = json.loads(line)
                    yield Transaction(**data)