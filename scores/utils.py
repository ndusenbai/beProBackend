from django.db.models import Aggregate, IntegerField


class GetScoreForRole(Aggregate):
    function = 'get_score_for_role'
    template = "%(function)s(%(my_role_id)s)"
    output_field = IntegerField()

    def __init__(self, my_role_id):
        super().__init__(my_role_id=my_role_id)
