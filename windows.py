import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pathlib import Path
import json
import cellcounter

home_dir = str(Path.home())

class DriverWindow(QMainWindow):
	"""
	Main window that links together all other windows. Should
	remain hidden at all times.
	"""
	def __init__(self):
		super(QMainWindow, self).__init__()

		self.upload_window = FileUploadWindow()
		self.result_window = None		

		self.image_path = None
		self.image_object = None
		self.results = dict.fromkeys([
									"num_cells",
									"cell_contours"
									# TODO: implement other results
									#  - photoswitching index
									#  - dendritic connections
									#  - dendritic activity 
									])

	def run(self):
		loop = QEventLoop()
		self.upload_window.finished_signal.connect(loop.quit)
		self.upload_window.show()
		loop.exec_()

		self.image_path = self.upload_window.image_path
		self.image_object = cellcounter.Image(self.image_path)

		self.results["num_cells"] = self.image_object.num_cells

		#OpenCV contour format
		self.results["cell_contours"] = [s.contour.tolist() for s in self.image_object.somas]

		self.result_window = ResultsWindow(self.results)
		self.result_window.show()



class FileUploadWindow(QMainWindow):
	"""
	Window for selecting image file. The parameter image_path
	contains the image file selected by the window.
	"""

	finished_signal = pyqtSignal()

	def __init__(self):
		super(QMainWindow, self).__init__()


		self.image_path = None


		self.setWindowTitle("Cell Counter")

		box = QVBoxLayout()
		box.setAlignment(Qt.AlignCenter)

		button = QPushButton("Import")
		button.clicked.connect(self.__on_click)
		box.addWidget(button, alignment=Qt.AlignCenter)

		tip = QLabel()
		tip.setText("NOTE: This program currently only supports PNG files.")
		box.addWidget(tip, alignment=Qt.AlignCenter)


		main_widget = QWidget()
		main_widget.setLayout(box)
		self.setCentralWidget(main_widget)


	def __on_click(self):
		self.image_path = QFileDialog.getOpenFileName(self, 'Select image',
													 home_dir, "PNG files (*.png)")[0]
		self.close()
		self.finished_signal.emit()
		

class ResultsWindow(QMainWindow):
	"""
	Window for displaying results of image analysis.
	"""

	def __init__(self, results):
		super(QMainWindow, self).__init__()
		self.results = results

		self.setWindowTitle("Results")

		box = QVBoxLayout()
		box.setAlignment(Qt.AlignCenter)


		original_image = QLabel()
		pixmap_1 = QPixmap("data/images/original_image.png")
		pixmap_1 = pixmap_1.scaledToWidth(pixmap_1.width() * 4)
		original_image.setPixmap(pixmap_1)
		box.addWidget(original_image, alignment=Qt.AlignCenter)

		result_image = QLabel()
		pixmap_2 = QPixmap("data/images/final_image.png")
		pixmap_2 = pixmap_2.scaledToWidth(pixmap_2.width() * 4)
		result_image.setPixmap(pixmap_2)
		box.addWidget(result_image, alignment=Qt.AlignCenter)

		image_key_text = QLabel()
		image_key_text.setText("KEY:\nWhite - Dendrite\nPink - Soma\nBlack - Background")
		box.addWidget(image_key_text, alignment=Qt.AlignCenter)

		cell_num_text = QLabel()
		cell_num_text.setText("\nCells detected: " + str(results["num_cells"]))
		box.addWidget(cell_num_text, alignment=Qt.AlignCenter)

		main_widget = QWidget()
		main_widget.setLayout(box)
		self.setCentralWidget(main_widget)

		self.__export_json()

	def __export_json(self):
		with open('data/results.json', 'w+') as dest_file:
			json.dump(self.results, dest_file)



if __name__ == '__main__':
	# For debugging purposes 

	app = QApplication(sys.argv)

	window = DriverWindow()
	window.show() #windows hidden by default


	# Start the event loop.
	app.exec_()

	print(window.image_path)

