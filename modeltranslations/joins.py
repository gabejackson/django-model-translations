from django.db.models import QuerySet
from django.db.models.sql.datastructures import Join


class MultipleConstraintJoin(Join):
    def __init__(self, original_join, conditions):
        self.__dict__ = original_join.__dict__
        self.conditions = conditions

    def get_extra_cond(self, compiler):
        qs = QuerySet(self.join_field.to).filter(self.conditions)
        where_node = qs.query.where
        where_node.relabel_aliases({self.table_name: self.table_alias})
        sql, params = compiler.compile(where_node)
        sql = ' AND %s' % sql
        return sql, params

    def __eq__(self, other):
        if super(MultipleConstraintJoin, self).__eq__(other):
            return str(self.conditions) == str(other.conditions)
        return False