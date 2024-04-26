
import sqlalchemy as sa
from sqlalchemy_searchable import search, parse_search_query

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def main(only_questions=True):
    session = Session()
    results = QuestAnswerBase.get_all_lemms(return_is_dict=True, only_questions=only_questions)
    results = map(lambda x: AttrDict(x.items()), results)
    results = list(results)
    return results


if __name__ == '__main__':
    print(main())
