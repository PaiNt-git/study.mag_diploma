
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator


def main():

    session = Session()

    query = session.query(QuestAnswerBase)

    return query
