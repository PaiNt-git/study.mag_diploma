
import sqlalchemy as sa

from sqlalchemy import cast

from sqlalchemy_searchable import search, parse_search_query, search_manager

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.sqltypes import Float, Numeric
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import or_


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def main(user_search_term, category=None, sort=False, only_questions=True):

    session = Session()

    query = session.query(QuestAnswerBase.id,
                          QuestAnswerBase.questions,
                          QuestAnswerBase.abstract,
                          )

    if category:
        query = query.filter(QuestAnswerBase.category == category)

    # Если не в фигурных скобках то поиск полнотектовый
    if user_search_term and user_search_term[0] != '{' and user_search_term[-1] != '}':

        vector = QuestAnswerBase.search_vector.property.columns[0]
        if only_questions:
            vector = QuestAnswerBase.q_search_vector.property.columns[0]

        options = vector.type.options
        regconfig = options['regconfig']

        kwargs = {}
        if regconfig is not None:
            kwargs['postgresql_regconfig'] = regconfig
        else:
            if 'regconfig' not in vector.type.options:
                kwargs['postgresql_regconfig'] = (
                    search_manager.options['regconfig']
                )

        search_query = parse_search_query(user_search_term)

        sort_rank = sa.func.ts_rank_cd(
            vector,
            sa.func.to_tsquery(kwargs['postgresql_regconfig'], search_query),
            16 | 1,  # https://www.postgresql.org/docs/14/textsearch-controls.html#TEXTSEARCH-RANKING
        ).label('rank')

        if sort:
            query = query.add_columns(sort_rank)

        query = query.filter(vector.match(search_query, **kwargs))

        if sort:
            query = query.order_by(
                sa.desc(sort_rank)
            )

        query = query.params(term=search_query)
        # print(query)
        # print(str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))

    # Если в фигурных скобках - поиск по вхождению
    elif user_search_term and user_search_term[0] == '{' and user_search_term[-1] == '}':

        sort = False

        user_search_term = user_search_term[1:-1]

        fclauses = [func.array_to_string(QuestAnswerBase.questions, " ").ilike(f'%{user_search_term}%')]
        if not only_questions:
            fclauses.append(QuestAnswerBase.abstract.ilike(f'%{user_search_term}%'))

        query = query.filter(or_(*fclauses))

        pass

    else:
        query = query.filter(False)

    try:
        results = query.all()
    except Exception as e:
        print(e)

    if sort:
        results = map(lambda x: AttrDict({'id': x[0],
                                          'questions': x[1],
                                          'abstract': x[2],
                                          'rank': x[3] if len(x) > 3 else 0,
                                          }.items()), results)
    else:
        results = map(lambda x: AttrDict({'id': x[0],
                                          'questions': x[1],
                                          'abstract': x[2],
                                          }.items()), results)
    results = list(results)
    return results
