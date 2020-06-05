import lxml.etree as LET
from pathlib import Path
import copy
import logging

class GTAObjects:

    """
    Objects created from parsing META/XML files.
    1. Peds
    2. Ped Personalities
    3. Weapons
    4. Weapon Archetypes
    5. Weapon Components
    6. Weapon Animations
    7. Loadouts
    """

    def __init__(self, param_dict):
        for k, v in param_dict.items():
            setattr(self, k, v)
        
    def return_att_dict(self):
        return self.__dict__

    def display_attributes(self):
        counter = 1
        for attr, val in self.__dict__.items():
            print(f'{counter}. Attribute: {attr} | Value: {val}')
            counter += 1

    def update_attr(self, new_val_dict):
        for k, v in new_val_dict.items():
            if isinstance(getattr(self, k), dict):
                setattr(self, k, {'value': v})
            else:
                setattr(self, k, v)
        return print("Attributes updated!")

    def __repr__(self):
        return f'Name: {self.Name}'

def xml_meta_parser(xml_file):
    """
    Parses xml file to create a list of gta objects
    """

    err_message = None

    try:
        file_parsed = LET.parse(xml_file)
    except FileNotFoundError:
        err_message = "FILE NOT FOUND"
        return None, err_message
    
    xml_root = file_parsed.getroot()
    
    # Parse ped file
    if xml_root.tag == 'CPedModelInfo__InitDataList':
        # I just wanted the items in InitDatas
        xml_ped_elements = xml_root.findall("./InitDatas/Item")
        ped_objects = create_parsed_objects(xml_ped_elements)

        return ped_objects, err_message

    elif xml_root.tag == 'CWeaponInfoBlob':
        # SlotNavigateOrder needs 2 identical entries - Same ordernumber/entry
        slot_nav_order = xml_root.find('SlotNavigateOrder')
        slot_best_order = xml_root.find('SlotBestOrder')
        wep_infos = xml_root.find('Infos')

        # Get weapon slots - Will need 3 total entries
        # Duplicate the SlotNavigateOrder
        nav_order_elements = weapon_slots(slot_nav_order[0])
        best_order_elements = weapon_slots(slot_best_order)

        # Gather all weapon elements before parsing into GTAObjects
        weapon_element_list = []
        for item in wep_infos.iter('Item'):
            if item.get('type') == 'CWeaponInfo':
                weapon_element_list.append(item)
        
        parsed_weapon_objects = create_parsed_objects(weapon_element_list)
        slot_nav_objects = weapon_slots(nav_order_elements)
        slot_best_objects = weapon_slots(best_order_elements)

    else:
        err_message = "NOT A VALID META/XML FILE"
        return None, err_message

def create_parsed_objects(xml_elements):
    """
    Parse elements of interest to create objects with their respective params
    """
    
    parsed_object_list = []
    for element_object in xml_elements:
            param_dictionary = {}
            for param in element_object:
                # Parameter has child elements
                # Weapons.meta specific parse
                # Weapon OverrideForces
                if param.tag == 'OverrideForces':
                    override_forces_parsed = []
                    # OverrideForaces Item
                    for sub in param.findall('*'):
                        force_item = {}
                        force_item[sub.tag] = []

                        # BoneTag, Forcefront, forceback
                        for sub2 in sub.findall('*'):
                            if sub2.text:
                                force_item[sub.tag].append({sub2.tag:sub2.text})
                            elif sub2.attrib:
                                force_item[sub.tag].append({sub2.tag:sub2.attrib})
                                
                        override_forces_parsed.append(force_item)
                    param_dictionary['OverrideForces'] = override_forces_parsed

                # Weapon AttachPoints - Has multiple children elements
                if param.tag == 'AttachPoints':
                    attach_items = []
                    # Attachment elements
                    for sub1 in param.findall('*'):
                        attach_params = {}
                        attach_params[sub1.tag] = []
                        # AttachBone & Component elements
                        for sub2 in sub1.findall('*'):
                            # AttachBone Element - No Children
                            if len(sub2.findall('*')) < 1:
                                if sub2.text:
                                    attach_params[sub1.tag].append({sub2.tag: sub2.text})
                            # Component Element - Has children
                            else:
                                comp_elements = {}
                                # sub2.tag == Components
                                comp_elements[sub2.tag] = []
                                for sub3 in sub2.findall('*'):
                                    name_default = {}
                                    # sub3.tag == Item
                                    name_default[sub3.tag] = []
                                    for sub4 in sub3.findall('*'):
                                        # sub4.tag == Name or Default
                                        if sub4.text:
                                            name_default[sub3.tag].append({sub4.tag:sub4.text})
                                        elif sub4.attrib:
                                            name_default[sub3.tag].append({sub4.tag:sub4.attrib})

                                    comp_elements[sub2.tag].append(name_default)

                                attach_params[sub1.tag].append(comp_elements)

                    param_dictionary[param.tag] = attach_items

                if len(param) > 0:
                    param_dictionary[param.tag] = []
                    for item in param:
                        param_dictionary[param.tag].append(item)
                # Only has attribute with 'value'; Usually does not contain text as well
                elif param.attrib:
                    param_dictionary[param.tag] = param.attrib
                # Not an empty tag - Only has text
                elif param.text:
                    param_dictionary[param.tag] = param.text
                else:
                    # No attribute or text - Empty tag
                    param_dictionary[param.tag] = None

            parsed_object_list.append(GTAObjects(param_dictionary))

    return parsed_object_list

def attr_db(parsed_object_list):
    """
    Return a dictionary of available values for each parameter
    Fills combo boxes for each parameter
    """
    parameter_database = {}

    for gta_object in parsed_object_list:
        for k, v in gta_object.return_att_dict().items():
            if v == None:
                continue
            elif isinstance(v, LET._Attrib):
                parameter_database[k] = v
            elif (k not in parameter_database) and isinstance(v, list):
                parameter_database[k] = {child.text for child in v}
            elif k not in parameter_database:
                parameter_database[k] = {v}
            elif k in parameter_database and isinstance(v, list):
                for child in v:
                    parameter_database[k].add(child.text)
            else:
                parameter_database[k].add(v)

    return parameter_database

def generate_new_object(object_template=None, new_val_dict=None):

    """
    Create the new object (Ped, weapon, etc.) with a template

    """
    error_mess = None

    if new_val_dict == None:
        error_mess = "GENERATE FAILED"
        return error_mess
    else:
        # Deepcopy so I don't override the template ped
        new_object = copy.deepcopy(object_template)
        new_object.update_attr(new_val_dict)

        return new_object, error_mess

def xml_writer(new_object, save_path, object_type='ped'):
    """
    Appends the custom object to the respective META file. If no file is present, will create one first.

    """
    object_type_dict = {'ped': 'peds', 'pedpersona':'pedpersonalities', 'weap': 'weapons', 
                        'weaparch':'weaponarchetypes', 'weapcomp': 'weaponcomponents',
                        'weapanim': 'weaponanimations', 'load': 'loadouts', 'pickup':'pickups'}

    meta_file_path = Path(f'{save_path}/{object_type_dict[object_type]}.meta')

    if meta_file_path.exists():
        # Need parser to reset formating of existing file
        xml_parser = LET.XMLParser(remove_blank_text=True)
        object_tree = LET.ElementTree(file=str(meta_file_path), parser=xml_parser)

        if object_type == 'ped':
            # InitDatas is the root for all ped items
            tree_root = object_tree.getroot().find('InitDatas')
            object_item = LET.SubElement(tree_root, 'Item')
        elif object_type == 'weap':
            tree_root = object_tree.getroot().find('Infos')
            sub1 = LET.SubElement(tree_root, 'Item')
            sub2 = LET.SubElement(sub1, 'Infos')
            object_item = LET.SubElement(sub2, 'Item', {'type':'CWeaponInfo'})
    # Reconstruct the tree from scratch if no existing file
    else:
        if object_type == 'ped':
            ped_xml_root = LET.Element('CPedModelInfo__InitDataList')
            ped_data_root = LET.SubElement(ped_xml_root, 'InitDatas')
            object_item = LET.SubElement(ped_data_root, "Item")
            object_tree = LET.ElementTree(ped_xml_root)
        elif object_type == 'weap':
            # CWeaponInfoBlob/Infos/Item/Infos/<Weapon items>
            main_weap_tags = ['TintSpecValues', 'FiringPatternAliases', 'UpperBodyFixupExpressionData', 'AimingInfos']
            weap_xml_root = LET.Element('CWeaponInfoBlob')
            # TODO - Slot tags
            for tag in main_weap_tags:
                LET.SubElement(weap_xml_root, tag)
            
            weap_info_root = LET.SubElement(weap_xml_root, 'Infos')
            weap_item_root = LET.SubElement(weap_info_root, 'Item')
            weap_sub_info = LET.SubElement(weapon_item_root, 'Infos')
            object_item = LET.SubElement(weap_sub_info, 'Item', {'type':'CWeaponInfo'})

            LET.SubElement(weap_xml_root, 'VehicleWeaponInfos')
            LET.SubElement(weap_xml_root, 'Name').text = 'Custom Weapon Addons'

            object_tree = LET.ElementTree(weap_xml_root)

    for attr, val in new_object.return_att_dict().items():
        # List datatype specifies parameter has more child elements
        if val == "":
            LET.SubElement(object_item, attr)

        # TODO: Need a specific way to parse weapon children
        # many children of children
        elif isinstance(val, list):
            item1_subset = LET.SubElement(object_item, attr)
            for subitem in val:
                LET.SubElement(item1_subset, "Item").text = subitem

        # Dictionary datatype specifies element only attributes
        elif isinstance(val, dict):
            LET.SubElement(object_item, attr, val)

        # Everything else should have text only
        else:
            LET.SubElement(object_item, attr).text = val

    object_tree.write(
        str(meta_file_path), encoding="utf-8", xml_declaration=True, pretty_print=True
    )

# Weapon specific functions
def weapon_slots(slot_groups):
    """
    Return parsed weapon slot entries
    """
    weap_slot = {}
    weap_slot_list = []
    for item in slot_groups.iter('OrderNumber', 'Entry'):
        if item.tag == 'OrderNumber':
            # OrderNumber is attribute {value: <int>}
            weap_slot[item.tag] = item.attrib
        if item.tag == 'Entry':
            weap_slot[item.tag] = item.text
        if len(weap_slot) == 2:
            weap_slot_list.append(weap_slot)
            weap_slot = {}

    return weap_slot_list

