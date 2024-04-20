import time


def main(main_window):
    is_checked = main_window.HideConsoleCheckBox.isChecked()
    try:
        if is_checked:
            main_window.ConsoleLabel.hide()
            main_window.ButtonClearConsole.hide()
            main_window.TextConsoleView.hide()
        else:
            main_window.ConsoleLabel.show()
            main_window.ButtonClearConsole.show()
            main_window.TextConsoleView.show()

        main_window.open_second_window(ok_callback=lambda dialog: print(1), cancel_callback=lambda dialog: print(2))

    except Exception as e:
        print(e)
