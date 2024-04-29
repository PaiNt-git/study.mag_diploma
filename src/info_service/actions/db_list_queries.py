
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBaseRelevQuery
from info_service.db_utils import togudb_serializator


def main():
    session = Session()
    query = session.query(QuestAnswerBaseRelevQuery).order_by(QuestAnswerBaseRelevQuery.id)
    return query
