
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, K=10, only_questions=True):
    from info_service import actions

    N = 0

    session = Session()
    results = actions.db_list_search_entries(text_query, category=None, sort=False, only_questions=only_questions)
    if len(results):
        for res in results:
            rel = actions.metrics_rel01_by_text(text_query, res.id)
            if rel:
                N += 1

    return N if N <= K else K
