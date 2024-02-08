import re
import pandas as pd
import base64
import json
import zlib
import xlsxwriter
import tempfile
import subprocess
import webbrowser
from typing import Any, List, Dict
from tabulate import tabulate
from itertools import groupby

def extractFeedFromString(string):
    feed_list=[]
    key_phrase=["PUT YOUR DEFINITION HERE - 08.02.24"]
    
    for key in key_phrase:
        match = re.findall(key+"(.*?)"+'"', string) #"\" are added as the special characters have to be escaped
        if match:
            feed_list=feed_list+match #match #.group(1)
            
        #else:
        #    return ""
    return feed_list

def FeedExtract(dataModelSchemas,files_names: List[str]):
    feeds=[]
    spisFeed = {}
    dataModelSchemasParsed = json.loads(dataModelSchemas)
    for currentPbitName in files_names:

        for x in dataModelSchemasParsed[currentPbitName]["model"]["tables"]:   #extracting legend expression from partitions
        
            partitions=x['partitions']
            for partition in partitions:
                if "PUT YOUR PHRASE HERE" in str(partition['source']['expression']): #Looking for phrase in M langauge definition of a table
                
                    feed=extractFeedFromString(str(partition['source']['expression']))
                    feeds=feeds+feed
        
        uniqueFeeds = list(set(feeds)) #Sometimes one feed is used more tables, henve remove duplicates
           
        spisFeed[currentPbitName]=uniqueFeeds
    
    with open("Feedy.json", "w", encoding="utf-8") as file:
        json.dump(spisFeed, file, ensure_ascii=False, indent=2)
    webbrowser.open("Feedy.json")
    return spisFeed
    print("Results saved successfully to .\Feedy.json")

def SearchForSpecificFeedContains(dataModelSchemas, files_names: List[str], lookUp: str):
    spisFeed = FeedExtract(dataModelSchemas, files_names)
    count = 0
    analityki = []
    for key, val in spisFeed.items():
        value = [item.lower() for item in val]
        for item in value:
            if lookUp.lower() in item:
                count += 1
                analityki.append((key, item))
    
    #grouping extracted feeds by analytics
    grouped_analityki = {}
    for item in analityki:
        if item[0] not in grouped_analityki:
            grouped_analityki[item[0]] = [item[1]]
        else:
            grouped_analityki[item[0]].append(item[1])

    print('\nFeedy zawierające "', lookUp, '" występują', count, 'razy w', len(grouped_analityki), 'analitykach\n')

    #preparing data for tabulation    
    table_data = []
    for i, (key, values) in enumerate(grouped_analityki.items(), start=1):
        table_data.append([i, key, ", ".join(values)])

    table = tabulate(table_data, headers=["No.", "Analityka", "Feedy"], tablefmt="ascii")
    print(table)

def SearchForSpecificFeedExact(dataModelSchemas, files_names: List[str], lookUp: str):
    spisFeed = FeedExtract(dataModelSchemas,files_names)
    count =0
    analityki = []
    for key, val in spisFeed.items():
        value = [item.lower() for item in val]
        if lookUp.lower() in value:
            count += 1
            analityki.append(key)
        
    
    print('\n Feed "',lookUp,'" znajduje się w ',len(analityki), " analitykach \n")
    for item in analityki:
        print(item)
        

def LegendExtract(pbit_table):
    headers=[]
    codedjson=[]
    legendTablesCount=0
    legendContents = []
    for x in pbit_table:   #extracting legend expression from partitions
        
        partitions=x['partitions']
        for partition in partitions:
            if "Legend" in partition['name']:
               
                counter +=1
                codedjson.append([x['name'],str(partition['source']['expression'])]) #saving to list
                for col in x['columns']:
                    #print(col['name'])
                    
                    #Checking for is Hidden. Sometimes in DataModelSchema under partitions-->columns-->there is another column
                    #with the property isHidden. It is not visible in PowerQuery but was being added by the script
                    #So now I am checking for hidden ones and ignore them. 
                    #Code is set for 3 columns, and only 3 headers should be present. Additional ones are likely to be hidden.
                    try:
                        col["type"]=="rowNumber"
                        pass
                    except:
                        headers.append([counter,col['name']]) #getting columns names

    #Extracting legend content from coded definition
    for i in range(0,legendTablesCount):
        #extracting content of Legend table
        
        definition=codedjson[i][1][codedjson[i][1].find('FromText')+10:].split('"')[0]
        
        decoded_base64 = base64.b64decode(definition)
        
        decompress=zlib.decompress(decoded_base64,wbits = -zlib.MAX_WBITS)
        
        dec=json.loads(decompress)
        
        
        json_len=len(dec)
        
        #extracting rows and columns from decompressed file, where json_len counts how many rows are there.
        for r in range(0,json_len):
            try:
                val0=dec[r][0] #row i column 0 and checking if the value is empty. If yes the replace text.
                
                if bool(val0):
                    pass
                else:
                    val0="N/A"
            except:
                val0=None
            try:
                val1=dec[r][1] #row i column 1
                
                if bool(val1):
                    pass
                else:
                    val1="N/A"
            except:
                val1=None
            try:
                val2=dec[r][2] #row and column 2
                
                if bool(val2):
                    pass
                else:
                    val2="N/A"
            except:
                val2=None
                
            legendContents.append([codedjson[i][0],val0,val1,val2])
    
    return codedjson,headers,legendTablesCount

def SaveTabletoExcel(pbitdf,headers,sheet_name,globaltab,globaltabnum):
    
    uniques=pbitdf[0].unique()
    tb_count=False #used for determining if it is the first table and later how far the next one has to 
    tab_len=0
    it=1 #it is a iteration symbol which corresponds to the number in headers
    tab_count=0 #for tab count
    #for each table we will save it separately
    for title in uniques: #title for eg. Legenda-opis,Legenda-wskaźniki etc. titles of tables with legend description
        
        filtered=pbitdf.loc[pbitdf[0]==title]
        
        filtered_list = [tup for tup in headers if tup[0] == it]
        filtered_list = [x[1] for x in filtered_list]
        
        filtered=filtered.iloc[:,1:4]
        try:
            filtered=filtered.rename({1: filtered_list[0],2: filtered_list[1],3: filtered_list[2],},axis=1)
            
        except:
            try:
                filtered=filtered.rename({1: filtered_list[0]},axis=1)
            except:
                filtered=filtered.rename({1: "No column name"},axis=1)
                
            try:
                filtered=filtered.rename({2: filtered_list[1]},axis=1)
            except:
                filtered=filtered.rename({2: "No column name"},axis=1)
                
            try:
                filtered=filtered.rename({3: filtered_list[2]},axis=1)
            except:
                filtered=filtered.rename({3: "No column name"},axis=1)
                
                
        filtered=filtered.sort_values(by=filtered.columns[0])
        
        if tb_count==False:
            
            filtered.to_excel(writer,sheet_name=sheet_name,startrow=2,index=False)
            tab_len=filtered.shape[0] #this will later tell how far next table on the same sheet has to be
            globaltab.append([sheet_name,title,tab_len])
            tb_count = True #forcing it to go through else statement
            
        else:
            
           # filtered.to_excel(writer,sheet_name=sheet_name,startrow=(tab_len+6),index=False)
            globaltab.append([sheet_name,title,filtered.shape[0]])
            tab_len=tab_len+4+filtered.shape[0]
            
        it +=1
        tab_count +=1
        
    globaltabnum.append([sheet_name,tab_count])

def VersionCompare(dataModelSchemas,files_names: List[str]):

    dataModelSchemasParsed = json.loads(dataModelSchemas)
    versionTable = [["Aanlityka", "Wersja z tytułu", "Wersja z miary"]]
    for currentPbitName in files_names:
        versionFromFileTitle = re.findall("([0-9]+[.]+[0-9]+[.]+[0-9]+)", currentPbitName)[0]
        
        for x in dataModelSchemasParsed[currentPbitName]["model"]["tables"]:   #Searching through table for a measure called "# Wersja". 
            try:
                x['measures']
            
                for measure in x['measures']:
                    if measure['name']=="# Wersja":
                    
                        VersionFromMeasure=measure['expression'].replace('"','')
                    
                        if versionFromFileTitle==VersionFromMeasure:
                            
                            pass
                        else:
                            newRow = [currentPbitName,versionFromFileTitle,VersionFromMeasure]
                            versionTable.append(newRow)
                
            except:
                pass
    versionTable = tabulate(versionTable, headers="firstrow", tablefmt="ascii")
    print(versionTable)

    
def SearchinMeasures(dataModelSchemas, files_names: List[str], lookUp: str) -> Dict[str, List[tuple]]:
    dataModelSchemasParsed = json.loads(dataModelSchemas)
    results = {}
    
    for currentPbitName in files_names:
        currentPbitResults = []
        
        for x in dataModelSchemasParsed[currentPbitName]["model"]["tables"]:
            try:
                x['measures']
            
                for measure in x['measures']:
                    measureName = measure['name']
                    measureDAX = str(measure["expression"])
                    
                    if lookUp in measureDAX:
                        currentPbitResults.append((measureName, " - ", measureDAX))
                
            except:
                pass
        
        if currentPbitResults:
            results[currentPbitName] = currentPbitResults

        with open("measure.json", "w", encoding="utf-8") as output_file:
            json.dump(results, output_file, indent=4, ensure_ascii=False)

    webbrowser.open("measure.json")
    #subprocess.call(['explorer', temp_file.name])
    #webbrowser.open('file://' + temp_file.name)

    
    return results


def SearchForMeasures(dataModelSchemas, files_names, lookUp):
    dataModelSchemasParsed = json.loads(dataModelSchemas)
    measuresUsed = []

    for currentPbitName in files_names:
        for x in dataModelSchemasParsed[currentPbitName]["model"]["tables"]:
            try:
                x['measures']
                for measure in x['measures']:
                    measureName = measure['name']
                    if lookUp.lower() in measureName.lower():
                        measuresUsed.append([currentPbitName, measureName])
            except:
                pass
    
    measuresUsed.sort(key=lambda x: x[0])  # Sort by fileName
    grouped_measures = []
    for key, group in groupby(measuresUsed, lambda x: x[0]):
        grouped_measures.append([key, [x[1] for x in group]])
    
    table_headers = ["File Name", "Measure Names"]
    print(tabulate(grouped_measures, headers=table_headers, tablefmt="fancy_grid"))
    return measuresUsed
        