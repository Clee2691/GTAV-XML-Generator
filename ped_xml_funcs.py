import xml.etree.ElementTree as ET
import os, os.path
import copy
from pathlib import Path

import lxml.etree as LET


class Ped:

    """
    Ped class encompassing attributes based on original Peds YMT file
    Has 71 total attributes

    Generate ped object using a dictionary of attributes -> see ped_generator() function

    """

    def __init__(self, ped_dictionary):
        for k, v in ped_dictionary.items():
            setattr(self, k, v)
        # print('New ped created!')

    def return_att_dict(self):
        return self.__dict__

    def display_attributes(self):
        counter = 1
        for attr, val in self.__dict__.items():
            print(f"{counter}. Attribute: {attr} | Value: {val}")
            counter += 1
        return

    def update_attr(self, new_val_dict):
        for k, v in new_val_dict.items():
            if isinstance(getattr(self, k), dict):
                setattr(self, k, {'value': v})
            else:
                setattr(self, k, v)
        return print("Attributes updated!")

    def __repr__(self):
        return f"Name: {self.Name}"


def ped_generator(xml_file):
    """
    Take the ped.ymt.xml file and extract all the peds in it (Original ped file)
    Has 683 total peds

    Input -> ped.ymt.xml file
    returns -> List of ped objects

    """
    list_of_peds = []
    err_message = None

    try:
        ped_parsed = LET.parse(xml_file)
        ped_root = ped_parsed.getroot()

        if ped_root.tag == "CPedModelInfo__InitDataList":

            # I just wanted the items in InitDatas
            ped_data = ped_root.findall("./InitDatas/Item")

            for ped_element in ped_data:
                ped_dictionary = {}
                for param in ped_element:
                    # Parameter has child elements
                    if len(param) > 0:
                        ped_dictionary[param.tag] = []
                        for item in param:
                            ped_dictionary[param.tag].append(item)
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

            print(
                "Ped database populated! Choose a ped template to start the ped creation process!"
            )

            return list_of_peds, err_message
        else:
            err_message = "NOT VALID PEDS FILE"
            return None, err_message

    except FileNotFoundError:
        err_message = "FILE NOT FOUND"
        return None, err_message

def attr_db(peds_list):
    """
    Gather possible entries for each ped attribute through peds.meta file
    Only need to run it once.

    69/71 entries have options

    """
    ped_attrib_db = {}

    for ped in peds_list:
        for k, v in ped.return_att_dict().items():
            if v == None:
                continue
            elif isinstance(v, LET._Attrib):
                ped_attrib_db[k] = v
            elif (k not in ped_attrib_db) and isinstance(v, list):
                ped_attrib_db[k] = {child.text for child in v}
            elif k not in ped_attrib_db:
                ped_attrib_db[k] = {v}
            elif k in ped_attrib_db and isinstance(v, list):
                for child in v:
                    ped_attrib_db[k].add(child.text)
            else:
                ped_attrib_db[k].add(v)    

    return ped_attrib_db

def generate_new_ped(ped_template=None, new_val_dict=None):

    """
    Create a new custom ped with values specified by a dictionary

    Input -> Ped object (Template), dictionary of parameter changes

    output -> new ped object with custom values

    """
    error_mess = None

    if new_val_dict == None:
        error_mess = "GENERATE FAILED"
        return error_mess
    else:
        # Deepcopy so I don't override the template ped
        new_ped = copy.deepcopy(ped_template)
        new_ped.update_attr(new_val_dict)

        return new_ped, error_mess

def ped_xml_writer(new_ped, save_path):
    """
    Writes the custom ped to peds.meta file. If no file is present, will create one first.
    If no custom ped is passed, this function does nothing.

    Input -> Custom ped object

    Output -> Either new peds.meta file or append custom ped to peds.meta
    """

    ped_meta_path = Path(save_path + "/peds.meta")

    if ped_meta_path.exists():
        # Need parser to reset formating of existing file
        xml_parser = LET.XMLParser(remove_blank_text=True)
        ped_tree = LET.ElementTree(file=str(ped_meta_path), parser=xml_parser)

        # InitDatas is the root for all ped items
        ped_data_root = ped_tree.getroot().find("InitDatas")

    else:
        ped_xml_root = LET.Element("CPedModelInfo__InitDataList")
        ped_data_root = LET.SubElement(ped_xml_root, "InitDatas")
        ped_tree = LET.ElementTree(ped_xml_root)

    ped_item = LET.SubElement(ped_data_root, "Item")

    for attr, val in new_ped.return_att_dict().items():
        # List datatype specifies parameter has more child elements
        if val == '':
            LET.SubElement(ped_item, attr)

        elif isinstance(val, list):
            item1_subset = LET.SubElement(ped_item, attr)
            for subitem in val:
                LET.SubElement(item1_subset, "Item").text = subitem

        # Dictionary datatype specifies element only attributes
        elif isinstance(val, dict):
            LET.SubElement(ped_item, attr, val)

        # Everything else should have text only
        else:
            LET.SubElement(ped_item, attr).text = val

    ped_tree.write(
        str(ped_meta_path), encoding="utf-8", xml_declaration=True, pretty_print=True
    )


