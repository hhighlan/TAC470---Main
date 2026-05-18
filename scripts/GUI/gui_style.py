from PyQt5.QtGui import QFont


def apply_app_font(app, point_size=15):
    font = QFont()
    font.setPointSize(point_size)
    app.setFont(font)


def get_main_stylesheet():
    return """
        QLabel {
            color: #2c3e50;
        }

        QLabel#statusLabel {
            color: red;
        }

        QPushButton {
            padding: 6px;
        }

        QComboBox {
            padding: 4px;
        }

        QToolTip {
        font-size: 13px;
        padding: 8px;
        }
    """