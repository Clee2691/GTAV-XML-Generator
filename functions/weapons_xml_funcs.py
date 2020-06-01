import lxml.etree as LET
from pathlib import Path

class Weapon:
    def __init__(self, weapon_params):
        for k, v in weapon_params:
            setattr(self, k, v)
    

def parse_weapons_meta(path_weapon_file):

    wep_file = LET.parse(path_weapon_file)
    wep_root = wep_file.getroot()
    if wep_root.tag == 'CWeaponInfoBlob':
        print(wep_root.tag)

def weapon_meta_writer(save_path):
    save_path = Path(f'{save_path}/weapons.meta')

    if save_path.is_file():
        xml_parser = LET.XMLParser(remove_blank_text=True)
        weap_tree = LET.ElementTree(save_path, parser=xml_parser)

        
    else:
        print('false')


if __name__ == '__main__':
    xml_file = 'database/weapons.meta'
    parse_weapons_meta(xml_file)
    weapon_meta_writer('weapon_xml_files')