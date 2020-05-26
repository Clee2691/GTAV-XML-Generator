import ped_xml_funcs
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class GTAVMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window settings
        self.setWindowTitle('GTA V Addon XML Creator')
        # setGeometry(x-pos, y-pos, width, height)
        self.setGeometry(800,200,350,500)

        # Main layout
        self.main_layout = QVBoxLayout()
        
        # QMainwindow needs a central widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.main_layout)

        self.create_title_labels()
        self.create_load_ped_xml()
        self.create_load_template()
        self.create_scroll_area()

    def create_title_labels(self):
        # Layout
        self.title_layout = QVBoxLayout()

        # Labels
        self.title_label = QLabel('GTA V Addon XML Creator')
        self.title_label.setFixedHeight(25)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.author_label = QLabel('By: Steeldrgn')
        self.author_label.setFixedHeight(25)
        self.author_label.setAlignment(Qt.AlignCenter)

        # Add labels to layout
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.author_label)

        # Add to main layout
        self.main_layout.addLayout(self.title_layout)

    def create_load_ped_xml(self):
        # Layout
        self.load_ped_xml_layout = QHBoxLayout()
        
        # Widgets
        self.path_line_edit = QLineEdit()
        self.path_line_edit.setPlaceholderText('PATH TO PEDS.YMT.XML FILE')
        self.path_line_edit.setAlignment(Qt.AlignCenter)

        self.path_btn = QPushButton('Load peds')

        # Add to self layout
        self.load_ped_xml_layout.addWidget(self.path_line_edit)
        self.load_ped_xml_layout.addWidget(self.path_btn)

        # Add the main layout
        self.main_layout.addLayout(self.load_ped_xml_layout)
        self.path_btn.setFocus()

    def create_load_template(self):
        # layout
        self.template_layout = QHBoxLayout()

        # Widgets
        self.template_label = QLabel('Choose a ped template: ')
        self.template_label.setAlignment(Qt.AlignCenter)
        self.template_cbox = QComboBox()

        # Add the self layout
        self.template_layout.addWidget(self.template_label)
        self.template_layout.addWidget(self.template_cbox)

        # Add to the main layout
        self.main_layout.addLayout(self.template_layout)
    
    def create_scroll_area(self):
        # layout
        self.form_layout = QFormLayout()

        # Widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setLayout(self.form_layout)

        # Set it to the main layout
        self.main_layout.addWidget(self.scroll_area)
        

def main():
    app = QApplication(sys.argv) # Can accept cmdline arguments
    app.setStyle('Fusion')

    main_ui = GTAVMainWindow()
    main_ui.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()