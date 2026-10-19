from registration import ExternalService, RegistrationValidator, UserInput
from registration_db import RegistrationDatabase


class Controller:
    def __init__(
        self,
        user_input: UserInput,
        database: RegistrationDatabase,
        external_service: ExternalService,
        validator: RegistrationValidator | None = None,
    ) -> None:
        self.user_input = user_input
        self.database = database
        self.external_service = external_service
        self.validator = validator or RegistrationValidator()

    def register(self) -> str:
        login, password, confirmation = self.user_input.get_registration_data()
        result = self.database.get(login, password, confirmation)
        if result is None:
            result = self.validator.validate(login, password, confirmation)
            self.database.add(login, password, confirmation, result)
        message = result.as_text()
        self.external_service.send(message)
        return message
