
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main():
    session = Session()
    query = session.query(QuestAnswerBaseRelevQueryRel).order_by(QuestAnswerBaseRelevQueryRel.id)
    return query
