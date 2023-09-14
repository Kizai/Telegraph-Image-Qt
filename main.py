#!/usr/bin/python3
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QPlainTextEdit, QComboBox, \
    QSystemTrayIcon, QMenu, QAction, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QClipboard, QIcon, QPixmap, QMovie
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QTimer
import re
import os
import requests
import sys
import sqlite3

LINK_FORMATS = {
    'URL': '{url}',
    'Markdown': '![]({url})',
    'HTML': '<img src="{url}" />',
    'UBB': '[img]{url}[/img]'
}


class ImageUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Telegraph-Image Uploader')

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon/logo.png"))

        self.image_format = None
        self.movie = None
        self.image_path = None

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        # select_image_action = QAction("Select Image", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        # select_image_action.triggered.connect(self.select_image)
        quit_action.triggered.connect(app.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        # tray_menu.addAction(select_image_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        self.layout.addWidget(self.image_label)

        self.select_button = QPushButton('Select File(png/jpg/gif/jpeg)')
        self.select_button.setStyleSheet("background-color: blue; color: white;")
        self.layout.addWidget(self.select_button)
        self.select_button.clicked.connect(self.select_image)

        self.upload_button = QPushButton('Upload Image')
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: green; 
                color: white;
            }
            QPushButton:disabled {
                background-color: gray; 
                color: black;
            }
        """
                                         )
        self.layout.addWidget(self.upload_button)

        self.upload_gif_button = QPushButton('Upload GIF')
        self.upload_gif_button.setStyleSheet("""
            QPushButton {
                background-color: green; 
                color: white;
            }
            QPushButton:disabled {
                background-color: gray; 
                color: black;
            }
        """
                                             )
        self.layout.addWidget(self.upload_gif_button)
        self.upload_gif_button.clicked.connect(self.upload_gif)

        self.link_area = QPlainTextEdit()
        self.link_area.setFixedHeight(50)
        self.layout.addWidget(self.link_area)

        self.link_format_combo = QComboBox()
        self.link_format_combo.setStyleSheet("background-color: orange; color: white;")
        self.link_format_combo.addItems(LINK_FORMATS.keys())
        self.layout.addWidget(self.link_format_combo)
        self.upload_button.clicked.connect(self.upload_image)

        self.clear_button = QPushButton('Clear Image')
        self.clear_button.setStyleSheet("background-color: red; color: white;")
        self.layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.clear_image)

        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.check_clipboard)
        self.image = None

        self.link_format_combo.currentIndexChanged.connect(self.update_link_format)

        self.set_api_button = QPushButton('Set API URL')
        self.layout.addWidget(self.set_api_button)
        self.set_api_button.clicked.connect(self.set_api_url)

        # Check the database for an saved API URL
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Settings (Key TEXT PRIMARY KEY, Value TEXT)")
        result = cursor.execute("SELECT Value FROM Settings WHERE Key='API_URL'").fetchone()
        if result is None:
            # No API URL found in the database, prompt the user to set one
            QMessageBox.warning(self, 'Warning', 'Please set an API URL to continue.')
            self.set_api_url()
        else:
            # Found an API URL in the database, use it
            global API_URL
            API_URL = result[0]
        conn.close()

    def select_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName()

        if image_path:
            self.image_path = image_path
            _, file_extension = os.path.splitext(image_path)
            self.image_format = file_extension[1:].upper()  # remove the leading '.' and convert to uppercase

            # Disable/enable the upload buttons based on the file format
            is_gif = self.image_format == 'GIF'
            self.upload_button.setDisabled(is_gif)
            self.upload_gif_button.setDisabled(not is_gif)

            # Create a QPixmap or QMovie based on the file format
            if is_gif:
                self.image = None
                self.movie = QMovie(image_path)
                self.image_label.setMovie(self.movie)
                self.movie.start()
            else:
                self.image = QPixmap(image_path)
                self.movie = None
                self.image_label.setPixmap(self.image.scaled(800, 600, Qt.KeepAspectRatio))

            self.image_label.adjustSize()
            QTimer.singleShot(0, lambda: self.adjustSize())

    def set_api_url(self):
        new_api_url, ok = QInputDialog.getText(self, 'Set API URL', 'Enter new API URL:')
        if ok:
            # User entered a new API URL and clicked OK, save it to the database
            conn = sqlite3.connect('settings.db')
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO Settings (Key, Value) VALUES (?, ?)", ('API_URL', new_api_url))
            conn.commit()
            conn.close()

            # Update the global API_URL variable
            global API_URL
            API_URL = new_api_url

            QMessageBox.information(self, 'Success', 'API URL set successfully.')
        else:
            QMessageBox.warning(self, 'Warning', 'Failed to set API URL.')

    def upload_image(self):
        try:
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)

            self.image.save(buffer, self.image_format)  # use self.image_format

            image_bytes = byte_array.data()
            content_type_mapping = {
                'PNG': 'image/png',
                'JPEG': 'image/jpeg',
                'JPG': 'image/jpeg',
            }
            content_type = content_type_mapping.get(self.image_format,
                                                    'image/jpeg')  # default to jpeg if format is not recognized

            response = requests.post(API_URL + '/upload',
                                     files={'file': ('image.' + self.image_format.lower(), image_bytes, content_type)})

            image_path = response.json()[0]['src']

            image_url = API_URL + image_path
            link_format = self.link_format_combo.currentText()
            link = LINK_FORMATS[link_format].format(url=image_url)
            self.link_area.setPlainText(link)
            self.clipboard.setText(link)
        except Exception as e:
            self.link_area.setPlainText(f'Error: {str(e)}')

    def upload_gif(self):
        try:
            if self.image_path:
                with open(self.image_path, "rb") as f:
                    image_data = f.read()

                content_type = 'image/gif'
                response = requests.post(API_URL + '/upload',
                                         files={'file': ('image.gif', image_data, content_type)})

                image_path = response.json()[0]['src']

                image_url = API_URL + image_path
                link_format = self.link_format_combo.currentText()
                link = LINK_FORMATS[link_format].format(url=image_url)
                self.link_area.setPlainText(link)
                self.clipboard.setText(link)
        except Exception as e:
            self.link_area.setPlainText(f'Error: {str(e)}')

    def update_link_format(self):
        link_text = self.link_area.toPlainText()
        if not link_text:
            return

        # extract the URL from the current link text
        url_match = re.search(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.(png|jpg|gif|jpeg)',
            link_text)
        if not url_match:
            return  # no valid URL found in the current link text

        url = url_match.group()

        # format the extracted URL using the new format
        new_format = self.link_format_combo.currentText()
        new_link = LINK_FORMATS[new_format].format(url=url)
        self.link_area.setPlainText(new_link)

    def check_clipboard(self):
        mime_data = self.clipboard.mimeData()
        if mime_data.hasImage():
            self.image = QPixmap.fromImage(QImage(mime_data.imageData()))
            self.image_label.setPixmap(self.image.scaled(800, 600, Qt.KeepAspectRatio))  # display the scaled image
            self.image_label.adjustSize()  # adjust the QLabel size to fit the new image

            self.upload_button.setEnabled(True)  # Enable the 'Upload Image' button
            self.upload_gif_button.setEnabled(False)  # Disable the 'Upload GIF' button

            self.image_format = "PNG"  # Set a default image format for clipboard images

            QTimer.singleShot(0, lambda: self.adjustSize())  # adjust the QWidget size after a brief delay

    def clear_image(self):
        self.image_label.clear()
        self.image = None
        self.movie = None
        self.link_area.clear()

        self.upload_button.setEnabled(True)  # Enable the button when the image is cleared
        self.upload_gif_button.setEnabled(True)  # Also enable the gif upload button

        QTimer.singleShot(0, lambda: self.adjustSize())  # Adjust the QWidget size after a brief delay

    def closeEvent(self, event):
        event.ignore()
        self.hide()


if __name__ == "__main__":
    app = QApplication([])
    uploader = ImageUploader()
    uploader.show()
    sys.exit(app.exec_())
