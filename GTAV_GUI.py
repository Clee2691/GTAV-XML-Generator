import ped_xml_funcs

import PyQt5.QtWidgets as pqt5

gtav_gui = pqt5.QApplication([]) # Brackets are for cmdline arugments
gtav_gui.setStyle('Fusion')

main_window = pqt5.QWidget()

layout = pqt5.QVBoxLayout()
peds = ped_xml_funcs.ped_generator('database/peds.ymt.xml')

for k, v in peds[0].return_att_dict().items():
    if v != None:
        layout.addWidget(pqt5.QLabel(k))

main_window.setLayout(layout)
main_window.show()
gtav_gui.exec_()

