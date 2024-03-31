
import sqlalchemy as sa
from sqlalchemy_searchable import parse_search_query

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator


def main(user_search_term, logging=True):

    session = Session()

    sql = f'''

    SELECT lexeme
    FROM   unnest(to_tsvector('pg_catalog.russian', '{user_search_term}')) arr
    ORDER  BY positions[1]

    '''
    if logging:
        print(sql)

    resultset = session.execute(sql)

    res = [x[0] for x in resultset]

    return ' '.join(res) if len(res) else ''


if __name__ == '__main__':
    main('Какой уровень образования лучше?')
