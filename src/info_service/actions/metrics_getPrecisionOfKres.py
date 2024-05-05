
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, k=1, K=10, only_questions=True, search_results=None):
    from info_service import actions

    session = Session()
    results = actions.db_list_search_entries(text_query, category=None, sort=False, only_questions=only_questions) if not search_results else search_results
    len_res = len(results)
    if len_res:
        relev_map = {k_: 0 for k_ in range(1, K + 1)}
        for num, res in enumerate(results[:K], 1):
            relev_map[num] = actions.metrics_rel01_by_text(text_query, res.id)
            if k == num:
                beforeeq_relev = [pos for pos, rel in sorted(relev_map.items(), key=lambda x: x[0]) if rel > 0]

                prec = len(beforeeq_relev) / k
                return prec

    return 0.0
