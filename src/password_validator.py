SPECIAL_CHARACTERS = frozenset("!@#$%^&*")


def validate_password(password: str) -> bool:
    if not isinstance(password, str):
        raise TypeError("Пароль должен быть строкой")
    if " " in password:
        raise ValueError("Пароль не должен содержать пробелы")

    return (
        8 <= len(password) <= 20
        and any(character.isupper() for character in password)
        and any(character.islower() for character in password)
        and any(character.isdigit() for character in password)
        and any(character in SPECIAL_CHARACTERS for character in password)
    )
