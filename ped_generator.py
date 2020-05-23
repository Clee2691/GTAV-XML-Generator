import xml.etree.ElementTree as ET


class Ped:
    def __init__(self, ped_dictionary):
        for k, v in ped_dictionary.items():
            setattr(self, k, v)
        print('New ped created!')

    def display_attributes(self):
        counter = 1
        for attr, val in self.__dict__.items():
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
                ped_dictionary[param.tag] = param.attrib['value']
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
    new_ped = ped_template

    new_ped.update_attr(new_val_dict)

    return new_ped

    
if __name__ == "__main__":
    ped_list = ped_generator('database/peds.ymt.xml')

    ped_input = input('Template: ')

    for ped in ped_list:
        if ped.Name == 'ped_input':
            ped_template = ped
            break
    
    custom_val_dict = {'Pedtype': 'CIVFEMALE', 'PropsName': None, 'PedCapsuleName': 'Test_Capsule'}
    generate_new_ped(ped_template, custom_val_dict)

