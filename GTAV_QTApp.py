import ped_xml_funcs
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class GTAVController:
    """ 
    Controller class for GUI
    Connects the buttons/ defines the functions each button does
    Passes gui creation to main gui class
    """

    def __init__(self, view):
        self.view = view
        self.conn_btn_signals()


    def conn_btn_signals(self):
        self.view.path_btn.clicked.connect(self.load_ped_db)
        self.view.template_load_btn.clicked.connect(self.pick_ped_template)
        self.view.generate_btn.clicked.connect(self.generate_xml)
        self.view.tree.doubleClicked.connect(self.dir_view_select)


    def dir_view_select(self, index):
        """ 
        Update path_line_edit field with valid peds meta or xml file 
        QTreeView.doubleclicked event passes QModelIndex object as a parameter
        """
        # Need a temp QFileSystemModel as filePath() method is accessible from that class and NOT QModelIndex class
        temp_model = QFileSystemModel()
        valid_file_types = ['xml File', 'meta File']

        # Get the filepath - index = QModelIndex object
        file_path = temp_model.filePath(index)

        # Returns a string displaying type of file
        file_type = temp_model.type(index)
        
        # Determine if it is a file not directory
        # fileInfo returns a QFileInfo object
        file_isFile = temp_model.fileInfo(index).isFile()
        
        if file_isFile and file_type in valid_file_types:
            self.view.set_ped_file_path(file_path)
    

    def load_ped_db(self):
        """ 
        Initial loading of the ped database
        """
        self.view.clear_combo_box()

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
            QMessageBox.information(QWidget(), 'SUCCESS','Ped DB Loaded!\nChoose a ped template to get started.')

    def pick_ped_template(self):
        """
        Show params for the picked ped
        """
        current_ped_text = self.view.get_ped_template_text()

        if current_ped_text in self.attr_db['Name']:

            self.cur_ped = None

            for ped in self.ped_list:
                if ped.Name.upper() == current_ped_text.upper():
                    self.cur_ped = ped

            self.view.generate_ped_param_form(self.attr_db, self.cur_ped)

        else:
            self.view.error_dialogs('INVALID TEMPLATE', current_ped_text)

        return self.cur_ped

    def generate_xml(self):

        if self.view.form_layout.count() == 0:
            self.view.error_dialogs('NO PED INFO', 'No ped template found to generate xml!')
            return

        new_val_dict = {}

        for param in range(self.view.form_layout.rowCount()):
            # itemAt(row, column) - column index [0(Label), 1(Lineedit/combobox)]
            row_label = self.view.form_layout.itemAt(param, 0).widget().text()
            row_param_widget = self.view.form_layout.itemAt(param, 1).widget()

            if isinstance(row_param_widget, QLineEdit):
                new_val_dict[row_label] = row_param_widget.text()

            elif isinstance(row_param_widget, QComboBox):
                new_val_dict[row_label] = row_param_widget.currentText()
        
        custom_ped, err_mess = ped_xml_funcs.generate_new_ped(self.cur_ped, new_val_dict)

        if not err_mess:
            ped_xml_funcs.ped_xml_writer(custom_ped)
            QMessageBox.information(QWidget(), 'SUCCESS', 'SUCCESS:\nCheck peds.meta file for the custom ped!')
        else:
            self.view.error_dialogs(err_message, 'ERROR:\nCustom ped generation failed! Try again.')


class GTAVMainWindow(QMainWindow):
    """Main GUI"""

    def __init__(self):

        super().__init__()

        # Main window settings
        self.setWindowTitle('GTA V Addon XML Creator')
        # setGeometry(x-pos, y-pos, width, height)
        self.setGeometry(800,200,715,500)

        self.q_split = QSplitter()

        # Main layout
        self.main_layout = QHBoxLayout()

        # Widget for splitter
        self.app_widget = QWidget()
        
        # QMainwindow needs a central widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.main_layout)

        # Create gui elements
        # Create the directory view first and add to main layout
        self.create_dir_view()
        #self.main_layout.addLayout(self.dir_layout)

        # App Layout
        self.app_layout = QVBoxLayout()

        # Create the rest of the gui and add to main layout
         
        self.create_title_labels()
        self.create_load_ped_xml()
        self.create_load_template()
        self.create_scroll_area()
        self.create_generate_btn()
        
        self.app_widget.setLayout(self.app_layout)
        self.q_split.addWidget(self.app_widget)
        
        self.main_layout.addWidget(self.q_split)


    def create_dir_view(self):
        # Set up the model/ widget
        self.model = QFileSystemModel()
        self.model.setRootPath('')

        # Treeview object needs a model set to it
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        # Set up the tree view
        self.tree.setIndentation(15)
        self.tree.setSortingEnabled(False)
        self.tree.setColumnWidth(0, 150) # Dir Name Column (Column, size)
        self.tree.setColumnWidth(1, 30) # Size Column
        self.tree.setColumnWidth(2, 30) # File type column

        self.q_split.addWidget(self.tree)
        

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

        # Add to app layout
        self.app_layout.addLayout(self.title_layout)


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
        self.app_layout.addLayout(self.load_ped_xml_layout)
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
        self.app_layout.addLayout(self.template_layout)


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
        self.app_layout.addWidget(self.scroll_area)


    def create_generate_btn(self):
        """
        Generate xml button layout
        """
        self.generate_btn = QPushButton('Generate XML')
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setDisabled(True)

        self.app_layout.addWidget(self.generate_btn)

    
    def populate_ped_cbox(self, ped_list):
        """
        Add all ped objects to the combo box
        Connects the load peds file button
        """
        for ped in ped_list:
            self.template_cbox.addItem(ped.Name)
        
        if self.template_cbox.count() > 1:
            self.template_cbox.setDisabled(False)


    def generate_ped_param_form(self, attr_dict, cur_ped_template):
        """
        Populate the scroll bar area with ped params
        Connects the Load Template button
        """

        self.remove_params()
        
        for k, v in cur_ped_template.return_att_dict().items():
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

        self.generate_btn.setDisabled(False)

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
        elif error == 'NO PED INFO':
            QMessageBox.warning(self, error, other_message)
        elif error == 'GENERATE FAILED':
            QMessageBox(self, error, other_message)
    
    def remove_params(self):
        """ 
        Clear out rows in form layout before repopulating
        """

        form_items = self.form_layout.rowCount()

        if form_items == 0:
            return
        else:
            for item in reversed(range(form_items)):
                self.form_layout.removeRow(item)

    def clear_combo_box(self):
        if self.template_cbox.count() > 1:
            self.template_cbox.clear()
            self.remove_params()
            self.template_cbox.addItem('-----Choose A Ped-----')
            self.template_cbox.setCurrentIndex(0)
    
    def get_ped_path_text(self):
        return self.path_line_edit.text()

    def set_ped_file_path(self, file_path):
        self.path_line_edit.setText(file_path)        

    def get_ped_template_text(self):
        return self.template_cbox.currentText()

    
def main():
    app = QApplication(sys.argv) # Can accept cmdline arguments
    app.setStyle('Fusion')

    # Set Fusion style to be dark  themed
    # Palette has 3 groups: Active, inactive, disabled
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15,15,15))
    palette.setColor(QPalette.Disabled, QPalette.Base, QColor(40, 40, 40))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.Text, Qt.gray)
    palette.setColor(QPalette.Button, QColor(53,53,53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.gray)

    app.setPalette(palette)

    # Main UI
    main_ui = GTAVMainWindow()
    main_ui.show()

    # Controller
    controller = GTAVController(view=main_ui)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()