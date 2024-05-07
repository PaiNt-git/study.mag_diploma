
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, K=10, only_questions=True, optimize=False, optimized_text_query=''):
    from info_service import actions

    text_query_search = text_query
    if optimize:
        text_query_search = actions.query_optimize_query(text_query, only_questions)
        optimized_text_query = text_query_search
    elif optimized_text_query:
        text_query_search = optimized_text_query

    session = Session()
    results = actions.db_list_search_entries(text_query_search, category=None, sort=True, only_questions=only_questions)
    len_res = len(results)
    if len_res:
        sum_pec = 0.0
        relev_from_res = actions.metrics_getTopKrelevN(text_query, K, only_questions, optimized_text_query=optimized_text_query)
        for num in range(1, K + 1):
            precK = actions.metrics_getPrecisionOfKres(text_query, num, K, only_questions=only_questions, search_results=results, optimized_text_query=optimized_text_query)
            sum_pec += precK

        return (sum_pec / relev_from_res) if relev_from_res else 0.0

    return 0.0
