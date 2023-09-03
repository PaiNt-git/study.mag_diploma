from sqlalchemy_searchable import search

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator


def db_get_text_search_query(user_search_term):

    session = Session()

    query = session.query(QuestAnswerBase)

    query = search(query, user_search_term, sort=True)

    results = map(lambda x: togudb_serializator(x, include=('id',
                                                            'category',
                                                            'name',
                                                            'abstract',
                                                            'questions',
                                                            'keywords',
                                                            'result',
                                                            )), query)

    results = list(results)

    print(results)
