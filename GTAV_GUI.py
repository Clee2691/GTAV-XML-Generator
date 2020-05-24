import ped_xml_funcs
import sys


from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QScrollArea,
                                QTextEdit, QProgressBar, QFrame, QStyle, QLineEdit, QGridLayout, QSizePolicy, QComboBox)

from PyQt5.QtCore import Qt

class GtaGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def load_ped_database():
        pass

    def initUI(self):
        # setGeometry(x-pos, y-pos, width, height)
        self.setGeometry(800,200,350,300)
        self.setWindowTitle('GTA V XML Maker')

        # Widgets
        title_label = QLabel('GTAV Addon XML Creator')
        title_label.setFixedSize(320, 20) #w, h
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed) # width, height
        
        author_label = QLabel('By: Steeldrgn')
        author_label.setFixedSize(320, 20)
        author_label.setAlignment(Qt.AlignHCenter)
        author_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        ped_meta_textbox = QLineEdit()
        ped_meta_textbox.setPlaceholderText('PATH TO PED.YMT.XML')
        ped_meta_textbox.setAlignment(Qt.AlignHCenter)
        ped_meta_textbox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        ped_meta_btn = QPushButton('Load ped DB')
        ped_meta_btn.setFocus()

        ped_temp_label = QLabel('Choose a ped template: ')
        ped_temp_label.setAlignment(Qt.AlignHCenter)
        ped_temp_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        ped_temp_combo = QComboBox()
        ped_temp_combo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        data_scroll = QScrollArea()
        data_scroll.setWidgetResizable(True)
    
        # Layouts
        main_vlayout = QVBoxLayout()
        title_auth_vlayout = QVBoxLayout()
        load_ped_hlayout = QHBoxLayout()
        ped_template_hlayout = QHBoxLayout()
        data_form_layout = QFormLayout()
        
        # Add to layouts
        title_auth_vlayout.addWidget(title_label)
        title_auth_vlayout.addWidget(author_label)

        load_ped_hlayout.addWidget(ped_meta_textbox)
        load_ped_hlayout.addWidget(ped_meta_btn)

        ped_template_hlayout.addWidget(ped_temp_label)
        ped_template_hlayout.addWidget(ped_temp_combo)

        data_scroll.setLayout(data_form_layout)

        self.setLayout(main_vlayout)
        main_vlayout.addLayout(title_auth_vlayout)
        main_vlayout.addLayout(load_ped_hlayout)
        main_vlayout.addLayout(ped_template_hlayout)
        main_vlayout.addWidget(data_scroll)

        self.setFocus()
        self.show()

def main():
    app = QApplication([]) # QApplication allows sys args - cmdline arugments
    main_gui = GtaGUI()

    # Informs environment how application ended
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()