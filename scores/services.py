from typing import OrderedDict

from django.contrib.auth import get_user_model

from scores.models import Score, Reason

User = get_user_model()


def create_score(user: User, data: OrderedDict) -> None:
    data['created_by'] = user
    reason = Reason.objects.get(id=data.pop('reason_id'))
    data['name'] = reason.name
    data['points'] = reason.score
    Score.objects.create(**data)
