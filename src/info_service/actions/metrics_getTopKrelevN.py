
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, K=10, only_questions=True, optimize=False, optimized_text_query=''):
    """
    https://www.evidentlyai.com/ranking-metrics/mean-average-precision-map
    https://www.evidentlyai.com/ranking-metrics/ndcg-metric
    :param text_query:
    :param K:
    :param only_questions:
    """
    from info_service import actions

    text_query_search = text_query
    if optimize:
        text_query_search = actions.query_optimize_query(text_query, only_questions)
        optimized_text_query = text_query_search
    elif optimized_text_query:
        text_query_search = optimized_text_query

    N = 0

    session = Session()
    results = actions.db_list_search_entries(text_query_search, category=None, sort=False, only_questions=only_questions)
    if len(results):
        for res in results:
            rel = actions.metrics_rel01_by_text(text_query, res.id)
            if rel:
                N += 1

    return N if N <= K else K
