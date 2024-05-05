
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, answer_id: int):
    from info_service import actions

    session = Session()
    query_rel = session.query(QuestAnswerBaseRelevQueryRel)\
        .join(QuestAnswerBaseRelevQueryRel.query).join(QuestAnswerBaseRelevQueryRel.answer)\
        .filter(QuestAnswerBaseRelevQuery.query == text_query, QuestAnswerBase.id == answer_id)\
        .order_by(QuestAnswerBaseRelevQueryRel.relevantion_part.desc()).first()

    if query_rel:
        return float(query_rel.relevantion_part)

    return 0.0
