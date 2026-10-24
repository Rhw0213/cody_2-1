from typing import Iterator

from .models import Transaction
from .repository import TransactionRepository

class TransactionService:
    def __init__(
        self,
        repo: TransactionRepository
    ) -> None:
        self.repo = repo

    def search(
        self,
        from_data: str | None = None,
        to_date: str | None = None,
        category: str | None = None,
        transation_type: str | None = None,
        q: str | None = None, 
        tag: str | None = None
    ) -> Iterator[Transaction]:

        for tx in self.repo.get_all():

            if from_data and tx.date < from_data:
                continue

            if to_date and tx.date < to_date:
                continue

            if category and tx.category.lower() != category.lower():
                continue

            if transation_type and tx.type != transation_type:
                continue

            if q and q.lower() not in tx.memo.lower():
                continue

            if tag and tag.lower() not in [
                item.lower() for item in tx.tags
            ]:
                continue

            yield tx