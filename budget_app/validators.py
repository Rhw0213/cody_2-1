from datetime import datetime

def validate_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")

        if len(value) != 10:
            raise ValueError        

        return value
    except ValueError:
        raise ValueError("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.")

def validate_type(value: str) -> str:
    if value not in ("income", "expense"):
        raise ValueError("거래 유형은 'income' 또는 'expense'이어야 합니다.")

    return value

def validate_amout(value: str) -> int:
    try:
        amount = int(value)
    except ValueError:
        raise ValueError("금액은 정수여야 합니다.")

    if amount <= 0:
        raise ValueError("금액은 양의 정수여야 합니다.")

    return amount