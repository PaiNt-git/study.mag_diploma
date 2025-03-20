
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(K=10, only_questions=True, optimize=False, substringsearch=False):
    """
    https://www.evidentlyai.com/ranking-metrics/mean-average-precision-map
    https://habr.com/ru/companies/econtenta/articles/303458/

    :param K:
    :param only_questions:
    """
    from info_service import actions

    if substringsearch:
        def query_text_wrapper(x): return ('{' + str(x) + '}')
    else:
        def query_text_wrapper(x): return str(x)

    return_vals = {
        'all': 0.0,
        'SumApAtKs': [],
        'count_queries': 0
    }

    session = Session()
    SumApAtK = 0.0
    all_queries = session.query(QuestAnswerBaseRelevQuery).order_by(QuestAnswerBaseRelevQuery.id)
    count_queries = all_queries.count()
    if count_queries == 0:
        return return_vals

    return_vals['count_queries'] = count_queries

    for query in all_queries:
        avgpreck = actions.metrics_getAvgPrecisionOfKres(query_text_wrapper(query.query), K, only_questions=only_questions, optimize=optimize)
        return_vals['SumApAtKs'].append(avgpreck)
        SumApAtK += avgpreck

    return_vals['all'] = (SumApAtK / count_queries if count_queries else 0.0)
    return return_vals
