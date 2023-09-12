import time
import json
import asyncio

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

from ipymarkup import format_span_box_markup, format_span_line_markup, format_dep_markup

from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

# from info_service import actions


from natasha.syntax import token_deps


def main(main_window):

    initial_query_text_widget = getattr(main_window, f'TextInitialQuery')
    initial_query_text = initial_query_text_widget.toPlainText()

    doc = Doc(initial_query_text)

    morph_vocab = MorphVocab()

    segmenter = Segmenter()

    emb = NewsEmbedding()

    ner_tagger = NewsNERTagger(emb)

    syntax_parser = NewsSyntaxParser(emb)

    doc.segment(segmenter)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)

    html_spans = format_span_line_markup(initial_query_text, doc.spans)

    html_syntax_tree = []

    for sentence in doc.sents:
        sent_tokens = sentence.tokens
        token_deps_ = token_deps(sent_tokens)
        html_syntax_tree.append(format_dep_markup([_.text for _ in sent_tokens], token_deps_))

    enreturn = ''

    enreturn += ('\n'.join(html_spans).replace('<div class="tex2jax_ignore" style="white-space: pre-wrap">', '<div class="tex2jax_ignore">'))

    enreturn += '<br><br><br><br>'

    for senthtmls in html_syntax_tree:

        sent_html = list(senthtmls)

        enreturn += ('\n'.join(sent_html) + '<br><br>')

    enreturn = '''
<!DOCTYPE HTML>
<html><head></head><body>

''' + enreturn + '''

</body></html>
'''

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


if __name__ == '__main__':

    initial_query_text = '''
Этого хватило, чтобы в зале воцарилась угнетающая тишина. Участники собрания, возможно, думали, что они находятся в каком-то дурном сне.

— Где ты раздобыл столько денег?

— Здание гильдий разве не общая зона?

— Откуда у тебя такая огромная сумма?!

— Это мы их проспонсировали, — ответил глава Океанических Систем Мититака «Сильные Руки». Его голос больше не дрожал, кажется, он быстрее всех оправился от потрясения.

— То есть предприятие возглавляете вы, Сироэ-доно...

— Да, и я собрал всех сегодня.

— Неудивительно.
    '''.strip()

    doc = Doc(initial_query_text)

    segmenter = Segmenter()

    emb = NewsEmbedding()

    ner_tagger = NewsNERTagger(emb)

    syntax_parser = NewsSyntaxParser(emb)

    doc.segment(segmenter)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)

    html_spans = format_span_line_markup(initial_query_text, doc.spans)

    html_syntax_tree = []

    for sentence in doc.sents:
        sent_tokens = sentence.tokens
        token_deps_ = token_deps(sent_tokens)
        html_syntax_tree.append(format_dep_markup([_.text for _ in sent_tokens], token_deps_))

    enreturn = ''

    enreturn += ('\n'.join(html_spans).replace('<div class="tex2jax_ignore" style="white-space: pre-wrap">', '<div class="tex2jax_ignore">'))

    enreturn += '<br><br><br><br>'

    for senthtmls in html_syntax_tree:

        sent_html = list(senthtmls)

        enreturn += ('\n'.join(sent_html) + '<br><br>')

    enreturn = '''
<!DOCTYPE HTML>
<html><head></head><body>

''' + enreturn + '''

</body></html>
'''

    print(enreturn)
