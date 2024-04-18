import os
import time
import json
import asyncio

from pprint import pprint

from itertools import chain
from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service.db_base import Session
import math


RUS_POS = {
    'S': 'сущ.',
    'A': 'прил.',
    'NUM': 'числ.',
    'A-NUM': 'числ. прил.',
    'V': 'глаг.',
    'ADV': 'нар.',
    'PRAEDIC': 'предикатив',
    'PARENTH': 'вводное',
    'S-PRO': 'мест. сущ.',
    'A-PRO': 'мест. прил.',
    'ADV-PRO': 'мест. нареч.',
    'PRAEDIC-PRO': 'мест. предик.',
    'PR': 'предлог',
    'PART': 'частица',
    'INIT': 'инит',
    'NONLEX': 'нонлекс',

    'DET': 'мест.',
    'CCONJ': 'союз',

    'ADP': 'предлог',
    'NOUN': 'сущ.',
    'ADJ': 'прил.',
    'ADJF': 'имя прилагательное (полное)',
    'ADJS': 'имя прилагательное (краткое)',
    'COMP': 'компаратив',
    'VERB': 'глагол (личная форма)',
    'INFN': 'глагол (инфинитив)',
    'PRTF': 'причастие (полное)',
    'PRTS': 'причастие (краткое)',
    'GRND': 'деепричастие',
    'NUMR': 'числ.',
    'ADVB': 'нар.',
    'NPRO': 'местоимение-существительное',
    'PRED': 'предикатив',
    'PREP': 'предлог',
    'CONJ': 'союз',
    'PRCL': 'частица',
    'INTJ': 'междометие',

}


def get_has_in_postgres_TF_IDF(lexem, only_questions=False):
    session = Session()
    que_type = 0
    if only_questions:
        que_type = 1

    sqlstr = '''

        CREATE OR REPLACE FUNCTION public.telegram_bot_link_base_get_words(query_type int)
        RETURNS SETOF RECORD LANGUAGE plpgsql as
        '
        DECLARE
          answer RECORD;
        BEGIN
            IF query_type = 0 THEN
              FOR answer IN SELECT id FROM telegram_bot_link_base
              LOOP
                    RETURN QUERY select answer.id as ans_id, lexems.word, lexems.nentry num_in_doc, lexems.weight_norm, (select SUM(allexem.cnt)
                    from
                    (
                    SELECT count(*) cnt FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR , ''ABCD'')
                    ) allexem) from
                    (
                    SELECT 1.0 as weight_norm,  * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''A'')
                    union all
                    SELECT 0.4 as weight_norm, * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''B'')
                    union all
                    SELECT 0.2 as weight_norm,  * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''C'')
                    union all
                    SELECT 0.1 as weight_norm,  * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''D'')
                    ) lexems;
              END LOOP;
            ELSE
              FOR answer IN SELECT id FROM telegram_bot_link_base
              LOOP
                    RETURN QUERY select answer.id as ans_id, lexems.word, lexems.nentry num_in_doc, lexems.weight_norm, (select SUM(allexem.cnt)
                    from
                    (
                    SELECT count(*) cnt FROM ts_stat(''SELECT q_search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR , ''AB'')
                    ) allexem) from
                    (
                    SELECT 1.0 as weight_norm,  * FROM ts_stat(''SELECT q_search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''A'')
                    union all
                    SELECT 0.4 as weight_norm, * FROM ts_stat(''SELECT q_search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''B'')
                    ) lexems;
              END LOOP;
            END IF;
            RETURN;
        END;
        '

    '''
    results = session.execute(sqlstr)
    session.commit()

    sqlstr = '''

        select count(*) from telegram_bot_link_base

    '''.format(lexem)
    alldocs = session.execute(sqlstr).scalar()

    sqlstr = '''

        select * from (
        SELECT * FROM public.telegram_bot_link_base_get_words({que_type}) f(ans_id int, word text, num_in_doc int4, weight_norm numeric, summa numeric)
        ) lemms where length(lemms.word)>1 and not isnumeric(lemms.word) and  lemms.word='{lexem}'
        ORDER BY summa DESC, weight_norm DESC, word

    '''.format(lexem=lexem, que_type=que_type)

    results = session.execute(sqlstr).fetchall()
    if not len(results):
        return None, 0
    results = map(dict, results)

    bydocs_tf = [x['num_in_doc'] / x['summa'] for x in results]

    # ndoc - Ответов с вхождением
    # nentry - Вхождений за всю базу

    if not only_questions:
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

            ) lemms where length(lemms.word)>1 and not isnumeric(lemms.word) and lemms.word='{lexem}'
            ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

        '''.format(lexem=lexem)
    else:
        sqlstr = '''

            select distinct * from
            (
                SELECT 'questions' as col_name, 'A' as weight, 1.0 as weight_norm,  * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base  ', 'A')
                union all
                SELECT 'keywords' as icolumn, 'B' as  weight, 0.4 as weight_norm, * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base  ', 'B')

            ) lemms where length(lemms.word)>1 and not isnumeric(lemms.word) and lemms.word='{lexem}'
            ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

        '''.format(lexem=lexem)

    results = session.execute(sqlstr).first()
    results = dict(results)

    idf = math.log(alldocs / results['ndoc'])

    bydocs_tf_idf = [float(tf) * float(idf) for tf in bydocs_tf]

    mean_tf_idf = sum(bydocs_tf_idf) / float(len(bydocs_tf_idf))

    return results, mean_tf_idf


def main(main_window):
    from info_service import actions

    all_tokens_with_synonims = main_window.MAINWINDOW_LOCAL_STORAGE.get('all_tokens_with_synonims', [])

    allstr = ''

    for token in all_tokens_with_synonims:

        synonyms = list(filter(lambda x: (bool(x['pg_lexem']) and x['pg_lexem'] != token['pg_lexem']), token['synonyms']))

        if token['pg_lexem'] and len(synonyms):

            pg_lexem, tf_idf = get_has_in_postgres_TF_IDF(token['pg_lexem'], True)

            rupos = RUS_POS.get(token["POS"], token["POS"])

            allstr += f'{token["text"]}<{token["pg_lexem"]}> [tf_idf: {tf_idf:.2f}][часть речи: {token["POS"]}({rupos})]:\n'

            has_tf_idf_tokens = False
            for synonym in synonyms:
                pg_lexem_syn, tf_idf_syn = get_has_in_postgres_TF_IDF(synonym["pg_lexem"], True)
                if pg_lexem_syn:
                    allstr += f'    -{synonym["ann_lemma"]}<{synonym["pg_lexem"]}>, [tf_idf: {tf_idf_syn:.2f}][сходство: {synonym["weight"]:.2f}]\n'
                    has_tf_idf_tokens = True

            if not has_tf_idf_tokens:
                allstr += f'    -[для данного токена не удалось найти синонимов лексемы которых присутвуют в базе]\n'

            allstr += '\n'

        pass

    main_window.TextQuerySynonims.setText(str(allstr))


if __name__ == '__main__':
    get_has_in_postgres_TF_IDF('поступ', True)
