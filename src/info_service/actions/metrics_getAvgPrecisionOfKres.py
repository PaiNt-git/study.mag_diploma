
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, K=10, only_questions=True):
    from info_service import actions

    session = Session()
    results = actions.db_list_search_entries(text_query, category=None, sort=False, only_questions=only_questions) if not search_results else search_results
    len_res = len(results)
    if len_res:
        sum_pec = 0.0
        relev_from_res = actions.metrics_getTopKrelevN(text_query, K, only_questions)
        for num in range(1, K + 1):
            precK = actions.metrics_getPrecisionOfKres(text_query, num, K, only_questions=only_questions, search_results=results)
            sum_pec += precK

        return sum_pec / relev_from_res

    return 0.0
