import ped_xml_funcs
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class GTAVController:
    """ Controller class for GUI """

    def __init__(self, view):
        self.view = view
        self.conn_btn_signals()


    def conn_btn_signals(self):
        self.view.path_btn.clicked.connect(self.load_ped_db)
        self.view.template_load_btn.clicked.connect(self.pick_ped_template)
        self.view.generate_btn.clicked.connect(self.generate_xml)

    
    def load_ped_db(self):
        """ 
        Initial loading of the ped database
        """

        xml_path = self.view.get_ped_path_text()
        if xml_path == "":
            self.err_mess = 'PATH EMPTY'
            self.view.error_dialogs(self.err_mess)
            return

        # Load the ped database and any error messages
        self.ped_list, self.err_mess = ped_xml_funcs.ped_generator(xml_path)
        
        # Creates error dialog boxes if there are errors
        if self.err_mess:
            self.view.error_dialogs(self.err_mess)
        else:
            self.view.populate_ped_cbox(self.ped_list)
            self.view.template_load_btn.setDisabled(False)

            # Generate the attribute options with the ped list
            self.attr_db = ped_xml_funcs.attr_db(self.ped_list)

    def pick_ped_template(self):
        """
        Show params for the picked ped
        """
        current_ped = self.view.get_ped_template_text()

        if current_ped in self.attr_db['Name']:
            self.view.generate_ped_param_form(self.ped_list, self.attr_db, current_ped)
        else:
            self.view.error_dialogs('INVALID TEMPLATE', current_ped)

    def generate_xml(self):
        pass


class GTAVMainWindow(QMainWindow):
    """Main GUI"""

    def __init__(self):

        super().__init__()

        # Main window settings
        self.setWindowTitle('GTA V Addon XML Creator')
        # setGeometry(x-pos, y-pos, width, height)
        self.setGeometry(800,200,500,500)

        # Main layout
        self.main_layout = QVBoxLayout()
        
        # QMainwindow needs a central widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.main_layout)

        # Create gui elements
        self.create_title_labels()
        self.create_load_ped_xml()
        self.create_load_template()
        self.create_scroll_area()
        self.create_generate_btn()


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

        self.path_btn = QPushButton('Load Peds File')

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
        self.template_label = QLabel('Choose A Ped Template: ')
        self.template_label.setAlignment(Qt.AlignCenter)
        self.template_cbox = QComboBox()
        self.template_cbox.addItem('-----Choose A Ped-----')
        self.template_cbox.setCurrentIndex(0)
        self.template_cbox.setEditable(True)
        self.template_cbox.setInsertPolicy(QComboBox.NoInsert)
        self.template_cbox.setDisabled(True)

        self.template_load_btn = QPushButton('Load Template')
        self.template_load_btn.setDisabled(True)

        # Add widgets to self layout
        self.template_layout.addWidget(self.template_label)
        self.template_layout.addWidget(self.template_cbox)
        self.template_layout.addWidget(self.template_load_btn)

        # Add to the main layout
        self.main_layout.addLayout(self.template_layout)


    def create_scroll_area(self):
        """
        Scroll area for the ped params that can be edited
        """
        # Scroll area needs a widget - Set layout to the widget
        self.scroll_widget = QWidget()

        # Form layout for the widget
        self.form_layout = QFormLayout()
        self.scroll_widget.setLayout(self.form_layout)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        # Set it to the main layout
        self.main_layout.addWidget(self.scroll_area)


    def create_generate_btn(self):
        """
        Generate xml button layout
        """
        self.generate_btn = QPushButton('Generate XML')
        self.generate_btn.setFixedHeight(40)

        self.main_layout.addWidget(self.generate_btn)

    
    def populate_ped_cbox(self, ped_list):
        """
        Add all ped objects to the combo box
        Connects the load peds file button
        """
        for ped in ped_list:
            self.template_cbox.addItem(ped.Name)
        
        if self.template_cbox.count() > 1:
            self.template_cbox.setDisabled(False)


    def remove_params(self):
        """ 
        Clear out rows in form layout before repopulating
        """

        form_items = self.form_layout.rowCount()

        if form_items == 0:
            pass
        else:
            for item in reversed(range(form_items)):
                self.form_layout.removeRow(item)


    def generate_ped_param_form(self, ped_list, attr_dict, cur_ped_template):
        """
        Populate the scroll bar area with ped params
        Connects the Load Template button
        """

        if self.form_layout.rowCount() != 0:
            self.remove_params()
            print(self.form_layout.rowCount())

        cur_ped = None

        for ped in ped_list:
            if ped.Name.upper() == cur_ped_template.upper():
                cur_ped = ped
        
        for k, v in cur_ped.return_att_dict().items():
            # Allow editing of name
            if k == 'Name':
                self.form_layout.addRow(QLabel(k), QLineEdit(v))
            
            elif isinstance(v, list):
                pass
            elif isinstance(v, dict):
                param_label = QLabel(k)
                param_edit_line = QLineEdit(v['value'])

                self.form_layout.addRow(param_label, param_edit_line)

            elif isinstance(v, str):
                param_label = QLabel(k)

                if k in attr_dict.keys():
                    param_cbox = QComboBox()
                    param_cbox.addItems(attr_dict[k])
                    param_cbox.setEditable(True)
                    param_cbox.setInsertPolicy(QComboBox.NoInsert)
                    param_cbox.setCurrentText(v)
                    self.form_layout.addRow(param_label, param_cbox)

                else:
                    param_edit_line = QLineEdit(v)
                    self.form_layout.addRow(param_label, param_edit_line)
   

    def error_dialogs(self, error, other_message=None):
        """
        Error messages to be shown
        """
        if error == 'PATH EMPTY':
            QMessageBox.warning(self, error, 'ERROR: \nPath cannot be empty!')
        elif error == 'FILE NOT FOUND':
            QMessageBox.warning(self, error, 'ERROR: \nFile cannot be found. Are you pointing to the right place?')
        elif error == 'NOT VALID PEDS FILE':
            QMessageBox.warning(self, error, 'ERROR: \nNot a valid peds.ymt.xml or peds.meta file! Choose a different file!')
        elif error == 'INVALID TEMPLATE':
            QMessageBox.warning(self, error, f'ERROR: \n{other_message} is not a valid ped template.')
    
    
    def get_ped_path_text(self):
        return self.path_line_edit.text()
        

    def get_ped_template_text(self):
        return self.template_cbox.currentText()
    

def main():
    app = QApplication(sys.argv) # Can accept cmdline arguments
    app.setStyle('Fusion')

    # Main UI
    main_ui = GTAVMainWindow()
    main_ui.show()

    # Controller
    controller = GTAVController(view=main_ui)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()