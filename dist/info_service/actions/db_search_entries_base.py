
import sqlalchemy as sa
from sqlalchemy_searchable import search, parse_search_query

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator


def db_search_entries_base(user_search_term, category=None, sort=False, search_on='all'):

    session = Session()

    query = session.query(QuestAnswerBase)
    if category:
        query = query.filter(QuestAnswerBase.category == category)

    vector = QuestAnswerBase.search_vector.property.columns[0]
    if search_on == 'questions':
        vector = QuestAnswerBase.q_search_vector.property.columns[0]

    options = vector.type.options
    regconfig = options['regconfig']

    search_query = parse_search_query(user_search_term)

    query = query.filter(vector.match(search_query))
    if sort:
        query = query.order_by(
            sa.desc(
                sa.func.ts_rank_cd(
                    vector,
                    sa.func.to_tsquery(search_query)
                )
            )
        )

    query = query.params(term=search_query)

    results = map(lambda x: togudb_serializator(x, include=('id',
                                                            'category',
                                                            'name',
                                                            'abstract',
                                                            'keywords',
                                                            'questions',
                                                            'result',
                                                            )), query)

    results = list(results)

    return results
