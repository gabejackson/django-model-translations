from django.db.models import ExpressionNode
from modeltranslations.joins import MultipleConstraintJoin


class ConditionalJoin(ExpressionNode):
    def join_hook(self, original_join, names, pos, query):
        return MultipleConstraintJoin(original_join, self.conditions)

    def __init__(self, path, conditions):
        self.path = path
        self.conditions = conditions
        super(ConditionalJoin, self).__init__()

    def resolve_expression(self, query, allow_joins=True, reuse=None, summarize=False):
        return query.resolve_ref(self.path, allow_joins, reuse, summarize, join_hook=self.join_hook)