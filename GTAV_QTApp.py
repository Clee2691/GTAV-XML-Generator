from functions import xml_parse
import sys
import logging

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import lxml.etree as LET

APP_VERSION = 2.0
AUTHOR = "Steeldrgn"

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
        self.view.path_btn.clicked.connect(self.load_db)
        self.view.template_load_btn.clicked.connect(self.pick_template)
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
        <dt>Step 1. Load META/XML File</dt>
        <dd>- Select a peds, weapon, etc. meta or XML file either through the file browser or file menu and press load.</dd><br>
        <dt>Step 2. Pick Object Template</dt>
        <dd>- Once the database is loaded, pick an object template to start editing the parameters.</dt><br>
        <dt>Step 3. Edit Object Parameters</dt>
        <dd>Edit the parameters you want and press generate meta file.</dd><br>
        <dt>Step 4. Locate File</dt>
        <dd>Check save location folder for the generated meta file.</dd><br>
        <dt>Step 5. Enjoy!</dt>
        <dd>Place file in desired location and enjoy your addon ped, weapon, etc!</dd><br>
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
        <h3 align="center"> Author: {AUTHOR} \u00A92020</h3>
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
            "Load META or XML File",
            "./database",
            "XML, META Files (*.meta *.xml)",
            "",
        )
        self.view.set_file_path(file_path)

    def dir_view_select(self, index):
        """ 
        Update path_line_edit field with valid peds, weapon, etc. meta or xml file 
        QTreeView.doubleclicked event passes QModelIndex object as a parameter
        """

        # Get the filepath - index = QModelIndex object -> model() return QFileSystemModel object
        file_path = index.model().filePath(index)

        # Returns a string displaying type of file
        file_type = index.model().type(index)

        # Determine if it is a file not directory
        # fileInfo returns a QFileInfo object
        file_isFile = index.model().fileInfo(index).isFile()

        self.view.set_file_path(file_path)

    def load_db(self):
        """ 
        Initial loading of the object database
        """
        self.view.clear_combo_box()

        xml_path = self.view.get_path_text()
        if xml_path == "":
            self.err_mess = "PATH EMPTY"
            self.view.error_dialogs(self.err_mess)
            return

        # Load the database and any error messages
        self.object_list, self.err_mess, temp_type = xml_parse.xml_meta_parser(xml_path)

        # Creates error dialog boxes if there are errors
        if self.err_mess:
            self.view.error_dialogs(self.err_mess)
        else:
            self.view.populate_cbox(self.object_list)
            self.view.template_load_btn.setDisabled(False)

            # Generate the attribute options with the object list
            self.attr_db = xml_parse.attr_db(self.object_list)
            self.view.statusBar().showMessage(
                f"Success! {temp_type} DB Loaded! Choose a {temp_type} template to get started!",
                0,
            )

    def pick_template(self):
        """
        Show params for the picked ped, weapon, etc.
        """
        current_text = self.view.get_template_text()

        self.cur_obj = None

        if current_text in self.attr_db["Name"]:

            for GTA_object in self.object_list:
                if GTA_object.Name.upper() == current_text.upper():
                    self.cur_obj = GTA_object

            temp_type = GTA_object.object_type.upper()

            self.view.generate_param_form(self.attr_db, self.cur_obj, temp_type)

        else:
            self.view.error_dialogs("INVALID TEMPLATE", current_text)

        return self.cur_obj

    def generate_xml(self):
        new_val_dict = {}
        slot_list = []
        for param in range(self.view.scroll_form_layout.rowCount()):
            # itemAt(row, column) - column index [0(Label), 1(Lineedit/combobox)]
            row_label = self.view.scroll_form_layout.itemAt(param, 0).widget().text()
            row_param_widget = self.view.scroll_form_layout.itemAt(param, 1).widget()

            if row_label == 'SlotNavigateOrder Number' or row_label == 'SlotBestOrder Number':
                slot_list.append((row_label.split(' ')[0], row_param_widget.text()))
                continue

            if isinstance(row_param_widget, QLineEdit):
                new_val_dict[row_label] = row_param_widget.text()

            elif isinstance(row_param_widget, QComboBox):
                new_val_dict[row_label] = row_param_widget.currentText()

        custom_obj, err_mess = xml_parse.generate_new_object(self.cur_obj, new_val_dict)

        if not err_mess:
            save_dialog = QFileDialog(self.view)
            save_path = save_dialog.getExistingDirectory(
                self.view, "Save Location", ".", QFileDialog.DontUseNativeDialog
            )
            if save_path == "":
                pass
            else:
                temp_type = custom_obj.object_type
                xml_parse.xml_writer(custom_obj, save_path, temp_type, slot_list)
                QMessageBox.information(
                    QWidget(),
                    "SUCCESS",
                    f"SUCCESS:\nCheck {save_path} file for the custom {temp_type}!",
                )
                self.view.statusBar().showMessage(
                    f"Success! Your custom {temp_type} has been written to {save_path}"
                )
        else:
            self.view.error_dialogs(
                err_message, f"ERROR:\nCustom {temp_type} generation failed! Try again."
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

        result = tab_rename_dialog.exec_()

        if result == QDialog.Accepted:
            # [PED, PEDPERS, WEAP, WEAPARCH, WEAPANIM, WEAPCOMP, LOAD, PICKUP]
            tab_type = self.view.tab_area.tabText(index).split(":")[0]
            new_name = f"{tab_type}:{rename_edit.text()}"
            self.view.tab_area.setTabText(index, new_name)


class GTAVMainWindow(QMainWindow):
    """Main GUI"""

    def __init__(self, q_settings_file):
        super().__init__()

        # Main window settings
        self.setWindowTitle(f"GTA V Addon META Creator V{APP_VERSION}")
        # setGeometry(x-pos, y-pos, width, height)
        self.setGeometry(200, 100, 1300, 800)

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
        self.author_label = QLabel(f"By: {AUTHOR}")
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
        Add all objects to the combo box
        Connects the load file button
        """
        for item in object_list:
            self.template_cbox.addItem(item.Name)

        if self.template_cbox.count() > 1:
            self.template_cbox.setDisabled(False)

    def generate_param_form(self, attr_dict, cur_template, temp_type):
        """
        Populate the scroll bar area with object params
        Connects the "Load Template" button
        """
        # ONE PAGE
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.scroll_form_layout = QFormLayout()
        scroll_widget.setLayout(self.scroll_form_layout)
        scroll_area.setWidget(scroll_widget)

        if temp_type == 'WEAP':
            # Slot Navigate order number
            self.slotnav_name_label = QLabel('SlotNavigateOrder Number')
            self.slotnav_line_edit = QLineEdit('0')
            self.slotnav_line_edit.setAlignment(Qt.AlignHCenter)
            self.scroll_form_layout.addRow(self.slotnav_name_label, self.slotnav_line_edit)

            # Slot best order number
            self.slotbest_label = QLabel('SlotBestOrder Number')
            self.slotbest_line_edit = QLineEdit('0')
            self.slotbest_line_edit.setAlignment(Qt.AlignHCenter)
            self.scroll_form_layout.addRow(self.slotbest_label, self.slotbest_line_edit)

        for k, v in cur_template.return_att_dict().items():
            # Only internal use
            if k == "object_type":
                pass
            # Allow editing of name
            elif k == "Name":
                self.name_label = QLabel(k)
                self.name_label.setAlignment(Qt.AlignHCenter)
                self.name_line_edit = QLineEdit(v)
                self.name_line_edit.setAlignment(Qt.AlignHCenter)
                self.scroll_form_layout.addRow(self.name_label, self.name_line_edit)
            elif v == None:
                param_label = QLabel(k)
                param_label.setAlignment(Qt.AlignHCenter)
                self.scroll_form_layout.addRow(param_label, QLineEdit())
            # Some lists have items with different tags -> Weapons.meta file
            # <Fx>, <Explosion>, <WeaponFlags>
            elif k == "WeaponFlags":
                # Will have a dialog with checkboxes
                param_label = QLabel(f"{k} Params")
                param_label.setAlignment(Qt.AlignHCenter)
                self.param_btn = QPushButton(f"Edit {k}")
                # Connecting edit param button with extra parameters
                # Need a lambda function, x is the first argument which is a boolean
                self.param_btn.clicked.connect(
                    lambda x, cur_temp=cur_template, attr_dict=attr_dict: self.edit_weapon_flags(
                        cur_temp, attr_dict
                    )
                )
                self.scroll_form_layout.addRow(param_label, self.param_btn)

            elif isinstance(v, list):
                param_label = QLabel(k)
                param_label.setAlignment(Qt.AlignHCenter)

                # Separate dialog for parameters that have children elements
                self.param_btn = QPushButton(f"Edit {k}")

                # Clicked returns boolean, so need x as first parameter
                self.param_btn.clicked.connect(
                    lambda x, cur_temp=cur_template, btn_text=self.param_btn.text(): self.edit_param_clicked(
                        cur_temp, btn_text
                    )
                )

                self.scroll_form_layout.addRow(param_label, self.param_btn)

            elif isinstance(v, LET._Attrib):
                param_label = QLabel(k)
                param_label.setAlignment(Qt.AlignHCenter)
                # For peds [value]
                # For weapons: [value, ref, (x,y,z), ]
                xyz_layout = QHBoxLayout()
                attrib_keys = v.keys()

                if "value" in attrib_keys:
                    param_edit_line = QLineEdit(v["value"])
                elif "ref" in attrib_keys:
                    param_edit_line = QLineEdit(v["ref"])

                # Some params have x,y or x,y,z
                elif len(v) >= 2:
                    for xyz, val in v.items():
                        xyz_label = QLabel(xyz)
                        xyz_line_edit = QLineEdit(val)
                        xyz_line_edit.setAlignment(Qt.AlignHCenter)
                        xyz_layout.addWidget(xyz_label)
                        xyz_layout.addWidget(xyz_line_edit)

                # Set alignment for Qlineedit to center
                param_edit_line.setAlignment(Qt.AlignHCenter)

                if xyz_layout.count() > 0:
                    self.scroll_form_layout.addRow(param_label, xyz_layout)
                else:
                    self.scroll_form_layout.addRow(param_label, param_edit_line)

            elif isinstance(v, str):
                param_label = QLabel(k)
                param_label.setAlignment(Qt.AlignHCenter)

                if k in attr_dict.keys():
                    param_cbox = QComboBox()
                    param_cbox.setSizeAdjustPolicy(
                        QComboBox.AdjustToMinimumContentsLength
                    )
                    param_cbox.addItems(attr_dict[k])
                    param_cbox.setEditable(True)
                    param_cbox.setInsertPolicy(QComboBox.InsertAtTop)
                    param_cbox.setCurrentText(v)
                    self.scroll_form_layout.addRow(param_label, param_cbox)

                else:
                    param_edit_line = QLineEdit(v)
                    param_edit_line.setAlignment(Qt.AlignHCenter)
                    self.scroll_form_layout.addRow(param_label, param_edit_line)

        self.tab_area.addTab(scroll_area, f"{temp_type}: {cur_template.Name}")
        self.generate_btn.setDisabled(False)

    def edit_param_clicked(self, cur_temp, btn_text):
        param = btn_text.split(" ")[-1]
        param_dialog = QDialog()
        # (Width, Height)
        param_dialog.setMaximumSize(1200, 1000)
        param_dialog.setMinimumSize(350, 250)
        param_layout = QVBoxLayout()

        param_dialog.setWindowTitle(f"Edit {param}")

        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        dialog_scroll = QScrollArea()
        dialog_scroll.setWidgetResizable(True)
        dialog_scroll_widget = QWidget()
        dialog_form_layout = QFormLayout()
        dialog_scroll_widget.setLayout(dialog_form_layout)
        dialog_scroll.setWidget(dialog_scroll_widget)

        # getattr() for accessing attribute of class with variable
        children_list = getattr(cur_temp, param)
        # Empty parameter set - e.g. AttachPoints for melee weapons
        if len(children_list) < 1:
            QMessageBox.information(
                self, "No Extra Params", f"There is nothing to edit for {param}."
            )
            cur_temp.param = None
            return

        # TODO: Recursion?
        elif param == "OverrideForces":
            for force_item in children_list:
                for k, v in force_item.items():
                    self.item_label = QLabel(k)
                    self.item_label.setAlignment(Qt.AlignHCenter)
                    dialog_form_layout.addWidget(self.item_label)
                    for force_param in v:
                        for k, v in force_param.items():
                            if k == "BoneTag":
                                self.force_name = QLabel(k)
                                self.force_value = QLineEdit(v)

                            else:
                                self.force_name = QLabel(k)
                                self.force_value = QLineEdit(v["value"])

                            self.force_name.setAlignment(Qt.AlignHCenter)
                            self.force_value.setAlignment(Qt.AlignHCenter)

                            dialog_form_layout.addRow(self.force_name, self.force_value)

        elif param == "AttachPoints":
            for attach_point_elements in children_list:
                for k, v in attach_point_elements.items():
                    self.attach_label = QLabel(f"AttachPoint {k}")
                    self.attach_label.setAlignment(Qt.AlignHCenter)
                    dialog_form_layout.addWidget(self.attach_label)
                    # Bone
                    self.bone_label = QLabel("AttachBone")
                    self.bone_label.setAlignment(Qt.AlignHCenter)
                    self.bone_edit = QLineEdit(v[0]["AttachBone"])
                    self.bone_edit.setAlignment(Qt.AlignHCenter)
                    dialog_form_layout.addRow(self.bone_label, self.bone_edit)

                    # Components
                    # TODO: Recursion?
                    # Component Dictionary
                    for k1, v1 in v[1].items():
                        # List of comp item param dictionaries
                        for comp_items in v1:
                            # Item dictionaries
                            for k2, v2 in comp_items.items():
                                self.comp_item_label = QLabel("Component Item")
                                self.comp_item_label.setAlignment(Qt.AlignHCenter)
                                dialog_form_layout.addWidget(self.comp_item_label)
                                for comp_param in v2:
                                    for k3, v3 in comp_param.items():
                                        if k3 == "Name":
                                            self.comp_param_label = QLabel(k3)
                                            self.comp_param_edit = QLineEdit(v3)
                                        elif k3 == "Default":
                                            self.comp_param_label = QLabel(k3)
                                            self.comp_param_edit = QLineEdit(
                                                v3["value"]
                                            )

                                        self.comp_param_label.setAlignment(
                                            Qt.AlignHCenter
                                        )
                                        self.comp_param_edit.setAlignment(
                                            Qt.AlignHCenter
                                        )
                                        dialog_form_layout.addRow(
                                            self.comp_param_label, self.comp_param_edit
                                        )

        else:
            for item in children_list:
                param_label = QLabel(f"{item.tag}")
                param_label.setAlignment(Qt.AlignHCenter)
                param_line_edit = QLineEdit()
                param_line_edit.setAlignment(Qt.AlignHCenter)
                # For attributes with XYZ elements
                xyz_layout = QHBoxLayout()

                if item.text:
                    param_line_edit.setText(item.text)
                    dialog_form_layout.addRow(param_label, param_line_edit)

                elif item.attrib:
                    attrib_keys = item.attrib.keys()
                    if "value" in attrib_keys:
                        param_line_edit.setText(item.attrib["value"])
                        # param_edit_line = QLineEdit(item.attrib['value'])
                    elif "ref" in attrib_keys:
                        param_line_edit.setText(item.attrib["ref"])
                    # Some params only have and x,y and x,y,z
                    # Create a layout that holds all coordinates for the second part of form
                    elif len(item.attrib) >= 2:
                        for k, v in item.attrib.items():
                            k_label = QLabel(k)
                            v_edit = QLineEdit(v)
                            v_edit.setAlignment(Qt.AlignHCenter)
                            xyz_layout.addWidget(k_label)
                            xyz_layout.addWidget(v_edit)

                if xyz_layout.count() > 0:
                    dialog_form_layout.addRow(param_label, xyz_layout)
                else:
                    dialog_form_layout.addRow(param_label, param_line_edit)

        param_layout.addWidget(dialog_scroll)
        param_layout.addWidget(dialog_buttons)
        param_dialog.setLayout(param_layout)

        dialog_buttons.accepted.connect(param_dialog.accept)
        dialog_buttons.rejected.connect(param_dialog.reject)

        result = param_dialog.exec_()

        if result == QDialog.Accepted:
            self.save_params(cur_temp, param, dialog_form_layout)

    def save_params(self, cur_temp, param, layout_items):
        row_pair_list = []
        new_pair = []
        count = 0

        if param == "OverrideForces":
            for item in range(layout_items.count()):
                item_text = layout_items.itemAt(item).widget().text()
                if item_text == "Item":
                    continue
                if count == 6:
                    row_pair_list.append(tuple(new_pair))
                    count = 1
                    new_pair = [item_text]
                else:
                    new_pair.append(item_text)
                    count += 1

            row_pair_list.append(tuple(new_pair))

        elif param == "AttachPoints":
            attach_points = {}
            attach_items = []
            for item in range(layout_items.count()):
                item_text = layout_items.itemAt(item).widget().text()
                # Each label with attachpoint item creates a new item dictionary containing components
                # Does not add attachpoint item label to dictionary
                if item_text == "AttachPoint Item":
                    if len(attach_points) == 0:
                        pass
                    # Ensures adding label: value pairs to the item dictionary
                    # Adds the Default:true/false to end of first attachpoint
                    elif len(attach_items) == 2:
                        attach_points["Item"].append(tuple(attach_items))
                        attach_items = []
                        row_pair_list.append(attach_points.copy())

                    # Creates new empty list for next item
                    attach_points["Item"] = []
                    continue

                # Does not add component item to list/dictionary
                if item_text == "Component Item":
                    attach_points["Item"].append(tuple(attach_items))
                    attach_items = []
                    continue
                if len(attach_items) != 2:
                    attach_items.append(item_text)
                else:
                    attach_points["Item"].append(tuple(attach_items))
                    attach_items = [item_text]
            # Add last pair to list
            attach_points["Item"].append(tuple(attach_items))
            row_pair_list.append(attach_points)

        else:

            for item in range(layout_items.count()):
                form_widget = layout_items.itemAt(item)

                # If item is a widget - Text associated with it
                if isinstance(form_widget, QWidgetItem):
                    item_text = form_widget.widget().text()

                # For items with XYZ attrib values
                elif isinstance(form_widget, QHBoxLayout):
                    item_text = []
                    item_pair = []
                    hbox_param_layout = form_widget.layout()
                    for index in range(hbox_param_layout.count()):
                        xyz_text = hbox_param_layout.itemAt(index).widget().text()
                        # First index is label (x ,y ,z)
                        if index % 2 == 0:
                            item_pair.append(xyz_text)

                        # Second index is the value
                        else:
                            item_pair.append(xyz_text)
                            item_text.append(tuple(item_pair))
                            item_pair = []

                # Loop through all other parameters
                if item % 2 == 0:
                    new_pair.append(item_text)
                else:
                    new_pair.append(item_text)
                    row_pair_list.append(tuple(new_pair))
                    new_pair = []

        print(getattr(cur_temp, param))
        # print(row_pair_list)
        new_params = xml_parse.element_maker(param, row_pair_list)

        cur_temp.update_attr(new_params)
        print(getattr(cur_temp, param))

    def edit_weapon_flags(self, cur_temp, attr_dict):
        flag_dialog = QDialog()
        flag_dialog.setWindowTitle("Edit WeaponFlags")
        flag_dialog_btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        # Width, Height
        flag_dialog.setMinimumSize(350, 250)
        flag_dialog_vlayout = QVBoxLayout()
        flag_checkbox_layout = QGridLayout()
        weap_flag_label = QLabel("WeaponFlags")

        flag_dialog_vlayout.addWidget(weap_flag_label)
        flag_dialog_vlayout.addLayout(flag_checkbox_layout)
        flag_dialog_vlayout.addWidget(flag_dialog_btns)

        weapon_flags = cur_temp.WeaponFlags
        weapflag_list = weapon_flags.split(" ")

        flag_qobjects = []
        for weap_flag in sorted(attr_dict["WeaponFlags"]):
            if weap_flag in weapflag_list:
                flag_check = QCheckBox(weap_flag)
                flag_check.setChecked(True)
                flag_qobjects.append(flag_check)
            else:
                flag_check = QCheckBox(weap_flag)
                flag_check.setChecked(False)
                flag_qobjects.append(flag_check)

        # Making grid labels for gridlayout - 96 different flags
        grid_list = []
        # Rows -> Columns
        for i in range(20):
            for j in range(5):
                grid_list.append((i, j))

        num = 0
        try:
            for flag_obj in flag_qobjects:
                flag_checkbox_layout.addWidget(
                    flag_obj, grid_list[num][0], grid_list[num][1]
                )
                num += 1
        except IndexError:
            pass

        flag_dialog.setLayout(flag_dialog_vlayout)

        flag_dialog_btns.accepted.connect(flag_dialog.accept)
        flag_dialog_btns.rejected.connect(flag_dialog.reject)

        result = flag_dialog.exec_()

        if result == QDialog.Accepted:
            checked_flags = []
            for item_num in range(flag_checkbox_layout.count()):
                item = flag_checkbox_layout.itemAt(item_num)
                if item.widget().isChecked():
                    checked_flags.append(item.widget().text())

            cur_temp.WeaponFlags = " ".join(checked_flags)

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
        elif error == "XML PARSE ERROR":
            QMessageBox.warning(
                self, error, "Error: \n Could not parse file. Possible Corruption?"
            )
        elif error == "INVALID TEMPLATE":
            QMessageBox.warning(
                self, error, f"ERROR: \n{other_message} is not a valid template."
            )
        elif error == "GENERATE FAILED":
            QMessageBox(self, error, other_message)

    def clear_combo_box(self):
        if self.template_cbox.count() > 1:
            self.template_cbox.clear()
            self.template_cbox.addItem("-----Choose A Template-----")
            self.template_cbox.setCurrentIndex(0)

    def get_path_text(self):
        return self.path_line_edit.text()

    def set_file_path(self, file_path):
        self.path_line_edit.setText(file_path)

    def get_template_text(self):
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
    except:
        print("Pricedown font not found, falling back to Arial")

    # Set all other text to Arial size 11
    app.setFont(QFont("Arial", 11))
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

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('program_log.log')
    file_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    logger.addHandler(file_handler)
    
    main()
