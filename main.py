from controller import Controller
from registration import ConsoleUserInput, SimulatedExternalService
from registration_db import RegistrationDatabase


def main() -> None:
    with RegistrationDatabase("registrations.sqlite3") as database:
        service = SimulatedExternalService()
        controller = Controller(ConsoleUserInput(), database, service)
        print(controller.register())
        print(f"Имитация внешней отправки: {service.sent_messages[-1]}")


if __name__ == "__main__":
    main()
