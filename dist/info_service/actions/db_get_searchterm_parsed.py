
import sqlalchemy as sa
from sqlalchemy_searchable import parse_search_query


def db_get_searchterm_parsed(user_search_term):

    search_query = parse_search_query(user_search_term)

    return search_query
