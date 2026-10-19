import unittest
from unittest.mock import Mock, patch

from controller import Controller
from registration import (
    ExternalService,
    RegistrationResult,
    RegistrationValidator,
    UserInput,
)
from registration_db import RegistrationDatabase


class TestRegistrationValidator(unittest.TestCase):
    def setUp(self):
        self.validator = RegistrationValidator()

    def test_accepts_username_email_and_phone(self):
        for login in ("valid_user7", "person@example.com", "+7-999-123-4567"):
            with self.subTest(login=login):
                self.assertEqual(self.validator.validate(login, "Пароль1!", "Пароль1!"), RegistrationResult(True))

    def test_rejects_blacklisted_login(self):
        self.assertEqual(self.validator.validate("ADMIN", "Пароль1!", "Пароль1!").error, "Логин запрещен")

    def test_rejects_password_without_required_character_groups(self):
        self.assertIn("заглавную", self.validator.validate("valid_user", "пароль1!", "пароль1!").error)
        self.assertIn("цифру", self.validator.validate("valid_user", "Пароль!!", "Пароль!!").error)


class TestRegistrationIntegration(unittest.TestCase):
    def setUp(self):
        self.database = RegistrationDatabase()
        self.input = Mock(spec=UserInput)
        self.external = Mock(spec=ExternalService)
        self.controller = Controller(self.input, self.database, self.external)

    def tearDown(self):
        self.database.close()

    def test_registers_valid_user_persists_and_sends_result(self):
        self.input.get_registration_data.return_value = ("valid_user", "Пароль1!", "Пароль1!")
        text = self.controller.register()
        self.assertEqual(text, "Регистрация успешна")
        self.assertEqual(self.database.get("valid_user", "Пароль1!", "Пароль1!"), RegistrationResult(True))
        self.external.send.assert_called_once_with(text)

    def test_reuses_database_result_without_revalidating(self):
        self.input.get_registration_data.return_value = ("bad", "bad", "different")
        stored = RegistrationResult(False, "Сохраненная ошибка")
        self.database.add("bad", "bad", "different", stored)
        with patch.object(self.controller.validator, "validate", side_effect=AssertionError("cache miss")):
            text = self.controller.register()
        self.assertEqual(text, "Ошибка регистрации: Сохраненная ошибка")
        self.external.send.assert_called_once_with(text)

    def test_invalid_registration_is_stored_and_failure_is_sent(self):
        data = ("x", "short", "short")
        self.input.get_registration_data.return_value = data
        text = self.controller.register()
        saved = self.database.get(*data)
        self.assertIsNotNone(saved)
        if saved is None:
            self.fail("Запись регистрации должна быть сохранена")
        self.assertFalse(saved.success)
        self.assertEqual(text, f"Ошибка регистрации: {saved.error}")
        self.external.send.assert_called_once_with(text)

    def test_database_delete_reports_whether_a_record_existed(self):
        data = ("valid_user", "Пароль1!", "Пароль1!")
        self.database.add(*data, RegistrationResult(True))
        self.assertTrue(self.database.delete(*data))
        self.assertFalse(self.database.delete(*data))
        self.assertIsNone(self.database.get(*data))


if __name__ == "__main__":
    unittest.main()
