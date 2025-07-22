""""Вспомогательные функции."""


def get_days_string(days):
    """Возвращает строку с днями по правилам русского языка."""
    if 11 <= days % 100 <= 14:
        return f'{days} дней'
    last_digit = days % 10
    if last_digit == 1:
        return f'{days} день'
    elif 2 <= last_digit <= 4:
        return f'{days} дня'
    else:
        return f'{days} дней'