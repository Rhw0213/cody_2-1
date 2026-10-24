import argparse
from uuid import uuid4
from datetime import datetime

from .category import CategoryStore
from .models import Transaction 
from .repository import TransactionRepository   
from .validators import validate_date, validate_type, validate_amout    
from .service import TransactionService

def add_transaction(repo: TransactionRepository) -> None:
    print("=== 거래 추가 ===")

    date = validate_date(input("날짜 (YYYY-MM-DD):"))
    transaction_type = validate_type(input("거래 유형 (income/expense):"))

    category_store = CategoryStore(
        str(repo.data_dir)
    )

    category = input("카테고리: ").strip().lower()

    if category not in category_store.get_all():
        raise ValueError(
            "등록되지 않은 카테고리입니다. "
            "category add 명령어로 먼저 등록하세요."
        )

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

def search_transactions(
    repo: TransactionRepository,
    args: argparse.Namespace
) -> None:

    if args.from_date:
        validate_date(args.from_date)

    if args.to_date:
        validate_date(args.to_date)

    if(
        args.from_date
        and args.to_date
        and args.from_date > args.to_date
    ):
        raise ValueError(
            "시작 날짜는 종료 날짜보다 늦을 수 없습니다."
        )

    service = TransactionService(repo)

    results = service.search(
        from_data=args.from_date,
        to_date=args.to_date,
        category=args.category,
        transation_type=args.transaction_type,
        q=args.q,
        tag=args.tag
    )

    batch_size = 100

    latest = heapq.nlargest(
        batch_size,
        results,
        key=lambda tx: (tx.date, tx.id)
    )

    if not latest:
        print("검색 결과가 없습니다.")
        return

    for tx in latest:
        print(
            f"{tx.id} | "
            f"{tx.date} | "
            f"{tx.type} | "
            f"{tx.category} | "
            f"{tx.amount}원 | "
            f"{tx.memo} | "
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

    category_parser = subparsers.add_parser(
        "category",
        help="카테고리 관리"
    )

    category_subparsers = category_parser.add_subparsers(
        dest="category_command",
        required=True
    )

    category_subparsers.add_parser(
        "add",
        help="카테고리 추가"
    )

    category_subparsers.add_parser(
        "list",
        help="카테고리 목록"
    )

    category_subparsers.add_parser(
        "remove",
        help="카테고리 삭제"
    )

    search_parser = subparsers.add_parser(
        "search",
        help="거래 검색"
    )

    search_parser.add_argument("--from", dest="from_date")
    search_parser.add_argument("--to", dest="to_date")
    search_parser.add_argument("--category")
    search_parser.add_argument(
        "--type", 
        dest="transation_type",
        choices=["income", "expense"]
    )
    search_parser.add_argument("--q")
    search_parser.add_argument("--tag")


    args = parser.parse_args()

    try:
        repo = TransactionRepository(args.data_dir)

        if args.command == "add":
            add_transaction(repo)
        elif args.command == "list":
            list_transactions(repo, limit=args.limit) 
        elif args.command == "category":
            store = CategoryStore(args.data_dir)

            if args.category_command == "add":
                name = input("카테고리명: ")
                store.add(name)
                print(f"[저장 완료] category={name.strip().lower()}")
            elif args.category_command == "list":
                categories = store.get_all()

                if not categories:
                    print("등록된 카테고리가 없습니다.")

                for name in categories:
                    print(f"- {name}")
            elif args.category_command == "remove":
                name = input("삭제할 카테고리 명: ")
                store.remove(name, repo)
                print(f"[삭제 완료] category={name.strip().lower()}")
        elif args.command == "search":
            search_transactions(repo, args)    
                

    except ValueError as error:
        print(f"[오류] {error}")
        print("[힌트] 올바른 값을 입력해주세요.")
        raise SystemExit(1)

    except (OSError, EOFError, KeyboardInterrupt) as error:
        print(f"[오류] 작업을 완료하지 못했습니다: {error}")
        print("[힌트] 파일 시스템 권한을 확인하거나, 입력을 취소하지 마세요.")
        raise SystemExit(1)