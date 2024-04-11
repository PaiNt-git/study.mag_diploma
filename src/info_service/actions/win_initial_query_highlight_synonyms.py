import os
import time
import json
import asyncio

from pprint import pprint

from itertools import chain
from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets


RUS_POS = {
    'S': 'существительное',
    'A': 'прилагательное',
    'NUM': 'числительное',
    'A-NUM': 'численное прилагательное',
    'V': 'глагол',
    'ADV': 'наречие',
    'PRAEDIC': 'предикатив',
    'PARENTH': 'вводное',
    'S-PRO': 'местоим. сущ.',
    'A-PRO': 'местоим. прил.',
    'ADV-PRO': 'местоим. нареч.',
    'PRAEDIC-PRO': 'местоим. предик.',
    'PR': 'предлог',
    'PART': 'частица',
    'INIT': 'инит',
    'NONLEX': 'нонлекс',

    'DET': 'местоимение',
    'CCONJ': 'союз',

    'ADP': 'предлог',
    'NOUN': 'имя существительное',
    'ADJ': 'имя прилагательное',
    'ADJF': 'имя прилагательное (полное)',
    'ADJS': 'имя прилагательное (краткое)',
    'COMP': 'компаратив',
    'VERB': 'глагол (личная форма)',
    'INFN': 'глагол (инфинитив)',
    'PRTF': 'причастие (полное)',
    'PRTS': 'причастие (краткое)',
    'GRND': 'деепричастие',
    'NUMR': 'числительное',
    'ADVB': 'наречие',
    'NPRO': 'местоимение-существительное',
    'PRED': 'предикатив',
    'PREP': 'предлог',
    'CONJ': 'союз',
    'PRCL': 'частица',
    'INTJ': 'междометие',

}


def main(main_window):
    from info_service import actions

    all_tokens_with_synonims = main_window.MAINWINDOW_LOCAL_STORAGE.get('all_tokens_with_synonims', [])

    allstr = ''

    for token in all_tokens_with_synonims:
        if token['pg_lexem'] and len(token['synonyms']):
            rupos = RUS_POS.get(token["POS"], token["POS"])

            allstr += f'{token["text"]} [часть речи: {token["POS"]} ({rupos})]:\n'
            for synonym in token['synonyms']:
                allstr += f'    {synonym["ann_lemma"]}, [сем. вес: {synonym["weight"]:.2f}]\n'

            allstr += '\n'

        pass

    main_window.TextQuerySynonims.setText(str(allstr))
