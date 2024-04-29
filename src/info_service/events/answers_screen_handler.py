import sys
import time

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets


from info_service.db_base import Session, QuestAnswerBase,\
    QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service import actions
from info_service.actions._answers_utils import q_k_result_format_override,\
    update_entity
from info_service.db_utils import togudb_serializator


def main(main_window):

    def del_answer():
        actions.win_CRUD_del_instance(main_window, 'TableAllAnswers', QuestAnswerBase, 0, dialog_title='Удалить экземпляр')
        actions.win_answers_first_page(main_window)
        actions.win_lemms_first_page(main_window)
        pass
    ButtonDelAnswer = getattr(main_window, f'ButtonDelAnswer')
    ButtonDelAnswer.clicked.connect(del_answer)

    def new_answer():
        columns_ = OrderedDict(
            [
                ('questions', 'Вопросы \n(через точку с запятой)'),
                ('abstract', 'Контент\nАбстракт\nОтвет'),
            ])
        actions.win_CRUD_new_instance(main_window, QuestAnswerBase, columns_, 'Новое знание')
        actions.win_answers_first_page(main_window)
        actions.win_lemms_first_page(main_window)
        pass
    ButtonNewAnswer = getattr(main_window, f'ButtonNewAnswer')
    ButtonNewAnswer.clicked.connect(new_answer)

    def new_rquery():
        columns_1 = OrderedDict(
            [
                ('query', 'Запрос'),
            ])

        def ok_dialog(dialog):
            try:
                session = Session()

                answinstances = []
                table_main_widget = getattr(main_window, 'TableAllAnswers')
                cur_row = table_main_widget.currentRow()
                cur_rows = []

                selected = table_main_widget.selectedItems()
                if selected:
                    for item in selected:
                        rrow = item.row()
                        pk = int(table_main_widget.item(rrow, 0).text())
                        if pk and rrow not in cur_rows:
                            cur_rows.append(rrow)

                for cur_row in cur_rows:
                    cell_val = int(table_main_widget.item(cur_row, 0).text())
                    answinstance = session.query(QuestAnswerBase).get(cell_val)
                    answinstances.append(answinstance)

                table_widget = getattr(dialog, 'NewInstanceFields')

                cell_query = table_widget.item(0, 0).text()
                instance = session.query(QuestAnswerBaseRelevQuery).filter(QuestAnswerBaseRelevQuery.query == cell_query).first()
                if not instance:
                    instance = QuestAnswerBaseRelevQuery()

                def row_map_callback(x): return q_k_result_format_override(togudb_serializator(x, include=columns_1.keys(), exclude=['id']))

                has_notempty = False
                for i, key in enumerate(columns_1.keys()):
                    ret = update_entity(table_widget, session, instance, row_map_callback, 0, i, session_add=False)
                    if ret:
                        has_notempty = True

                if has_notempty:
                    session.add(instance)
                    session.flush()
                    session.commit()

                # Добавим релевантную связь
                for answinstance in answinstances:
                    relev_inst = session.query(QuestAnswerBaseRelevQueryRel).filter(QuestAnswerBaseRelevQueryRel.answer_id == answinstance.id,
                                                                                    QuestAnswerBaseRelevQueryRel.query_id == instance.id,
                                                                                    ).first()
                    if not relev_inst:
                        relev_inst = QuestAnswerBaseRelevQueryRel()

                    relev_inst.answer_id = answinstance.id
                    relev_inst.query_id = instance.id
                    relev_inst.relevantion_part = 1.0
                    session.add(relev_inst)
                    session.flush()
                    session.commit()

            except Exception as e:
                print(e)
            pass

        actions.win_CRUD_new_instance(main_window, QuestAnswerBaseRelevQuery, columns_1, 'Новый запрос', override_ok_dialog=ok_dialog)
        actions.win_relev_first_page(main_window)
        actions.win_relev_query_first_page(main_window)
        pass
    ButtonAddRelevQuery = getattr(main_window, f'ButtonAddRelevQuery')
    ButtonAddRelevQuery.clicked.connect(new_rquery)

    for crud_name in ('TableAllAnswers',):

        ButtonFirstPage = getattr(main_window, f'ButtonFirstPage{crud_name}')
        ButtonFirstPage.clicked.connect(lambda: actions.win_answers_first_page(main_window))

        ButtonLastPage = getattr(main_window, f'ButtonLastPage{crud_name}')
        ButtonLastPage.clicked.connect(lambda: actions.win_answers_last_page(main_window))

        ButtonNextPage = getattr(main_window, f'ButtonNextPage{crud_name}')
        ButtonNextPage.clicked.connect(lambda: actions.win_answers_next_page(main_window))

        ButtonsPrevPage = getattr(main_window, f'ButtonPrevPage{crud_name}')
        ButtonsPrevPage.clicked.connect(lambda: actions.win_answers_prev_page(main_window))

        columns = OrderedDict(
            [
                ('id', 'id'),
                ('questions', 'Вопросы \n(через точку с запятой)'),
                ('abstract', 'Контент\nАбстракт\nОтвет'),
            ])

        actions.win_CRUD_connect_edit(main_window, crud_name, columns, actions.db_list_entries(), row_map_callback=lambda x: q_k_result_format_override(togudb_serializator(x, include=columns.keys())))
