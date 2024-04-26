
import sqlalchemy as sa

from info_service.db_base import Session, QuestAnswerBase

from info_service import actions


def main(user_search_term, search_on='all'):

    vector = QuestAnswerBase.search_vector.property.columns[0]
    if search_on == 'questions':
        vector = QuestAnswerBase.q_search_vector.property.columns[0]

    options = vector.type.options
    regconfig = options['regconfig']

    search_query = actions.db_get_searchterm_parsed(user_search_term)

    retexp = sa.func.to_tsquery(regconfig, search_query)

    return retexp


if __name__ == '__main__':
    main('Какой уровень образования лучше?')
