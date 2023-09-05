
import sqlalchemy as sa
from sqlalchemy_searchable import search, parse_search_query

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator


def db_list_all_lemms():

    session = Session()

    results = QuestAnswerBase.get_all_lemms(return_is_dict=True)

    results = list(results)

    print('test1')

    print('test2')

    return results


if __name__ == '__main__':
    print(db_list_all_lemms())
