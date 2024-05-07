
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
    results = actions.db_list_search_entries(text_query_search, category=None, sort=False, only_questions=only_questions)
    len_res = len(results)
    if len_res:
        relevK = actions.metrics_getTopKrelevN(text_query, K, only_questions, optimized_text_query=optimized_text_query)
        div = (K if len_res > K else len_res)
        return (relevK / div) if div else 0.0

    return 0.0
