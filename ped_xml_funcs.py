import xml.etree.ElementTree as ET
import os.path
import copy


class Ped:

    """
    Ped class encompassing attributes based on original Peds YMT file
    Has 71 total attributes

    Generate ped object using a dictionary of attributes -> see ped_generator() function

    """

    def __init__(self, ped_dictionary):
        for k, v in ped_dictionary.items():
            setattr(self, k, v)
        print('New ped created!')

    def return_att_dict(self):
        return self.__dict__

    def display_attributes(self):
        counter = 1
        for attr, val in self.__dict__.items():
            print(f'{counter}. Attribute: {attr} | Value: {val}')
            counter += 1
        return

    def update_attr(self, new_val_dict):
        for k, v in new_val_dict.items():
            setattr(self, k, v)
        return print('Attributes updated!')

    def __repr__(self):
        return f'Name: {self.Name}'


def ped_generator(xml_file):
    """
    Take the ped.ymt.xml file and extract all the peds in it (Original ped file)
    Has 683 total peds

    Input -> ped.ymt.xml file
    returns -> List of ped objects

    """
    list_of_peds = []

    ped_parsed = ET.parse(xml_file)
    ped_root = ped_parsed.getroot()

    # I just wanted the items in InitDatas
    ped_data = ped_root.findall('./InitDatas/Item')

    for ped_element in ped_data:
        ped_dictionary = {}
        for param in ped_element:
            # Parameter has child elements
            if len(param) > 0:
                ped_dictionary[param.tag] = []
                for item in param:
                    ped_dictionary[param.tag].append(item.text)
            # Only has attribute with 'value'; Usually does not contain text as well
            elif param.attrib:
                ped_dictionary[param.tag] = param.attrib
            # Not an empty tag - Only has text
            elif param.text != None:
                ped_dictionary[param.tag] = param.text
            else:
                # No attribute or text - Empty tag
                ped_dictionary[param.tag] = None

        list_of_peds.append(Ped(ped_dictionary))

    print('Ped database populated! Create a new ped!')
    return list_of_peds


def generate_new_ped(ped_template, new_val_dict = None):

    """
    Create a new custom ped with values specified by a dictionary

    Input -> Ped object (Template), dictionary of parameter changes

    output -> new ped object with custom values

    """

    if new_val_dict == None:
        return print('No point generating a new ped if you do not have values to change...')
    else:
        # Use copy ped_template to be used as the new ped
        new_ped = copy.deepcopy(ped_template)
        new_ped.update_attr(new_val_dict)
        print('Custom ped created!')
        return new_ped


def ped_xml_writer(new_ped = None):
    """
    Writes the custom ped to peds.meta file. If no file is present, will create one first.
    If no custom ped is passed, this function does nothing.

    Input -> Custom ped object

    Output -> Either new peds.meta file or append custom ped to peds.meta
    """

    ped_meta_path = 'ped_xml_files/peds.meta'

    if os.path.exists(ped_meta_path) == False:
        print('Looks like no peds.meta file is present, hang on while it is created...')

        with open(ped_meta_path, 'x'):
            root = ET.Element('CPedModelInfo__InitDataList')
            init_data_node = ET.SubElement(root, 'InitDatas')
            
            ET.ElementTree(root).write(ped_meta_path)
        
        print('peds.meta file created! Located: {ped_meta_path}')

    if new_ped != None:
        ped_tree = ET.ElementTree(file='ped_xml_files/peds.meta')
        # InitDatas is the root for all ped items
        ped_data_root = ped_tree.getroot().find('InitDatas')
        ped_item = ET.SubElement(ped_data_root, 'Item')

        for attr, val in new_ped.return_att_dict().items():
            # List datatype specifies parameter has more child elements
            if isinstance(val, list):
                item1_subset = ET.SubElement(ped_item, attr)
                for subitem in val:
                    ET.SubElement(item1_subset, 'Item').text = subitem
            # Dictionary datatype specifies element only attributes
            elif isinstance(val, dict):
                ET.SubElement(ped_item, attr, val)
            # Everything else should have text only
            else:
                ET.SubElement(ped_item, attr).text = val

        ped_tree.write('ped_xml_files/peds.meta')

        return print('Custom ped successfully written to peds.meta!')
    else:
        return print('You did not enter a new ped to add! No changes made.')