import time

from info_service import actions


def main(main_window):
    # Очистим все поля в запросах
    main_window.TextInitialQuery.clear()
    main_window.TextModifiedQuery.clear()
    main_window.LabelPostgresQueryLexStemming.setText('')
    main_window.TextQuerySynonims.setText('')
    main_window.LabelInitialQuery.setText('')
    main_window.LabelModifiedQuery.setText('')

    # Таблица
    main_window.TableInitialQueryExceptedTokens.clear()
    main_window.TableInitialQueryExceptedTokens.setRowCount(0)

    # HTML окно
    initial_query_analysis_widget = getattr(main_window, f'WebViewAnalysisPreview')
    initial_query_analysis_widget.setHtml('<!DOCTYPE HTML><html><head></head><body></body></html>')

    # Перегрузить все леммы
    actions.win_lemms_first_page(main_window)
