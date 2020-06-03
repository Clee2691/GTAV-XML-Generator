from functions import ped_xml_funcs, weapons_xml_funcs
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import lxml.etree as LET

APP_VERSION = 1.0


class GTAVController:
    """ 
    Controller class for GUI
    Connects the buttons/ defines the functions each button does
    Passes gui creation to main gui class
    """

    def __init__(self, view):
        self.view = view
        self.conn_btn_signals()
        self.create_menu_actions()

    def conn_btn_signals(self):
        self.view.path_btn.clicked.connect(self.load_ped_db)
        self.view.template_load_btn.clicked.connect(self.pick_ped_template)
        self.view.generate_btn.clicked.connect(self.generate_xml)

        self.view.tree.doubleClicked.connect(self.dir_view_select)
        self.view.tab_area.tabCloseRequested.connect(self.close_tab)
        self.view.tab_area.tabBarDoubleClicked.connect(self.tab_rename)

    # Menu actions
    def create_menu_actions(self):
        # File menu section
        self.view.load_action = QAction("Load file", self.view)
        self.view.menu_file.addAction(self.view.load_action)
        self.view.load_action.triggered.connect(self.load_file_dialog)

        self.view.exit_action = QAction("Exit", self.view)
        self.view.menu_file.addAction(self.view.exit_action)
        self.view.exit_action.triggered.connect(self.view.closeEvent)

        # Help menu section
        self.view.help_action = QAction("Help", self.view)
        self.view.about_action = QAction("About", self.view)
        self.view.menu_help.addAction(self.view.help_action)
        self.view.help_action.triggered.connect(self.help_dialog)
        self.view.menu_help.addAction(self.view.about_action)
        self.view.about_action.triggered.connect(self.about_dialog)

    def help_dialog(self):
        self.help_dialog = QDialog()
        self.help_dialog.setMinimumSize(500, 500)
        self.help_dialog.setMaximumSize(800, 500)
        self.help_dialog.setWindowTitle("Help - How To")

        # Layout
        self.help_layout = QVBoxLayout()
        self.help_label = QLabel()

        self.help_text = """ <html> <body style=" font-family:'Arial'; font-size:10pt; font-weight:400; font-style:normal;">
        <h1 align="center">Help - How To Use</h1>
        <dl>
        <dt>Step 1. Load Ped File</dt>
        <dd>- Select a peds meta or XML file either through the file browser or file menu and press load.</dd><br>
        <dt>Step 2. Pick Ped Template</dt>
        <dd>- Once the database is loaded, pick a ped template to start editing the parameters.</dt><br>
        <dt>Step 3. Edit Ped Parameters</dt>
        <dd>Edit the parameters you want and press generate meta file.</dd><br>
        <dt>Step 4. Locate File</dt>
        <dd>Check peds_xml_files folder for the generated meta file.</dd><br>
        <dt>Step 5. Enjoy!</dt>
        <dd>Place file in desired location and enjoy your addon ped!</dd><br>
        </ol>
        </body>
        </html>
        """

        self.help_label.setText(self.help_text)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.help_dialog.accept)

        self.help_layout.addWidget(self.help_label)
        self.help_layout.addWidget(self.button_box)
        self.help_dialog.setLayout(self.help_layout)

        self.help_dialog.exec_()

    def about_dialog(self):
        self.about_dialog = QDialog()
        self.about_dialog.setWindowTitle("ABOUT GTA V META CREATOR")
        self.about_dialog.setSizeGripEnabled(True)

        about_text = f""" 
        <html> 
        <body style=" font-family:'Arial'; font-size:10pt; font-weight:400; font-style:normal;">
        <h1 align="center">GTA V Addon META Creator V{APP_VERSION}</h1>
        <h3 align="center"> Author: Steeldrgn \u00A92020</h3>
        </body>
        </html>
        """
        # layout
        self.about_layout = QVBoxLayout()

        self.about_label = QLabel()
        self.about_label.setText(about_text)

        self.about_ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
        self.about_ok_btn.accepted.connect(self.about_dialog.accept)

        self.about_layout.addWidget(self.about_label)
        self.about_layout.addWidget(self.about_ok_btn)

        self.about_dialog.setLayout(self.about_layout)
        self.about_dialog.exec_()

    def load_file_dialog(self):
        self.load_file_dialog = QFileDialog()
        file_path, _ = self.load_file_dialog.getOpenFileName(
            self.view,
            "Load Peds META or XML File",
            "./database",
            "XML, META Files (*.meta *.xml)",
            "",
        )
        self.view.set_ped_file_path(file_path)

    def dir_view_select(self, index):
        """ 
        Update path_line_edit field with valid peds meta or xml file 
        QTreeView.doubleclicked event passes QModelIndex object as a parameter
        """

        # Get the filepath - index = QModelIndex object -> model() return QFileSystemModel object
        file_path = index.model().filePath(index)

        # Returns a string displaying type of file
        file_type = index.model().type(index)

        # Determine if it is a file not directory
        # fileInfo returns a QFileInfo object
        file_isFile = index.model().fileInfo(index).isFile()

        self.view.set_ped_file_path(file_path)

    def load_ped_db(self):
        """ 
        Initial loading of the ped database
        """
        self.view.clear_combo_box()

        xml_path = self.view.get_ped_path_text()
        if xml_path == "":
            self.err_mess = "PATH EMPTY"
            self.view.error_dialogs(self.err_mess)
            return

        # Load the ped database and any error messages
        self.ped_list, self.err_mess = ped_xml_funcs.ped_generator(xml_path)

        # Creates error dialog boxes if there are errors
        if self.err_mess:
            self.view.error_dialogs(self.err_mess)
        else:
            self.view.populate_cbox(self.ped_list)
            self.view.template_load_btn.setDisabled(False)

            # Generate the attribute options with the ped list
            self.attr_db = ped_xml_funcs.attr_db(self.ped_list)
            # QMessageBox.information(QWidget(), 'SUCCESS','Ped DB Loaded!\nChoose a ped template to get started.')
            self.view.statusBar().showMessage(
                "Success! Ped DB Loaded! Choose a ped template to get started!", 0
            )

    def pick_ped_template(self):
        """
        Show params for the picked ped
        """
        current_ped_text = self.view.get_ped_template_text()

        if current_ped_text in self.attr_db["Name"]:

            self.cur_ped = None

            for ped in self.ped_list:
                if ped.Name.upper() == current_ped_text.upper():
                    self.cur_ped = ped

            self.view.generate_ped_param_form(self.attr_db, self.cur_ped)

        else:
            self.view.error_dialogs("INVALID TEMPLATE", current_ped_text)

        return self.cur_ped

    def generate_xml(self):

        if self.view.form_layout.count() == 0:
            self.view.error_dialogs(
                "NO PED INFO", "No ped template found to generate META file!"
            )
            return

        new_val_dict = {}

        for param in range(self.view.form_layout.rowCount()):
            # itemAt(row, column) - column index [0(Label), 1(Lineedit/combobox)]
            row_label = self.view.form_layout.itemAt(param, 0).widget().text()
            row_param_widget = self.view.form_layout.itemAt(param, 1).widget()

            if isinstance(row_param_widget, QLineEdit):
                new_val_dict[row_label] = row_param_widget.text()

            elif isinstance(row_param_widget, QComboBox) or isinstance(
                row_param_widget, QLabel
            ):
                # Added children to XML tag if it has any
                # Manual adding of HasChildren and Item in label generation
                cur_label = row_label.split(" ")[0]
                if "HasChildren" in row_label:
                    new_val_dict[cur_label] = []
                elif "Item" in row_label:
                    new_val_dict[cur_label].append(row_param_widget.currentText())
                else:
                    new_val_dict[row_label] = row_param_widget.currentText()

        custom_ped, err_mess = ped_xml_funcs.generate_new_ped(
            self.cur_ped, new_val_dict
        )

        if not err_mess:
            save_path = "."

            save_dialog = QFileDialog(self.view)
            save_path = save_dialog.getExistingDirectory(
                self.view, "Save Location", ".", QFileDialog.DontUseNativeDialog
            )
            if save_path == "":
                save_path = "."
            ped_xml_funcs.ped_xml_writer(custom_ped, save_path)

            QMessageBox.information(
                QWidget(),
                "SUCCESS",
                "SUCCESS:\nCheck peds.meta file for the custom ped!",
            )
            self.view.statusBar().showMessage(
                f"Success! Your custom ped has been written to {save_path}/peds.meta"
            )
        else:
            self.view.error_dialogs(
                err_message, "ERROR:\nCustom ped generation failed! Try again."
            )

    def close_tab(self, index):
        self.view.tab_area.removeTab(index)

    def tab_rename(self, index):
        tab_rename_dialog = QDialog(self.view)
        tab_rename_dialog.setWindowTitle("Rename Tab")
        dialog_layout = QVBoxLayout()

        rename_label = QLabel("Enter name for the tab:")
        rename_edit = QLineEdit(self.view.tab_area.tabText(index).split(":")[-1])
        rename_button_group = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        dialog_layout.addWidget(rename_label)
        dialog_layout.addWidget(rename_edit)
        dialog_layout.addWidget(rename_button_group)

        tab_rename_dialog.setLayout(dialog_layout)
        rename_button_group.accepted.connect(tab_rename_dialog.accept)
        rename_button_group.rejected.connect(tab_rename_dialog.reject)

        tab_rename_dialog.exec_()

        if QDialog.accepted:
            new_name = f"PEDS: {rename_edit.text()}"
            self.view.tab_area.setTabText(index, new_name)


class GTAVMainWindow(QMainWindow):
    """Main GUI"""

    def __init__(self, q_settings_file):
        super().__init__()

        # Main window settings
        self.setWindowTitle(f"GTA V Addon META Creator V{APP_VERSION}")
        # setGeometry(x-pos, y-pos, width, height)
        self.setGeometry(800, 200, 715, 500)

        # Status bar located at bottom of window
        self.statusBar()

        self.create_menu_bar()

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
        if q_settings_file:
            self.restore_dir_view()

        # App Layout
        self.app_layout = QVBoxLayout()

        # Create the rest of the gui and add to main layout
        # Keep for now
        self.create_title_labels()
        self.create_load_file()
        self.create_load_template()

        # Tab widget for form creation
        self.create_tab_area()
        self.create_generate_btn()

        self.app_widget.setLayout(self.app_layout)
        self.q_split.addWidget(self.app_widget)

        self.main_layout.addWidget(self.q_split)

    def save_dir_view(self):
        q_settings = QSettings("settings.ini", QSettings.IniFormat)
        q_settings.setValue(
            "expanded_item", self.model.filePath(self.tree.currentIndex())
        )

    def restore_dir_view(self):
        q_settings = QSettings("settings.ini", QSettings.IniFormat)
        expand_file = q_settings.value("expanded_item")
        model_index = self.model.index(expand_file)
        self.tree.setCurrentIndex(model_index)
        self.tree.setExpanded(model_index, True)

    def closeEvent(self, event):
        close = QMessageBox.question(
            self,
            "QUIT",
            "Do you really want to quit the application?",
            QMessageBox.Yes | QMessageBox.Cancel,
            defaultButton=QMessageBox.Cancel,
        )

        if event == False and close == QMessageBox.Yes:
            self.save_dir_view()
            qApp.quit()
        elif event == False and close == QMessageBox.Cancel:
            pass
        elif close == QMessageBox.Yes:
            self.save_dir_view()
            event.accept()
        elif close == QMessageBox.Cancel:
            event.ignore()

    def create_menu_bar(self):
        # Create a menubar
        self.menu_bar = self.menuBar()
        self.menu_file = self.menu_bar.addMenu("&File")
        self.menu_help = self.menu_bar.addMenu("&Help")

    def create_dir_view(self):
        # Set up the model/ widget
        self.model = QFileSystemModel()
        self.filter_list = []
        self.filter_list.append("*.meta")
        self.filter_list.append("*.xml")

        self.model.setNameFilters(self.filter_list)
        self.model.setNameFilterDisables(False)

        self.model.setRootPath("C:/")

        # Treeview object needs a model set to it
        self.tree = QTreeView()
        self.tree.setAnimated(True)

        self.tree.setModel(self.model)

        # Set up the tree view
        self.tree.setIndentation(15)
        self.tree.setSortingEnabled(False)
        self.tree.setColumnWidth(0, 150)  # Dir Name Column (Column, size)
        self.tree.setColumnWidth(1, 30)  # Size Column
        self.tree.setColumnWidth(2, 30)  # File type column

        self.q_split.addWidget(self.tree)

    def create_title_labels(self):
        # Layout
        self.title_layout = QVBoxLayout()

        # Labels
        self.title_label = QLabel(f"GTA V Addon META Creator V{APP_VERSION}")
        self.title_label.setFixedHeight(25)
        self.title_label.setAlignment(Qt.AlignCenter)
        try:
            self.title_label.setFont(QFont("pricedown", 20))
        except:
            self.title_label.setFont(QFont("Arial", 20))
        self.author_label = QLabel("By: Steeldrgn")
        self.author_label.setFixedHeight(30)
        self.author_label.setAlignment(Qt.AlignCenter)
        try:
            self.author_label.setFont(QFont("pricedown", 20))
        except:
            self.author_label.setFont(QFont("Arial", 20))

        # Add labels to layout
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.author_label)

        # Add to app layout
        self.app_layout.addLayout(self.title_layout)

    def create_load_file(self):
        # Layout
        self.load_xml_layout = QHBoxLayout()

        # Widgets
        self.path_line_edit = QLineEdit()
        self.path_line_edit.setPlaceholderText("PATH TO META or XML FILE")
        self.path_line_edit.setAlignment(Qt.AlignCenter)

        # TODO: Change to variable load
        self.path_btn = QPushButton("Load File")

        # Add to self layout
        self.load_xml_layout.addWidget(self.path_line_edit)
        self.load_xml_layout.addWidget(self.path_btn)

        # Add the main layout
        self.app_layout.addLayout(self.load_xml_layout)
        self.path_btn.setFocus()

    def create_load_template(self):
        # layout
        self.template_layout = QHBoxLayout()

        # Widgets
        self.template_label = QLabel("Choose A Template: ")
        self.template_label.setAlignment(Qt.AlignCenter)
        self.template_cbox = QComboBox()
        self.template_cbox.addItem("-----Choose A Template-----")
        self.template_cbox.setCurrentIndex(0)
        self.template_cbox.setEditable(True)
        self.template_cbox.setInsertPolicy(QComboBox.NoInsert)
        self.template_cbox.setDisabled(True)

        self.template_load_btn = QPushButton("Load Template")
        self.template_load_btn.setDisabled(True)

        # Add widgets to self layout
        self.template_layout.addWidget(self.template_label)
        self.template_layout.addWidget(self.template_cbox)
        self.template_layout.addWidget(self.template_load_btn)

        # Add to the main layout
        self.app_layout.addLayout(self.template_layout)

    def create_tab_area(self):
        self.tab_area = QTabWidget()
        self.tab_area.setTabsClosable(True)
        self.tab_area.setMovable(True)
        self.app_layout.addWidget(self.tab_area)

    def create_generate_btn(self):
        """
        Generate Meta button layout
        """
        self.generate_btn = QPushButton("Generate META File")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setDisabled(True)

        self.app_layout.addWidget(self.generate_btn)

    def populate_cbox(self, object_list):
        """
        Add all ped objects to the combo box
        Connects the load peds file button
        """
        for item in object_list:
            self.template_cbox.addItem(item.Name)

        if self.template_cbox.count() > 1:
            self.template_cbox.setDisabled(False)

    def generate_ped_param_form(self, attr_dict, cur_ped_template):
        """
        Populate the scroll bar area with ped params
        Connects the Load Template button
        """
        # ONE PAGE
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_form_layout = QFormLayout()
        scroll_widget.setLayout(scroll_form_layout)
        scroll_area.setWidget(scroll_widget)

        for k, v in cur_ped_template.return_att_dict().items():
            # Allow editing of name
            if k == "Name":
                scroll_form_layout.addRow(QLabel(k), QLineEdit(v))
            elif v == None:
                scroll_form_layout.addRow(QLabel(k), QLineEdit())
            elif isinstance(v, list):
                param_label = QLabel(f"{k} HasChildren")
                param_label2 = QLabel("See Items Below:")
                scroll_form_layout.addRow(param_label, param_label2)

                for item in v:
                    param_label = QLabel(f"{k} Item")
                    param_cbox = QComboBox()
                    param_cbox.addItem(item.text)
                    param_cbox.setEditable(True)
                    param_cbox.setInsertPolicy(QComboBox.InsertAtTop)
                    param_cbox.setCurrentText(item.text)
                    scroll_form_layout.addRow(param_label, param_cbox)

            elif isinstance(v, LET._Attrib):
                param_label = QLabel(k)
                param_edit_line = QLineEdit(v["value"])

                scroll_form_layout.addRow(param_label, param_edit_line)

            elif isinstance(v, str):
                param_label = QLabel(k)

                if k in attr_dict.keys():
                    param_cbox = QComboBox()
                    param_cbox.addItems(attr_dict[k])
                    param_cbox.setEditable(True)
                    param_cbox.setInsertPolicy(QComboBox.InsertAtTop)
                    param_cbox.setCurrentText(v)
                    scroll_form_layout.addRow(param_label, param_cbox)

                else:
                    param_edit_line = QLineEdit(v)
                    scroll_form_layout.addRow(param_label, param_edit_line)

        self.tab_area.addTab(scroll_area, f"PED: {cur_ped_template.Name}")
        self.generate_btn.setDisabled(False)

    def error_dialogs(self, error, other_message=None):
        """
        Error messages to be shown
        """
        if error == "PATH EMPTY":
            QMessageBox.warning(self, error, "ERROR: \nPath cannot be empty!")
        elif error == "FILE NOT FOUND":
            QMessageBox.warning(
                self,
                error,
                "ERROR: \nFile cannot be found. Are you pointing to the right place?",
            )
        elif error == "NOT VALID PEDS FILE":
            QMessageBox.warning(
                self,
                error,
                "ERROR: \nNot a valid peds.ymt.xml or peds.meta file! Choose a different file!",
            )
        elif error == "INVALID TEMPLATE":
            QMessageBox.warning(
                self, error, f"ERROR: \n{other_message} is not a valid ped template."
            )
        elif error == "NO PED INFO":
            QMessageBox.warning(self, error, other_message)
        elif error == "GENERATE FAILED":
            QMessageBox(self, error, other_message)

    def clear_combo_box(self):
        if self.template_cbox.count() > 1:
            self.template_cbox.clear()
            self.template_cbox.addItem("-----Choose A Template-----")
            self.template_cbox.setCurrentIndex(0)

    def get_ped_path_text(self):
        return self.path_line_edit.text()

    def set_ped_file_path(self, file_path):
        self.path_line_edit.setText(file_path)

    def get_ped_template_text(self):
        return self.template_cbox.currentText()


def main():
    app = QApplication(sys.argv)  # Can accept cmdline arguments
    app.setStyle("Fusion")

    # Set Fusion style to be dark  themed
    # Palette has 3 groups: Active, inactive, disabled
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.Disabled, QPalette.Base, QColor(40, 40, 40))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.Text, Qt.gray)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.gray)

    app.setPalette(palette)

    # Adding a custom font
    # Create new QFontdatabase class
    try:
        font_db = QFontDatabase()
        # Add custom font into the database
        font_id = font_db.addApplicationFont("fonts/pricedownbl.ttf")
        # Add font to a font family
        pd_font_fam = font_db.applicationFontFamilies(font_id)
        pricedown = QFont(pd_font_fam[0])

        app.setFont(QFont("Arial", 11))
    except:
        pass

    q_settings = False

    try:
        with open("settings.ini", "r") as file:
            q_settings = True
    except:
        pass

    # Main UI
    main_ui = GTAVMainWindow(q_settings)
    main_ui.show()

    # Controller
    controller = GTAVController(view=main_ui)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
