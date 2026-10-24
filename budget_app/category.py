import json
from pathlib import Path

from .repository import TransactionRepository

class CategoryStore:
    def __init__(self, data_dir: str = "data") -> None:
        self.file_path = Path(data_dir) / "categories.jsonl"

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file_path.touch(exist_ok=True)

    def get_all(self) -> list[str]:
        categories = []

        with self.file_path.open(
            "r", encoding="utf-8"
        ) as file:
            for line in file:
                if line.strip():
                    data = json.loads(line)
                    categories.append(data["name"])

        return categories

    def add(self, name: str) -> None:
        name = name.strip().lower()

        if not name:
            raise ValueError("카테고리명을 입력하세요.")

        if name in self.get_all():
            raise ValueError("이미 등록된 카테고리 입니다.")

        with self.file_path.open(
            "a", encoding="utf-8"
        ) as file:
            json.dump(
                {"name": name},
                file,
                ensure_ascii=False
            )
            file.write("\n")

    def remove(
        self,
        name: str,
        repo: TransactionRepository
    ) -> None:
        name = name.strip().lower()

        categories = self.get_all()

        if name not in categories:
            raise ValueError("존재하지 않는 카테고리입니다.")

        for transaction in repo.get_all():
            if transaction.category.lower() == name:
                raise ValueError(
                    "거래 내역에서 사용 중인 카테고리는 삭제할 수 없습니다."
                )

        categories.remove(name)

        import os
        import tempfile
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir = self.file_path.parent,
                delete=False
            ) as file:
                temp_path = Path(file.name)

                for category in categories:
                    json.dump(
                        {"name": category},
                        file,
                        ensure_ascii=False
                    )

                    file.write("\n")

            os.replace(temp_path, self.file_path)

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)