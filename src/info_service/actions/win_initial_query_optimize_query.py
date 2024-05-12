import time
import json
import asyncio
import itertools

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets


from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

from info_service import actions

from info_service.actions._answers_utils import *


def main(main_window):
    from info_service.actions.win_initial_query_highlight_synonyms import get_has_in_postgres_TF_IDF

    try:
        only_questions = main_window.MAINWINDOW_LOCAL_STORAGE['only_questions']

        all_tokens_with_synonims = main_window.MAINWINDOW_LOCAL_STORAGE.get('all_tokens_with_synonims', [])

        sentence_members = main_window.MAINWINDOW_LOCAL_STORAGE.get('sentence_members', [])

        def get_ext_token_by_id(tid):
            for token_info in all_tokens_with_synonims:
                if token_info['_natasha_token'].id == tid:
                    return token_info

        opt_tokens_ = [get_ext_token_by_id(x.id) for x in itertools.chain.from_iterable(map(lambda x: x['first_level_cut'], sentence_members))]

        opt_tokens = []

        for token in opt_tokens_:

            pg_lexem, tf_idf = get_has_in_postgres_TF_IDF(token['pg_lexem'], only_questions)

            ten_pers = 0 if tf_idf <= 0 else tf_idf * 0.1

            synonyms = list(filter(lambda x: (bool(x['pg_lexem']) and x['pg_lexem'] != token['pg_lexem']), token['synonyms']))

            if token['pg_lexem'] and len(synonyms):

                has_tf_idf_tokens = False
                for synonym in synonyms:
                    pg_lexem_syn, tf_idf_syn = get_has_in_postgres_TF_IDF(synonym["pg_lexem"], only_questions)
                    if pg_lexem_syn and tf_idf_syn > tf_idf + ten_pers:
                        opt_tokens.append(synonym)
                        has_tf_idf_tokens = True
                        break

                if not has_tf_idf_tokens:
                    if tf_idf > 0.0:
                        opt_tokens.append(token)

            else:
                if tf_idf > 0.0:
                    opt_tokens.append(token)

        allstr = ' '.join([x['pg_lexem'] for x in opt_tokens])
        first_allstr = allstr
        res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)

        # Проверка и Обрезка дополнительных членов предложения
        if not len(res):
            for add_sm in itertools.chain.from_iterable(map(lambda x: x['additional'], sentence_members)):

                add_sm = get_ext_token_by_id(add_sm.id)

                if add_sm['id'] in [x['id'] for x in opt_tokens]:
                    # Проверим исходный член предлоежения
                    opt_tokens_prime = [(x.get('_prime_token_info', x) if (x['id'] == add_sm['id']) else x) for x in opt_tokens]
                    allstr = ' '.join([x['pg_lexem'] for x in opt_tokens_prime])
                    res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)
                    if not len(res):
                        # Уберем дополнительный член предлоежения
                        opt_tokens = list(filter(lambda x: x['id'] != add_sm['id'], opt_tokens))
                        allstr = ' '.join([x['pg_lexem'] for x in opt_tokens])
                        res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)
                        if len(res):
                            break
                    else:
                        break

        # Оставшиеся члены предложения по пробуем заменить исходными токенами
        if not len(res):
            for i in range(len(opt_tokens)):
                opt_tokens = [(x.get('_prime_token_info', x) if (x['id'] == opt_tokens[i]['id']) else x) for x in opt_tokens]
                allstr = ' '.join([x['pg_lexem'] for x in opt_tokens])
                res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)
                if len(res):
                    break
            else:
                allstr = first_allstr

        main_window.TextModifiedQuery.setText(str(allstr))

    except Exception as e:
        print(e)
