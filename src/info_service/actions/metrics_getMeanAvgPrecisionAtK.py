
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(K=10, only_questions=True):
    """
    https://www.evidentlyai.com/ranking-metrics/mean-average-precision-map
    https://habr.com/ru/companies/econtenta/articles/303458/

    :param K:
    :param only_questions:
    """
    from info_service import actions

    session = Session()
    SumApAtK = 0.0
    all_queries = session.query(QuestAnswerBaseRelevQuery)
    count_queries = all_queries.count()
    if count_queries == 0:
        return 0.0
    for query in all_queries:
        SumApAtK += actions.metrics_getAvgPrecisionOfKres(query.query, K, only_questions=only_questions)

    return SumApAtK / count_queries
