import os

import json

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, column_property
from sqlalchemy.pool import NullPool
from sqlalchemy_utils.types.ts_vector import TSVectorType
from sqlalchemy_searchable import vectorizer
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, Unicode, UnicodeText
from sqlalchemy.dialects.postgresql.array import ARRAY
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm.session import object_session


SETTINGS = {}

secrets_dir_path = os.path.normpath(os.path.join('secrets'))
if not os.path.isdir(secrets_dir_path):
    secrets_dir_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'secrets'))

with open(os.path.normpath(os.path.join(secrets_dir_path, 'database.json')), 'r') as f:
    SETTINGS.update(json.load(f))


engine = create_engine(SETTINGS['DATABASE_URL_TOGUDB'], poolclass=NullPool, pool_recycle=40, connect_args={'connect_timeout': 10})
Base = declarative_base()
Base.metadata.reflect(engine)
Session = scoped_session(sessionmaker(bind=engine, autocommit=False))


# ========

class QuestAnswerBase(Base):
    __tablename__ = 'telegram_bot_link_base'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)

    category = column_property(Column(String, nullable=True, index=True),
                               info={'verbose_name': 'Категория', })

    questions = column_property(Column(ARRAY(String), nullable=True),
                                info={'verbose_name': 'Вопросы',
                                      })

    name = column_property(Column(Unicode, nullable=True),
                           info={'verbose_name': 'Наименование знания'})

    abstract = column_property(Column(UnicodeText, nullable=False),
                               info={'verbose_name': 'Контент-абстракт-ответ'})

    keywords = column_property(Column(ARRAY(String), nullable=True),
                               info={'verbose_name': 'Ключевые слова',
                                     })

    result = column_property(Column(JSONB, nullable=True, default={"url": "@phil_togu_bot"}),
                             info={'verbose_name': 'Результат, ссылка и т.д. (JSON)',
                                   'help_text': 'Пример: {"url": "@phil_togu_bot"} или {"url": "https://pnu.edu.ru"}',
                                   })

    q_search_vector = sa.Column(
        TSVectorType('questions', 'keywords',
                     weights={'questions': 'A', 'keywords': 'B', },
                     regconfig='pg_catalog.russian',
                     ),
        index=True,
    )

    search_vector = sa.Column(
        TSVectorType('questions', 'name', 'abstract', 'keywords',
                     weights={'questions': 'A', 'abstract': 'B', 'keywords': 'C', 'name': 'D'},
                     regconfig='pg_catalog.russian',
                     ),
        index=True,
    )

    @staticmethod
    def get_all_lemms(session=None, limit=None, offset=None, return_is_dict=False, optimize_for_context=True, only_questions=False):
        session = session or Session()

        if only_questions:
            sqlstr = '''

                select distinct * from
                (
                    SELECT 'questions' as col_name, 'A' as weight, 1.0 as weight_norm,  * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base  ', 'A')
                    union all
                    SELECT 'keywords' as icolumn, 'B' as  weight, 0.4 as weight_norm, * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base  ', 'B')

                ) lemms {optim}
                ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

            '''.format(optim=('where length(word)>1 and not isnumeric(word)' if optimize_for_context else ''))

        else:
            sqlstr = '''

                select distinct * from
                (
                    SELECT 'questions' as col_name, 'A' as weight, 1.0 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'A')
                    union all
                    SELECT 'abstract' as icolumn, 'B' as  weight, 0.4 as weight_norm, * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'B')
                    union all
                    SELECT 'keywords' as icolumn, 'C' as weight, 0.2 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'C')
                    union all
                    SELECT 'name' as icolumn, 'D' as weight, 0.1 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'D')

                ) lemms {optim}
                ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

            '''.format(optim=('where length(word)>1 and not isnumeric(word)' if optimize_for_context else ''))

        if limit:
            sqlstr += ' LIMIT {}'.format(limit)

        if offset:
            sqlstr += ' OFFSET {}'.format(offset)

        results = session.execute(sqlstr)
        if return_is_dict:
            results = map(dict, results)

        return results

    def get_all_lemms_of_self(self, limit=None, offset=None, return_is_dict=False, optimize_for_context=True, only_questions=False):
        session = object_session(self)
        if not session:
            raise ValueError

        if only_questions:
            sqlstr = '''

                select distinct * from
                (
                    SELECT 'questions' as col_name, 'A' as weight, 1.0 as weight_norm,  * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base WHERE telegram_bot_link_base.id={pk} ', 'A')
                    union all
                    SELECT 'keywords' as icolumn, 'B' as  weight, 0.4 as weight_norm, * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base WHERE telegram_bot_link_base.id={pk} ', 'B')

                ) lemms {optim}
                ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

            '''.format(pk=self.id, optim=('where length(word)>1 and not isnumeric(word)' if optimize_for_context else ''))

        else:
            sqlstr = '''

                select distinct * from
                (
                    SELECT 'questions' as col_name, 'A' as weight, 1.0 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  WHERE telegram_bot_link_base.id={pk} ', 'A')
                    union all
                    SELECT 'abstract' as icolumn, 'B' as  weight, 0.4 as weight_norm, * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  WHERE telegram_bot_link_base.id={pk} ', 'B')
                    union all
                    SELECT 'keywords' as icolumn, 'C' as weight, 0.2 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  WHERE telegram_bot_link_base.id={pk} ', 'C')
                    union all
                    SELECT 'name' as icolumn, 'D' as weight, 0.1 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  WHERE telegram_bot_link_base.id={pk} ', 'D')

                ) lemms {optim}
                ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

            '''.format(pk=self.id, optim=('where length(word)>1 and not isnumeric(word)' if optimize_for_context else ''))

        if limit:
            sqlstr += ' LIMIT {}'.format(limit)

        if offset:
            sqlstr += ' OFFSET {}'.format(offset)

        results = session.execute(sqlstr)
        if return_is_dict:
            results = map(dict, results)

        return results


@vectorizer(QuestAnswerBase.keywords)
def keywords_vectorizer(column):
    return sa.cast(sa.func.array_to_string(column, ' '), sa.Text)


@vectorizer(QuestAnswerBase.questions)
def questions_vectorizer(column):
    return sa.cast(sa.func.array_to_string(column, ' '), sa.Text)
