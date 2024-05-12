
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

    return_vals = {
        'all': 0.0,
        'relev_from_res': 0.0,
        'precKs': [],
        'sum_pec': 0.0
    }

    session = Session()
    results = actions.db_list_search_entries(text_query_search, category=None, sort=True, only_questions=only_questions)
    len_res = len(results)
    if len_res:
        lenk = len_res if len_res < K else K
        return_vals['lenk'] = lenk
        sum_pec = 0.0
        # relev_from_res = actions.metrics_getTopKrelevN(text_query, K, only_questions, optimized_text_query=optimized_text_query)
        for num in range(1, K + 1):
            precK = actions.metrics_getPrecisionOfKres(text_query, num, K, only_questions=only_questions, search_results=results, optimized_text_query=optimized_text_query)
            if precK != 0.0:
                return_vals['precKs'].append(precK)
            sum_pec += precK

        return_vals['sum_pec'] = sum_pec

        return_vals['all'] = (sum_pec / lenk) if lenk else 0.0

        return return_vals

    return return_vals
