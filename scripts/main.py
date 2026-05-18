import sys

from PyQt5.QtWidgets import QApplication

from GUI.main_window import MainWindow
from GUI.gui_style import apply_app_font


def main():
    app = QApplication(sys.argv)

    apply_app_font(app, point_size=15)

    window = MainWindow()
    window.resize(1200, 900)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()