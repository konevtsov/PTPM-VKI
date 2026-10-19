from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistrationResult:
    success: bool
    error: str = ""

    def as_text(self) -> str:
        return "Регистрация успешна" if self.success else f"Ошибка регистрации: {self.error}"


class RegistrationValidator:
    BLACKLIST = frozenset({"admin", "administrator", "root", "support", "system"})
    SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{};':\",./<>?\\|`~"

    @staticmethod
    def _is_username(login: str) -> bool:
        return len(login) >= 5 and all(
            "a" <= char <= "z"
            or "A" <= char <= "Z"
            or "0" <= char <= "9"
            or char == "_"
            for char in login
        )

    @staticmethod
    def _is_email(login: str) -> bool:
        if login.count("@") != 1:
            return False
        name, domain = login.split("@")
        if not name or "." not in domain:
            return False
        domain_parts = domain.split(".")
        if any(not part for part in domain_parts) or len(domain_parts[-1]) < 2:
            return False
        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if not all(char in letters for char in domain_parts[-1]):
            return False
        local_allowed = letters + "0123456789._%+-"
        domain_allowed = letters + "0123456789.-"
        return all(char in local_allowed for char in name) and all(
            char in domain_allowed for char in domain
        )

    @staticmethod
    def _is_phone(login: str) -> bool:
        parts = login.split("-")
        return (
            len(parts) == 4
            and parts[0].startswith("+")
            and len(parts[0]) == 2
            and parts[0][1].isdigit()
            and len(parts[1]) == 3
            and len(parts[2]) == 3
            and len(parts[3]) == 4
            and all(part.isdigit() for part in parts[1:])
        )

    def validate(self, login: str, password: str, password_confirmation: str) -> RegistrationResult:
        if not isinstance(login, str) or not login:
            return RegistrationResult(False, "Логин не может быть пустым")
        if login.lower() in self.BLACKLIST:
            return RegistrationResult(False, "Логин запрещен")
        if not (self._is_email(login) or self._is_phone(login) or self._is_username(login)):
            return RegistrationResult(False, "Некорректный формат логина")
        if not isinstance(password, str) or len(password) < 7:
            return RegistrationResult(False, "Пароль должен содержать не менее 7 символов")
        if not all(
            "А" <= char <= "Я"
            or "а" <= char <= "я"
            or char in "Ёё"
            or char.isdigit()
            or char in self.SPECIAL_CHARACTERS
            for char in password
        ):
            return RegistrationResult(False, "Пароль содержит недопустимые символы")
        if not any("А" <= char <= "Я" or char == "Ё" for char in password):
            return RegistrationResult(False, "Пароль должен содержать заглавную кириллическую букву")
        if not any("а" <= char <= "я" or char == "ё" for char in password):
            return RegistrationResult(False, "Пароль должен содержать строчную кириллическую букву")
        if not any(char.isdigit() for char in password):
            return RegistrationResult(False, "Пароль должен содержать цифру")
        if not any(char in self.SPECIAL_CHARACTERS for char in password):
            return RegistrationResult(False, "Пароль должен содержать спецсимвол")
        if password != password_confirmation:
            return RegistrationResult(False, "Пароль и подтверждение не совпадают")
        return RegistrationResult(True)


class UserInput(ABC):
    @abstractmethod
    def get_registration_data(self) -> tuple[str, str, str]:
        ...


class ConsoleUserInput(UserInput):
    def get_registration_data(self) -> tuple[str, str, str]:
        return (input("Логин: "), input("Пароль: "), input("Подтвердите пароль: "))


class ExternalService(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        ...


class SimulatedExternalService(ExternalService):
    def __init__(self) -> None:
        self.sent_messages: list[str] = []

    def send(self, message: str) -> None:
        self.sent_messages.append(message)
