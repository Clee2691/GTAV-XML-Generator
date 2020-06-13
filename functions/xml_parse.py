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
        return None, err_message, None
    except LET.XMLSyntaxError:
        err_message = "XML PARSE ERROR"
        return None, err_message, None
    
    xml_root = file_parsed.getroot()
    
    # Parse ped file
    if xml_root.tag == 'CPedModelInfo__InitDataList':
        # I just wanted the items in InitDatas
        xml_ped_elements = xml_root.findall("./InitDatas/Item")
        ped_objects = create_parsed_objects(xml_ped_elements, 'ped')

        return ped_objects, err_message, 'ped'

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
        
        parsed_weapon_objects = create_parsed_objects(weapon_element_list, 'weap')
        
        return parsed_weapon_objects, err_message, 'weap'

    else:
        err_message = "NOT A VALID META/XML FILE"
        return None, err_message, None

def create_parsed_objects(xml_elements, obj_type=None):
    """
    Parse elements of interest to create objects with their respective params
    """
    
    parsed_object_list = []
    for element_object in xml_elements:
            param_dictionary = {}
            param_dictionary['object_type'] = obj_type
            for param in element_object:
                # Parameter has child elements
                # Weapons.meta specific parse
                
                # Weapon OverrideForces
                if param.tag == 'OverrideForces':
                    override_forces_parsed = []
                    # OverrideForces Item
                    for item in param.findall('Item'):
                        force_item = {}
                        force_item[item.tag] = []
                        # BoneTag, Forcefront, forceback
                        for item_param in item.findall('*'):
                            if item_param.text:
                                force_item[item.tag].append({item_param.tag:item_param.text})
                            elif item_param.attrib:
                                force_item[item.tag].append({item_param.tag:item_param.attrib})
                        override_forces_parsed.append(force_item)
                    param_dictionary[param.tag] = override_forces_parsed

                # Weapon AttachPoints - Has multiple children elements
                elif param.tag == 'AttachPoints':
                    attach_items = []
                    # All attachpoint <Item> elements
                    for item in param.findall('*'):
                        attach_params = {}
                        attach_params[item.tag] = []
                        # AttachBone & Component elements
                        for bone_component in item.findall('*'):
                            # AttachBone Element
                            if bone_component.tag == 'AttachBone':
                                attach_params[item.tag].append({bone_component.tag: bone_component.text})
                            # Component Element - Has children
                            elif bone_component.tag == 'Components':
                                comp_elements = {}
                                comp_elements[bone_component.tag] = []
                                 # Component <Item> Elements
                                for component_item in bone_component.findall('*'):
                                    name_default = {}
                                    name_default[component_item.tag] = []
                                    # Dictionary for component elements
                                    for comp_item_param in component_item.findall('*'):
                                        # Add individual param for each component
                                        if comp_item_param.text:
                                            name_default[component_item.tag].append({comp_item_param.tag:comp_item_param.text})
                                        elif comp_item_param.attrib:
                                            name_default[component_item.tag].append({comp_item_param.tag:comp_item_param.attrib})
                                    comp_elements[bone_component.tag].append(name_default)
                                attach_params[item.tag].append(comp_elements)
                        attach_items.append(attach_params)
                    param_dictionary[param.tag] = attach_items

                elif len(param) > 0:
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
            elif k == 'OverrideForces':
                continue
            elif k == 'AttachPoints':
                continue
            elif k == 'WeaponFlags':
                if (k not in parameter_database):
                    parameter_database[k] = set()
                else: 
                    # Need to strip blank/ new line. Split flags to list
                    for flag in v.strip().strip('\n').strip().split(' '):
                        parameter_database[k].add(flag)
            #elif k == 'WeaponFlags' and (k in parameter_database):
                
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

def xml_writer(new_object, save_path, object_type=None):
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
            tree_root = object_tree.getroot().find('Infos/Item/Infos')
            object_item = LET.SubElement(tree_root, 'Item', {'type':'CWeaponInfo'})
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
            weap_sub_info = LET.SubElement(weap_item_root, 'Infos')
            object_item = LET.SubElement(weap_sub_info, 'Item', {'type':'CWeaponInfo'})

            LET.SubElement(weap_xml_root, 'VehicleWeaponInfos')
            LET.SubElement(weap_xml_root, 'Name').text = 'Custom Weapon Addons'

            object_tree = LET.ElementTree(weap_xml_root)

    # All children elements under object Item
    for attr, val in new_object.return_att_dict().items():
        # List datatype specifies parameter has more child elements
        if attr == 'object_type':
            pass
        elif val == "":
            LET.SubElement(object_item, attr)

        # Need to do overrideforces + attachpoints
        elif attr == 'OverrideForces':
            # Each item in val is a dictionary item
            overforce_ele = LET.SubElement(object_item, attr)
            for force in val:
                # Base item element
                item_ele = LET.SubElement(overforce_ele, 'Item')
                for dict_items in force['Item']:
                    for k, v in dict_items.items():
                        # Bonetag tag has text not attribute dictionary
                        if k == 'BoneTag':
                            LET.SubElement(item_ele, k).text = v
                        else:
                            LET.SubElement(item_ele, k, v)

        elif attr == 'AttachPoints':
            # AttachPoints attribute is a pretty complicated dictionary of dictionaries of dictionaries
            # Base attachpoints element
            attachpoints_base = LET.SubElement(object_item, attr)
            for base_item in val:
                attachpoints_item = LET.SubElement(attachpoints_base, 'Item')
                attach_bone = base_item['Item'][0]
                LET.SubElement(attachpoints_item, 'AttachBone').text = attach_bone['AttachBone']
                comp_base_ele = LET.SubElement(attachpoints_item, 'Components')
                for comp_items in base_item['Item'][1]['Components']:
                    component_item = LET.SubElement(comp_base_ele, 'Item')
                    for item_param_dict in comp_items['Item']:
                        for k, v in item_param_dict.items():
                            if k == 'Name':
                                LET.SubElement(component_item, k).text = v
                            else:
                                LET.SubElement(component_item, k, v)
                        
        # Elements with items are elements already
        elif isinstance(val, list):
            item1_subset = LET.SubElement(object_item, attr)
            for subitem in val:
                if isinstance(subitem, LET._Element):
                    item1_subset.append(subitem)
                else:
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

def element_maker(param, new_param_list):
    """
    Specific to weapons.meta file for now
    """
    element_dict = {}

    if param == 'OverrideForces':
        override_dict = {}
        override_list = []
        for group in new_param_list:
            override_dict['Item'] = []
            override_dict['Item'].append({group[0]: group[1]})
            override_dict['Item'].append({group[2]: {'value': group[3]}})
            override_dict['Item'].append({group[4]: {'value': group[5]}})
            override_list.append(override_dict.copy())

        element_dict['OverrideForces'] = override_list

    elif param == 'AttachPoints':
        attach_list = []
        
        # List of dictionaries of items
        for attach_dict in new_param_list:
            attach_list_dict = {'Item': []}
            # Each key is a list of the components
            for k, v in attach_dict.items():
                # AttachBone: Bone text
                attach_list_dict['Item'].append({v[0][0]:v[0][1]}.copy())
                comp_item_list_dict = {'Components': []}
                comp_item_param_dict = {'Item': []}

                for item in v[1:]:
                    att_name, att_val = item
                    # Default has a value: true/false dictionary
                    if att_name == 'Default':
                        comp_item_param_dict['Item'].append({att_name: {'value':att_val}.copy()}.copy())

                        comp_item_list_dict['Components'].append(comp_item_param_dict.copy())

                        comp_item_param_dict = {'Item': []}
                    else:
                        comp_item_param_dict['Item'].append({att_name: att_val}.copy())

                attach_list_dict['Item'].append(comp_item_list_dict.copy())

            attach_list.append(attach_list_dict.copy())

        element_dict[param] = attach_list

    elif param == 'Fx':
        element_dict[param] = []

        # Value attrib dictionaries
        val_list = ['MuzzleSmokeFxMinLevel', 'MuzzleSmokeFxIncPerShot','MuzzleSmokeFxDecPerSec','TracerFxChanceSP', 
                'TracerFxChanceMP', 'FlashFxChanceSP', 'FlashFxChanceMP', 'FlashFxAltChance', 'FlashFxScale',
                'FlashFxLightEnabled', 'FlashFxLightCastsShadows', 'FlashFxLightOffsetDist', 'GroundDisturbFxEnabled', 'GroundDisturbFxDist']

        for pair in new_param_list:
            # If element requires an attribute dictionary
            if pair[0] in val_list:
                new_ele = LET.Element(pair[0], {'value':pair[1]})

                element_dict[param].append(new_ele)
            # Element with XYZ Params
            elif isinstance(pair[1], list):
                xyz_dict = {}

                for item in pair[1]:
                    xyz_dict[item[0]] = item[1]
                new_ele = LET.Element(pair[0], xyz_dict)

                element_dict[param].append(new_ele)
            else:
                new_ele = LET.Element(pair[0])
                new_ele.text = pair[1]
                element_dict[param].append(new_ele)
                
    else:
        # List of elements
        element_dict[param] = []
        for pair in new_param_list:
            new_ele = LET.Element(pair[0])
            new_ele.text = pair[1]
            element_dict[param].append(new_ele)

    return element_dict
