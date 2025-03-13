
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(text_query: str, answer_id: int):
    from info_service import actions

    if text_query and text_query[0] == '{' and text_query[-1] == '}':
        text_query = text_query[1:-1]

    session = Session()
    query_rel = session.query(QuestAnswerBaseRelevQueryRel)\
        .join(QuestAnswerBaseRelevQueryRel.query).join(QuestAnswerBaseRelevQueryRel.answer)\
        .filter(QuestAnswerBaseRelevQuery.query == text_query, QuestAnswerBase.id == answer_id)\
        .order_by(QuestAnswerBaseRelevQueryRel.relevantion_part.desc()).first()

    if query_rel:
        return float(query_rel.relevantion_part)

    return 0.0
