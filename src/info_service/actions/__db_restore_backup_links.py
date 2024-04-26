
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase
from info_service.db_utils import togudb_serializator
from sqlalchemy.engine import create_engine
from sqlalchemy.pool.impl import NullPool
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker


def main():

    session = Session()

    query = session.query(QuestAnswerBase).delete(synchronize_session=False)
    session.commit()

    engine = create_engine('postgresql://togudb:t111@127.0.0.1:5436/t123', poolclass=NullPool, pool_recycle=40, connect_args={'connect_timeout': 10})
    Session_ = scoped_session(sessionmaker(bind=engine, autocommit=False))
    oldsess = Session_()

    rawq = '''
        select *
        from telegram_bot_link_base
    '''

    for row in oldsess.execute(rawq):
        ex_row = list(row)
        print(ex_row)
        nel = QuestAnswerBase()
        nel.questions = ex_row[2]
        nel.abstract = ex_row[4]
        nel.result = ex_row[6]
        session.add(nel)
        session.flush()

    session.commit()

    return


if __name__ == '__main__':
    main()
