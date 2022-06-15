from django.contrib.auth import get_user_model

User = get_user_model()


def send_created_account_notification(user: User) -> None:
    # TODO: set mail hosting
    pass
