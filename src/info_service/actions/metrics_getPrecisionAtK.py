
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, K=10, only_questions=True):
    from info_service import actions

    session = Session()
    results = actions.db_list_search_entries(text_query, category=None, sort=False, only_questions=only_questions)
    len_res = len(results)
    if len_res:
        relevK = actions.metrics_getTopKrelevN(text_query, K, only_questions)
        return relevK / (K if len_res > K else len_res)

    return 0
