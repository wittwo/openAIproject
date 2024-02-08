import os
import shutil
import json
from typing import Any, List, Dict

from zipfile import ZipFile


def getpbits(PATH_NAME: str):
    files_list = []
    files_names = []
    files_MAX31 = []
    ccont = 0

    for file in os.listdir(PATH_NAME):
        if file.endswith(".pbit"):
            files_list.append(os.path.join(file))
        

    for file in files_list:
        files_names.append(file.split('.pbit')[0])
    
    for file in files_names:
        files_MAX31.append(file[:28])
        
    files_count=len(files_MAX31)

    for index in range(files_count - 1):
        if files_MAX31[index] == files_MAX31[index + 1]:
            files_MAX31[index] = f"{files_MAX31[index]}_{ccont}"
            ccont += 1
            files_MAX31[index + 1] = f"{files_MAX31[index + 1]}_{ccont}"
            ccont += 1

    return files_list,files_names,files_MAX31,files_count

class ReportExtractor():

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.result = []
        self.result2 = []

    def extract(self):
        pathFolder = f'{self.path}/temp_{self.name[:-5]}'
        try: shutil.rmtree(pathFolder)
        except:
            print(f'folder {pathFolder} not present')
        f = ZipFile(f'{self.path}/{self.name}', 'r')
        f.extractall(pathFolder)
        report_layout = json.loads(
            open(f'{pathFolder}/DataModelSchema', 'r', encoding='utf-16 le').read())

        f.close()
        
        self.result =  report_layout
        self.result2= json.load(open(f'{pathFolder}/DataModelSchema', 'r', encoding='utf-16 le')
        )

def ExtractDataModelSchemas(PATH_NAME: str, files_list: List[str],files_names: List[str],files_count: int):
    
    json_data = {}
    for plik in range(0,files_count):
        Extractor=ReportExtractor(PATH_NAME,files_list[plik])
        Extractor.extract()
        DataModelSchemaJSON = Extractor.result2
    
        print(files_names[plik])
        json_data[files_names[plik]]=DataModelSchemaJSON

    dataModelSchemas = json.dumps(json_data, indent=2)

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=2)
    
    return dataModelSchemas
