from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QPlainTextEdit, QComboBox, \
	QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPixmap, QImage, QClipboard, QIcon
from PyQt5.QtCore import Qt, QByteArray, QBuffer

import requests
import sys

API_URL = 'https://telegraph-image-9gk.pages.dev/upload'
BASE_URL = 'https://telegraph-image-9gk.pages.dev'

LINK_FORMATS = {
	'URL': '{url}',
	'Markdown': '![]({url})',
	'HTML': '<img src="{url}" />',
	'UBB': '[img]{url}[/img]'
}


class ImageUploader(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Image Uploader')

		self.tray_icon = QSystemTrayIcon(self)
		self.tray_icon.setIcon(QIcon("icon.png"))  # Replace "icon.png" with your actual icon file

		show_action = QAction("Show", self)
		quit_action = QAction("Exit", self)
		hide_action = QAction("Hide", self)
		show_action.triggered.connect(self.show)
		hide_action.triggered.connect(self.hide)
		quit_action.triggered.connect(app.quit)
		tray_menu = QMenu()
		tray_menu.addAction(show_action)
		tray_menu.addAction(hide_action)
		tray_menu.addAction(quit_action)
		self.tray_icon.setContextMenu(tray_menu)
		self.tray_icon.show()

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.image_label = QLabel()
		self.layout.addWidget(self.image_label)
		self.upload_button = QPushButton('Upload Image')
		self.layout.addWidget(self.upload_button)
		self.link_area = QPlainTextEdit()
		self.link_area.setFixedHeight(50)
		self.layout.addWidget(self.link_area)
		self.link_format_combo = QComboBox()
		self.link_format_combo.addItems(LINK_FORMATS.keys())
		self.layout.addWidget(self.link_format_combo)
		self.upload_button.clicked.connect(self.upload_image)

		self.clear_button = QPushButton('Clear Image')
		self.layout.addWidget(self.clear_button)
		self.clear_button.clicked.connect(self.clear_image)

		self.clipboard = QApplication.clipboard()
		self.clipboard.dataChanged.connect(self.check_clipboard)
		self.image = None

	def check_clipboard(self):
		mime_data = self.clipboard.mimeData()
		if mime_data.hasImage():
			self.image = QPixmap.fromImage(QImage(mime_data.imageData()))
			self.image_label.setPixmap(self.image)

	def clear_image(self):
		self.image_label.clear()
		self.image = None

	def upload_image(self):
		try:
			byte_array = QByteArray()
			buffer = QBuffer(byte_array)
			self.image.save(buffer, 'PNG')
			image_bytes = byte_array.data()
			response = requests.post(API_URL, files={'file': ('image.png', image_bytes, 'image/png')})

			image_path = response.json()[0]['src']

			image_url = BASE_URL + image_path
			link_format = self.link_format_combo.currentText()
			link = LINK_FORMATS[link_format].format(url=image_url)
			self.link_area.setPlainText(link)
			self.clipboard.setText(link)
		except Exception as e:
			self.link_area.setPlainText(f'Error: {str(e)}')

	def closeEvent(self, event):
		event.ignore()
		self.hide()


if __name__ == "__main__":
	app = QApplication([])
	uploader = ImageUploader()
	uploader.show()
	sys.exit(app.exec_())
