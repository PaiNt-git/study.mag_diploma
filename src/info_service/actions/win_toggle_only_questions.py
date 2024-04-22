import time

from info_service import actions


def main(main_window):
    try:
        is_checked = main_window.OnlyQuestionsCheckBox.isChecked()

        if is_checked:
            main_window.MAINWINDOW_LOCAL_STORAGE['only_questions'] = True
        else:
            main_window.MAINWINDOW_LOCAL_STORAGE['only_questions'] = False

        actions.win_clearing_run(main_window)

    except Exception as e:
        print(e)

    # main_window.open_second_window(ok_callback=lambda dialog: print(1), cancel_callback=lambda dialog: print(2))
