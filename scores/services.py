from typing import OrderedDict

from django.contrib.auth import get_user_model

from scores.models import Score

User = get_user_model()


def create_score(user: User, data: OrderedDict) -> None:
    data['created_by'] = user
    Score.objects.create(**data)
