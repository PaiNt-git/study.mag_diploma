import os
import time
import json
import asyncio
import itertools

from pprint import pprint

import gensim
import snowballstemmer

from copy import copy

from gensim.models.phrases import Phrases, Phraser

from itertools import chain
from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets


from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    PER,
    NamesExtractor,
    Doc
)
from natasha.syntax import token_deps

from navec import Navec

from ipymarkup import format_span_box_markup, format_span_line_markup, format_dep_markup


SENT_MEMBERS = {
    'root': 'сказуемое',
    'nsubj': 'подлежащее',
    'amod': 'определение',
    'advmod': 'обстоятельство',
    'nmod': 'дополнение',
    'obl': 'обособление',
    'obj': 'обособленое дополнение',
    'xcomp': 'инфинитивный комплемент (открытый клаузальный комплемент) / дополнение вторичной предикации',
    'acl': 'отношение(подлежащее)',
    'advcl': 'отношение(сказуемое)',
    'det': 'определитель, уточнение',
    'flat:name': 'обращение',
    'appos': 'уточнение',
    'nsubj:pass': 'подлежащее пассива',
    'ccomp': 'клаузальный комплемент',
}


class ModifNavec(Navec):
    @property
    def as_gensim(self):
        from gensim.models import KeyedVectors
        model = KeyedVectors(self.pq.dim)
        weights = self.pq.unpack()  # warning! memory heavy
        model.add_vectors(self.vocab.words, weights)
        return model


def main(main_window):
    from info_service import actions

    ru_stemmer = snowballstemmer.stemmer('russian')

    initial_query_text_widget = getattr(main_window, f'TextInitialQuery')
    initial_query_text = initial_query_text_widget.toPlainText()

    doc = Doc(initial_query_text)

    morph_vocab = MorphVocab()
    segmenter = Segmenter()

    emb = NewsEmbedding()

    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    doc.segment(segmenter)

    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)

    html_NER_spans = format_span_line_markup(initial_query_text, doc.spans)
    html_NER_spans = map(lambda x: x, html_NER_spans)
    html_NER_spans = '\n'.join(html_NER_spans) + '<br>'

    html_syntax_tree = []
    for sentence in doc.sents:
        sent_tokens = sentence.tokens
        token_deps_ = token_deps(sent_tokens)
        html_syntax_tree.append(list(format_dep_markup([_.text for _ in sent_tokens], token_deps_, arc_gap=18)))
    html_syntax_tree = '\n'.join(chain.from_iterable(html_syntax_tree)) + '<br>'

    # Исключениен именованых сущностей из подбора синонимов
    doc_spans = list(doc.spans)
    spchains = list(itertools.chain.from_iterable(map(lambda x: getattr(x, 'tokens', []), doc_spans)))

    table_widget = getattr(main_window, f'TableInitialQueryExceptedTokens')
    table_widget.clear()
    time.sleep(0.2)
    table_widget.setRowCount(0)

    columns = OrderedDict(
        [
            ('text', 'NER'),
            ('start', 'Начало'),
        ])
    table_widget.setColumnCount(len(columns))
    table_widget.setHorizontalHeaderLabels(columns.values())

    for i, row in enumerate(doc_spans):

        curc = table_widget.rowCount()
        table_widget.insertRow(curc)

        row.normalize(morph_vocab)

        for k, col_key in enumerate(columns.keys()):

            qtcell = QtWidgets.QTableWidgetItem(str(getattr(row, col_key, '')))
            qtcell.setFlags(qtcell.flags() & ~QtCore.Qt.ItemIsEditable)

            table_widget.setItem(curc, k, qtcell)

    table_widget.setVerticalHeaderLabels(list(map(str, range(1, len(doc_spans) + 1))))
    table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
    table_widget.setWordWrap(True)
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setStretchLastSection(True)
    for i in range(table_widget.columnCount()):
        if table_widget.columnWidth(i) > 200:
            table_widget.setColumnWidth(i, 200)

    # Исключениен устойчивых словосочетаний из подбора синонимов
    bigrammpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/gensim-model_bigram.pkl')
    bigram_reloaded = Phraser.load(bigrammpath)

    bigrams = []

    for sentence in doc.sents:
        phrases = bigram_reloaded[[x.text.lower() for x in sentence.tokens]]
        bigrams.extend([x for x in phrases if ' ' in x])

    table_widget = getattr(main_window, f'TableInitialQueryExceptedBigram')
    table_widget.clear()
    time.sleep(0.2)
    table_widget.setRowCount(0)

    columns = OrderedDict(
        [
            ('text', 'Bigram'),
            ('start', 'Начало'),
        ])
    table_widget.setColumnCount(len(columns))
    table_widget.setHorizontalHeaderLabels(columns.values())

    bigrams_listoflist = [x.split(' ') for x in bigrams]
    has_bigram = []

    for sentence in doc.sents:

        for token in sentence.tokens:
            bigrams_intersect = [' '.join(x) for x in bigrams_listoflist if token.text.lower() in x]
            if len(bigrams_intersect):
                setattr(token, '_is_bigram', True)

                for bigram_text in bigrams_intersect:
                    if bigram_text not in has_bigram:
                        has_bigram.append(bigram_text)

                        curc = table_widget.rowCount()
                        table_widget.insertRow(curc)

                        qtcell = QtWidgets.QTableWidgetItem(str(bigram_text))
                        qtcell.setFlags(qtcell.flags() & ~QtCore.Qt.ItemIsEditable)
                        table_widget.setItem(curc, 0, qtcell)

                        qtcell = QtWidgets.QTableWidgetItem(str(token.start))
                        qtcell.setFlags(qtcell.flags() & ~QtCore.Qt.ItemIsEditable)
                        table_widget.setItem(curc, 1, qtcell)

            else:
                setattr(token, '_is_bigram', False)

    table_widget.setVerticalHeaderLabels(list(map(str, range(1, len(doc_spans) + 1))))
    table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
    table_widget.setWordWrap(True)
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setStretchLastSection(True)
    for i in range(table_widget.columnCount()):
        if table_widget.columnWidth(i) > 200:
            table_widget.setColumnWidth(i, 200)

    print('===>Нахождение синонимов всем токенам запроса и приведение: ')
    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/gensim-model.bin')
    navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_hudlit_v1_12B_500K_300d_100q.tar')
    # navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_news_v1_1B_250K_300d_100q.tar')

    if os.path.isfile(mpath):
        gensim_model = gensim.models.KeyedVectors.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    sentence_members = []

    def get_childs(parent_token, alltokens, nesting_level=0):
        rt = list(filter(lambda x: (x.head_id == parent_token.id), alltokens))
        if nesting_level > 0:
            rt.extend(itertools.chain.from_iterable([get_childs(x, alltokens, nesting_level=nesting_level - 1) for x in rt]))
        return rt

    all_tokens_with_synonims = []
    for sentence in doc.sents:

        sentence_members.append({
            'main': [],
            'additional': [],
            'first_level_cut': [],
        })

        for token in sentence.tokens:
            print(token.text)

            # синтаксический разбор членов предлоежения
            if token.rel in SENT_MEMBERS.keys():
                virt_token = token
                _is_ner = False
                if token.id in [x.id for x in spchains]:
                    for span in doc_spans:
                        if token.id in [x.id for x in span.tokens]:
                            virt_token = copy(span)
                            setattr(virt_token, 'rel', token.rel)
                            setattr(virt_token, 'start', token.start)
                            setattr(virt_token, 'id', token.id)
                            setattr(virt_token, 'head_id', token.head_id)
                            _is_ner = True

                setattr(virt_token, '_is_ner', _is_ner)

                has_root = len([x for x in sentence.tokens if x.rel == 'root']) > 0
                has_nsubj = len([x for x in sentence.tokens if x.rel == 'nsubj']) > 0

                print(' '.join([f'{x.text}|{x.rel}' for x in sentence.tokens]))

                if (virt_token.rel in ('root', 'nsubj', 'nsubj:pass')) or (not has_root and virt_token.rel == 'advcl') or (not has_nsubj and virt_token.rel == 'acl'):
                    sentence_members[-1]['main'].append(virt_token)
                else:
                    sentence_members[-1]['additional'].append(virt_token)

                if virt_token._is_ner or virt_token._is_bigram:
                    has_tok_ids = [x.id for x in sentence_members[-1]['first_level_cut']]
                    if virt_token.id not in has_tok_ids:
                        sentence_members[-1]['first_level_cut'].append(virt_token)

                if (virt_token.rel == 'root') or (not has_root and virt_token.rel == 'advcl') or (virt_token.id == virt_token.head_id and virt_token.rel != 'punct'):

                    sentence_members[-1]['first_level_cut'].append(virt_token)

                    if (virt_token.rel == 'root' and not has_nsubj):
                        sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=2))
                    elif has_root and has_nsubj:
                        sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=1))
                    elif has_root and not has_nsubj:
                        sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=0))
                    elif not has_root and virt_token.id == virt_token.head_id and virt_token.rel != 'punct':
                        sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=1))

                    sentence_members[-1]['first_level_cut'] = list(filter(lambda x: (x.rel in SENT_MEMBERS.keys() and
                                                                                     x.pos in ('NOUN', 'ADJ', 'VERB', 'INFN', 'PROPN')),
                                                                          sentence_members[-1]['first_level_cut']))

            token.lemmatize(morph_vocab)

            _gensim_synonyms = []
            if token.pos not in (
                'PUNCT',    # знаки препинания
                'ADP',      # предлог
                'CCONJ',    # союз
                'DET',      # местоимение
            ):
                try:
                    if token.id not in [x.id for x in spchains]:
                        _gensim_synonyms = (gensim_model.most_similar(positive=[token.lemma]) if token.lemma and len(token.text) > 2 else [])
                except KeyError:
                    pass
                print(f'====>Весь набор предположительных синонимов ({token.pos}): ')
                _gensim_synonyms.sort(key=lambda x: x[1], reverse=True)
                pprint(_gensim_synonyms)

            token_info = {}
            token_info['_natasha_token'] = token
            token_info['POS'] = token.pos
            token_info['id'] = token.id

            token_info['text'] = token.text
            token_info['ann_lemma'] = token.lemma
            token_info['ann_lexem'] = ru_stemmer.stemWord(token.text).lower()
            token_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(token.text, logging=False) if token.text else None
            token_info['weight'] = 1.0
            token_info['synonyms'] = []

            _has_that_lemma = []

            for syn, weight in _gensim_synonyms:
                syn_norm = morph_vocab.lemmatize(syn, token.pos, token.feats)
                if syn_norm in _has_that_lemma:
                    continue
                syn_info = {}

                syn_info['_prime_token_info'] = token_info

                syn_info['POS'] = token.pos
                syn_info['id'] = token.id

                syn_info['text'] = syn
                syn_info['ann_lemma'] = syn_norm
                syn_info['ann_lexem'] = ru_stemmer.stemWord(syn_norm).lower()
                syn_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(syn_norm, logging=False) if syn_norm else None
                syn_info['weight'] = weight

                token_info['synonyms'].append(syn_info)

                _has_that_lemma.append(syn_norm)

            all_tokens_with_synonims.append(token_info)

        try:
            sentence_members[-1]['first_level_cut'] = sorted(sentence_members[-1]['first_level_cut'], key=lambda x: x.start)
            _uniq_tokens_ids = []
            _uniq_tokens = []
            _has_base_tokens = []
            for tk in sentence_members[-1]['first_level_cut']:
                if tk.id not in _uniq_tokens_ids:
                    _uniq_tokens_ids.append(tk.id)
                    if not len([x for x in _has_base_tokens if x in tk.text]):
                        _uniq_tokens.append(tk)
                        _has_base_tokens.extend((tk.text.split(' ') if tk.text.count(' ') else [tk.text]))
        except Exception as e:
            print(e)

        sentence_members[-1]['first_level_cut'] = _uniq_tokens

    print(f'=====>Итоговый массив токенов: ')
    pprint(all_tokens_with_synonims)

    main_sm_str = ''
    for i, sent in enumerate(sentence_members):
        main_sm_str += f'<hr><i>{i+1}-е предложение</i><br><br>'

        def get_smname(rel):
            return SENT_MEMBERS.get(rel, rel)

        main_sm_str += '&nbsp;&nbsp;<b>Основные члены предложения:</b><ul class="topsmallul">'
        main_sm_str += ''.join([f'<li><b>{x.text}</b> - {get_smname(x.rel)}</li>' for x in sent['main']])
        main_sm_str += '</ul>'

        main_sm_str += '&nbsp;&nbsp;<b>Второстепенные члены предложения:</b><ul class="topsmallul">'
        main_sm_str += ''.join([f'<li><b>{x.text}</b> - {get_smname(x.rel)}</li>' for x in sent['additional']])
        main_sm_str += '</ul>'

        main_sm_str += '&nbsp;&nbsp;<b>Сокращение предложения, до 3 уровня связи членов предложения (только с существительными, глаголами, прилагательными, NER):</b><ul class="topsmallul divblue">'
        main_sm_str += ' '.join([f'<b>{x.text}</b>' for x in sent['first_level_cut']])
        main_sm_str += '</ul>'

    enreturn = '''
<!DOCTYPE HTML>
<html><head>

<style>
.zoomed {
    zoom: 1.5;
    -moz-transform: scale(1.5);
    -moz-transform-origin: 0 0;
}
.minzoomed {
    zoom: 1.1;
    -moz-transform: scale(1.1);
    -moz-transform-origin: 0 0;
}
.topsmallul {
    padding-top: 2px;
    margin-top: 2px;
}
.divblue {
    color: blue;
}
</style>

</head><body>
<h4>Синтаксический анализ</h4>
<div class="zoomed">''' + html_syntax_tree + '''</div>
<h4>Члены предложения:</h4>
<div class="minzoomed">''' + main_sm_str + '''</div>
</body></html>
'''.replace('<div class="tex2jax_ignore" style="white-space: pre-wrap">', '<div class="tex2jax_ignore">')

    initial_query_analysis_widget = getattr(main_window, f'WebViewAnalysisPreview')
    initial_query_analysis_widget.setHtml(enreturn)

    main_window.MAINWINDOW_LOCAL_STORAGE['all_tokens_with_synonims'] = all_tokens_with_synonims

    main_window.MAINWINDOW_LOCAL_STORAGE['sentence_members'] = sentence_members

    print(f'=>Токены анализа записаны в локал-сторадж... ')


if __name__ == '__main__':
    from info_service import actions

    initial_query_text = '''В синтаксисе предложения принято делить на части, эти части образуют небольшое множество грамматических классов — членов предложения. Член предложения определяется и опознается по той функции, которую он выполняет в составе предложения.'''.strip()

    doc = Doc(initial_query_text)

    morph_vocab = MorphVocab()
    segmenter = Segmenter()

    emb = NewsEmbedding()

    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    doc.segment(segmenter)

    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)

    print('=====нахождение синонимов всем токенам запроса и приведение ')
    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/gensim-model.bin')
    navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_hudlit_v1_12B_500K_300d_100q.tar')
    # navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_news_v1_1B_250K_300d_100q.tar')

    if os.path.isfile(mpath):
        gensim_model = gensim.models.KeyedVectors.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    all_tokens_with_synonims = []
    for sentence in doc.sents:
        for token in sentence.tokens:
            print(token.text)
            if token.text == 'опознается':
                print(1)

            token.lemmatize(morph_vocab)

            token_info = {
                '_natasha_token': token,
            }
            try:
                token_info['_gensim_synonyms'] = (gensim_model.most_similar(token.lemma) if token.lemma and len(token.text) > 2 else [])
            except KeyError:
                token_info['_gensim_synonyms'] = []
            token_info['synonyms'] = []

            token_info['text'] = token.text
            token_info['lemma'] = token.lemma
            token_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(token.lemma) if token.lemma else None
            token_info['weight'] = 1.0

            for syn, weight in token_info['_gensim_synonyms']:
                syn_norm = morph_vocab.lemmatize(syn, token.pos, token.feats)
                syn_info = {}
                syn_info['text'] = syn
                syn_info['lemma'] = syn_norm
                syn_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(syn_norm)
                syn_info['weight'] = weight
                token_info['synonyms'].append(syn_info)
                print(syn_info)

            all_tokens_with_synonims.append(token_info)

    html_NER_spans = format_span_line_markup(initial_query_text, doc.spans)
    html_NER_spans = map(lambda x: x, html_NER_spans)
    html_NER_spans = '\n'.join(html_NER_spans) + '<br>'

    html_syntax_tree = []
    for sentence in doc.sents:
        sent_tokens = sentence.tokens
        token_deps_ = token_deps(sent_tokens)
        html_syntax_tree.append(list(format_dep_markup([_.text for _ in sent_tokens], token_deps_, arc_gap=18)))
    html_syntax_tree = '\n'.join(chain.from_iterable(html_syntax_tree)) + '<br>'

    enreturn = '''
<!DOCTYPE HTML>
<html><head></head><body>
<h4>Синтаксический анализ</h4>
''' + html_syntax_tree + '''
<h5>Члены предложения:</h5>


</body></html>
'''.replace('<div class="tex2jax_ignore" style="white-space: pre-wrap">', '<div class="tex2jax_ignore">')

    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(enreturn)
