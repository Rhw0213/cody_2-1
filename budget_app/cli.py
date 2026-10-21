import argparse
from uuid import uuid4
from datetime import datetime

from .models import Transaction 
from .repository import TransactionRepository   
from .validators import validate_date, validate_type, validate_amout    

def add_transaction(repo: TransactionRepository) -> None:
    print("=== 거래 추가 ===")

    date = validate_date(input("날짜 (YYYY-MM-DD):"))
    transaction_type = validate_type(input("거래 유형 (income/expense):"))
    category = input("카테고리:").strip()

    if not category:
        raise ValueError("카테고리는 비워둘 수 없습니다.") 

    amount = validate_amout(input("금액:"))
    memo = input("메모 (선택 사항):")
    tags_input = input("태그 (쉼표로 구분, 선택 사항):")

    tags = [
        tag.strip()
        for tag in tags_input.split(",")
        if tag.strip()
    ]

    transaction = Transaction(
        id=f"TX-{uuid4().hex}",
        type=transaction_type,
        date=date,
        amount=amount,
        category=category,
        memo=memo,
        tags=tags
    )

    repo.add(transaction)

    print(f"[저장 완료] id={transaction.id}")

def list_transactions(repo: TransactionRepository, limit: int = None) -> None:
    if limit <= 0:
        raise ValueError("limit은 1 이상의 정수여야 합니다.")
    print("=== 거래  목록 ===")
    import heapq

    latest = heapq.nlargest(
        limit, 
        repo.get_all(), 
        key=lambda tx: (tx.date, tx.id) 
    )
    if not latest:
        print("거래 내역이 없습니다.")
        return

    for tx in latest:
        print(
            f" {tx.id} |"
            f" {tx.date} |"
            f" {tx.type} |"
            f" {tx.category} |"
            f" {tx.amount}원 |"
            f" {tx.memo} "
        )

def main() -> None:
    parser = argparse.ArgumentParser(
        description="가계부 CLI"
    )

    parser.add_argument(
        "--data-dir", 
        default="data", 
        help="데이터 디렉토리 경로 (기본값: data)"
    )

    subparsers = parser.add_subparsers(
        dest="command", 
        required=True
    )

    add_parser = subparsers.add_parser(
        "add", 
        help="거래 추가"
    )

    list_parser = subparsers.add_parser(
        "list", 
        help="거래 목록 조회"
    )

    list_parser.add_argument(
        "--limit", 
        type=int, 
        default=10, 
        help="조회할 거래 수 (기본값: 10)"
    )

    args = parser.parse_args()

    try:
        repo = TransactionRepository(args.data_dir)

        if args.command == "add":
            add_transaction(repo)
        elif args.command == "list":
            list_transactions(repo, limit=args.limit) 

    except ValueError as error:
        print(f"[오류] {error}")
        print("[힌트] 올바른 값을 입력해주세요.")
        raise SystemExit(1)

    except (OSError, EOFError, KeyboardInterrupt) as error:
        print(f"[오류] 작업을 완료하지 못했습니다: {error}")
        print("[힌트] 파일 시스템 권한을 확인하거나, 입력을 취소하지 마세요.")
        raise SystemExit(1)