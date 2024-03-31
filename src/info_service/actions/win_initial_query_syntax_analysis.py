import os
import time
import json
import asyncio

from pprint import pprint

import gensim
import snowballstemmer

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
import itertools


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

    enreturn = '''
<!DOCTYPE HTML>
<html><head></head><body>
<h4>Синтаксический анализ</h4>
''' + html_syntax_tree + '''
<h5>Члены предложения:</h5>


</body></html>
'''.replace('<div class="tex2jax_ignore" style="white-space: pre-wrap">', '<div class="tex2jax_ignore">')

    initial_query_analysis_widget = getattr(main_window, f'WebViewAnalysisPreview')
    initial_query_analysis_widget.setHtml(enreturn)

    # Исключениен именованых сущностей из подбора синонимов
    doc_spans = list(doc.spans)

    table_widget = getattr(main_window, f'TableInitialQueryExceptedTokens')

    table_widget.clear()
    time.sleep(0.2)
    table_widget.setRowCount(0)

    columns = OrderedDict(
        [
            ('normal', 'NE \n(нормальная форма)'),
            ('start', 'StartChar'),
            ('stop', 'EndChar'),
            ('text', 'форма в тексте'),

        ])

    table_widget.setColumnCount(len(columns))

    table_widget.setHorizontalHeaderLabels(columns.values())

    for i, row in enumerate(doc_spans):

        curc = table_widget.rowCount()
        table_widget.insertRow(curc)

        row.normalize(morph_vocab)

        for k, col_key in enumerate(columns.keys()):

            qtcell = QtWidgets.QTableWidgetItem(str(getattr(row, col_key, '')))
            qtcell.setFlags(qtcell.flags() | QtCore.Qt.ItemIsEditable)

            table_widget.setItem(curc, k, qtcell)

    table_widget.setVerticalHeaderLabels(list(map(str, range(1, len(doc_spans) + 1))))

    table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
    table_widget.setWordWrap(True)
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setStretchLastSection(True)
    for i in range(table_widget.columnCount()):
        if table_widget.columnWidth(i) > 200:
            table_widget.setColumnWidth(i, 200)

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
            token.lemmatize(morph_vocab)

            token_info = {}
            token_info['_natasha_token'] = token

            _gensim_synonyms = []
            try:
                spchains = itertools.chain.from_iterable(map(lambda x: getattr(x, 'tokens', []), doc_spans))
                if token.id not in [x.id for x in spchains]:
                    _gensim_synonyms = (gensim_model.most_similar(positive=[token.lemma]) if token.lemma and len(token.text) > 2 else [])
            except KeyError:
                pass

            pprint('Весь набор предположительных синонимов')
            _gensim_synonyms.sort(key=lambda x: x[1], reverse=True)
            pprint(_gensim_synonyms)

            token_info['text'] = token.text
            token_info['ann_lemma'] = token.lemma
            token_info['ann_lexem'] = ru_stemmer.stemWord(token.text).lower()
            token_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(token.lemma, logging=False) if token.lemma else None
            token_info['weight'] = 1.0

            token_info['synonyms'] = []

            _has_that_lemma = []

            for syn, weight in _gensim_synonyms:
                syn_norm = morph_vocab.lemmatize(syn, token.pos, token.feats)
                if syn_norm in _has_that_lemma:
                    continue
                syn_info = {}
                syn_info['text'] = syn
                syn_info['ann_lemma'] = syn_norm
                syn_info['ann_lexem'] = ru_stemmer.stemWord(syn_norm).lower()
                syn_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(syn_norm, logging=False) if syn_norm else None
                syn_info['weight'] = weight

                token_info['synonyms'].append(syn_info)
                _has_that_lemma.append(syn_norm)

            all_tokens_with_synonims.append(token_info)

    pprint(all_tokens_with_synonims)


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
