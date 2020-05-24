import xml.etree.ElementTree as ET
import os.path
import copy

class Ped:
    def __init__(self, ped_dictionary):
        for k, v in ped_dictionary.items():
            setattr(self, k, v)
        print('New ped created!')

    def return_att_dict(self):
        return self.__dict__

    def display_attributes(self):
        attr_dict = self.return_att_dict()

        counter = 1
        for attr, val in attr_dict.items():
            print(f'{counter}. Attribute: {attr} | Value: {val}')
            counter += 1

    def update_attr(self, new_val_dict):
        for k, v in new_val_dict.items():
            setattr(self, k, v)
        print('Attributes updated!')

    def __repr__(self):
        return (f'Name: {self.Name}')


def ped_generator(xml_tree):
    """
    Take the ped.meta file and extract all the peds in it

    """
    list_of_peds = []

    ped_parsed = ET.parse(xml_tree)
    ped_root = ped_parsed.getroot()

    ped_data = ped_root.findall('./InitDatas/Item')

    for ped_element in ped_data:
        ped_dictionary = {}
        for param in ped_element:
            # Parameter has child elements
            if len(param) > 0:
                ped_dictionary[param.tag] = []
                for item in param:
                    ped_dictionary[param.tag].append(item.text)
            # Only has attribute with 'value' - usually true or false
            elif param.attrib:
                ped_dictionary[param.tag] = param.attrib
            # Not an empty tag
            elif param.text != None:
                ped_dictionary[param.tag] = param.text
            else:
                ped_dictionary[param.tag] = None

        ped = Ped(ped_dictionary)
        list_of_peds.append(ped)

    return list_of_peds


def generate_new_ped(ped_template, new_val_dict):
    """
    Create a new custom ped with values specified by user

    """
    new_ped = copy.deepcopy(ped_template)

    new_ped.update_attr(new_val_dict)

    return new_ped

def ped_xml_writer(new_ped = None):
    ped_meta_path = 'ped_xml_files/peds.meta'

    if os.path.exists(ped_meta_path) == False:
        print('Looks like no peds.meta file is present, hang on while it is created...')

        with open(ped_meta_path, 'x'):
            root = ET.Element('CPedModelInfo__InitDataList')
            init_data_node = ET.SubElement(root, 'InitDatas')
            
            ET.ElementTree(root).write(ped_meta_path)

    if new_ped != None:
        ped_tree = ET.ElementTree(file='ped_xml_files/peds.meta')
        ped_data_root = ped_tree.getroot().find('InitDatas')
        ped_item = ET.SubElement(ped_data_root, 'Item')

        for attr, val in new_ped.return_att_dict().items():
            if isinstance(val, list):
                item1_subset = ET.SubElement(ped_item, attr)
                for stuff in val:
                    ET.SubElement(item1_subset, 'Item').text = stuff
            elif isinstance(val, dict):
                ET.SubElement(ped_item, attr, val)
            else:
                ET.SubElement(ped_item, attr).text = val

        ped_tree.write('ped_xml_files/peds.meta')