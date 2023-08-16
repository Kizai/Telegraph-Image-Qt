from PySide6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon, QAction, QShortcut, QKeySequence
from PySide6.QtWebEngineWidgets import QWebEngineView
from config import IMG_URL, LOGO_PATH
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(IMG_URL))
        self.setCentralWidget(self.browser)

        # Set the window size to 400*600
        self.resize(400, 600)

        # Create a status bar icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(LOGO_PATH))

        # Create context menu
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(app.quit)

        # Add a new action for navigating to another page
        manage_action = QAction("Manage", self)
        manage_action.triggered.connect(self.manage)

        tray_menu = QMenu()
        tray_menu.addAction(manage_action)  # Add the new action
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        # Show icon in system tray
        self.tray_icon.show()

        # Set up a shortcut to refresh the page on Ctrl+R
        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self.browser.reload)

    def manage(self):
        manage_url = IMG_URL + 'admin'  # Replace this with your actual management URL
        self.browser.setUrl(QUrl(manage_url))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
