import xml.etree.ElementTree as ET
from settings_storage import SettingsStorage


class XmlSettingsStorage(SettingsStorage):

    
    def save(self, data, file_path):
        """
        Адаптируем сохранение: преобразуем словарь в XML-дерево.
        Использует API xml.etree.ElementTree (Element, SubElement, ElementTree).
        """
        root = ET.Element("settings")
        for key, value in data.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def load(self, file_path):
        """
        Адаптируем загрузку: преобразуем XML-дерево в словарь.
        Использует API xml.etree.ElementTree (parse, iter).
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        data = {}
        for child in root:
            data[child.tag] = child.text
        return data