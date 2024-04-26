
import sqlalchemy as sa

from sqlalchemy import cast

from sqlalchemy_searchable import search, parse_search_query, search_manager

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.sqltypes import Float, Numeric


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def main(user_search_term, category=None, sort=False, only_questions=True):

    session = Session()

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

    query = session.query(QuestAnswerBase.id,
                          QuestAnswerBase.questions,
                          QuestAnswerBase.abstract,
                          )
    if sort:
        query = query.add_columns(sort_rank)

    if category:
        query = query.filter(QuestAnswerBase.category == category)

    query = query.filter(vector.match(search_query, **kwargs))

    if sort:
        query = query.order_by(
            sa.desc(sort_rank)
        )

    query = query.params(term=search_query)
    print(query)
    # print(str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))

    results = query.all()
    results = map(lambda x: AttrDict({'id': x[0],
                                      'questions': x[1],
                                      'abstract': x[2],
                                      'rank': x[3],
                                      }.items()), results)
    results = list(results)
    return results
