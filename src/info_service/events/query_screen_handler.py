import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service import actions
from info_service.db_base import QuestAnswerBaseRelevQuery, Session


def main(main_window):

    ButtonExecuteInitialQuery = main_window.ButtonExecuteInitialQuery

    def _execute_initial_query():
        actions.win_initial_query_pg_stemming(main_window)
        actions.win_initial_query_refresh_label(main_window)
        actions.win_initial_query_first_page(main_window)
    ButtonExecuteInitialQuery.clicked.connect(_execute_initial_query)

    ButtonExecuteModifiedQuery = main_window.ButtonExecuteModifiedQuery

    def _execute_modified_query():
        actions.win_modified_query_refresh_label(main_window)
        actions.win_modified_query_first_page(main_window)
    ButtonExecuteModifiedQuery.clicked.connect(_execute_modified_query)

    ButtonClearAllQueryScreen = main_window.ButtonClearAllQueryScreen

    def _clear_all_queries():
        initial_query_text_widget = main_window.TextInitialQuery
        initial_query_text_widget.setPlainText('')
        modified_query_text_widget = main_window.TextModifiedQuery
        modified_query_text_widget.setPlainText('')
        main_window.TextQuerySynonims.setText('')
        initial_query_analysis_widget = getattr(main_window, f'WebViewAnalysisPreview')
        initial_query_analysis_widget.setHtml('')
        _execute_initial_query()
        _execute_modified_query()
    ButtonClearAllQueryScreen.clicked.connect(_clear_all_queries)

    ButtonAddQueryToList = main_window.ButtonAddQueryToList

    def _add_query_to_list():
        session = Session()
        initial_query_text_widget = getattr(main_window, f'TextInitialQuery')
        initial_query_text = initial_query_text_widget.toPlainText()
        instance = session.query(QuestAnswerBaseRelevQuery).filter(QuestAnswerBaseRelevQuery.query == initial_query_text).first()
        if not instance:
            instance = QuestAnswerBaseRelevQuery()

        instance.query = initial_query_text
        session.add(instance)
        session.flush()
        session.commit()
        actions.win_relev_first_page(main_window)
        actions.win_relev_query_first_page(main_window)
    ButtonAddQueryToList.clicked.connect(_add_query_to_list)

    ButtonAnalysisInitialQuery = main_window.ButtonAnalysisInitialQuery
    ButtonAnalysisInitialQuery.clicked.connect(lambda x: actions.win_initial_query_syntax_analysis(main_window))

    ButtonHighlightSynonyms = main_window.ButtonHighlightSynonyms
    ButtonHighlightSynonyms.clicked.connect(lambda x: actions.win_initial_query_highlight_synonyms(main_window))

    OptimizeQueryButton = main_window.OptimizeQueryButton
    OptimizeQueryButton.clicked.connect(lambda x: actions.win_initial_query_optimize_query(main_window))
