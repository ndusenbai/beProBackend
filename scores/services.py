from typing import OrderedDict

from django.contrib.auth import get_user_model

from auth_user.services import get_user_role
from scores.models import Score, Reason
from companies.models import Company

User = get_user_model()


def create_score(user: User, data: OrderedDict) -> None:
    data['created_by'] = user
    reason = Reason.objects.get(id=data.pop('reason_id'))
    data['name'] = reason.name
    data['points'] = reason.score
    Score.objects.create(**data)


def get_score_feed(request):
    user = request.user
    company = request.GET.get('company', None)
    extra_kwargs = {}
    role = get_user_role(user)

    if company:
        if role == 'owner':
            extra_kwargs['role__company'] = company
        elif role in ('observer', 'hr', 'head_of_hr_department'):
            extra_kwargs['role__company'] = company
        elif role in ('employee', 'head_of_department'):
            extra_kwargs['role__company'] = company
            extra_kwargs['role__grade__lte'] = user.role.grade
    else:
        if role == 'owner':
            extra_kwargs['role__company__in'] = user.owned_companies.all()
        elif role in ('observer', 'hr', 'head_of_hr_department'):
            extra_kwargs['role__company'] = user.role.company
        elif role in ('employee', 'head_of_department'):
            extra_kwargs['role__company'] = user.role.company
            extra_kwargs['role__grade__lte'] = user.role.grade

    return Score.objects.select_related(
        'role',
        'role__user'
    ).filter(**extra_kwargs).order_by('-created_at')
