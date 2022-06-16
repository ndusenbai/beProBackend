from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


def change_password(user: User, validated_data: dict) -> None:
    if user.check_password(validated_data.get('old_password')):
        user.set_password(validated_data.get('new_password'))
        user.save()
    else:
        raise serializers.ValidationError('Old password incorrect', code='incorrect_old')


def send_created_account_notification(user: User) -> None:
    # TODO: set mail hosting
    pass
