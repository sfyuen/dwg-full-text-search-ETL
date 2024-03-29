import aspose.cad as cad
from aspose.pycore import cast
from elasticsearch import Elasticsearch
from datetime import datetime, timezone
import re
import os

# Handle AutoCAD control codes
re_dict={
    "%%o" : "",
    "%%u" : "",
    "%%d" : "°",
    "%%p" : "±",
    "%%c" : "∅",
    "%%%" : "%"
}

# Directory of dwg files
directory = 'dwg'
# Target index of elasticsearch
esindex = 'cad'
# Credential of elasticsearch
escredential = ""

# Initial the index of elasticsearch
def init_es():
     if es.indices.exists(index=esindex):
         print(f'Index exists, data will be loaded to {esindex}')
     else:
         mapping = { 
           "mappings":{ 
               "properties":{
                 "filename":{
                     "type": "keyword"
                 },
                 "size":{
                     "type": "long"
                 },
                 "path":{
                     "type": "keyword"
                 },
                 "content": {
                     "type": "text",
                         "fields": {
                             "keyword": {
                                 "type": "keyword"
                         }
                     }
                 },
                 "edited":{
                   "type":"date"
                 }
               }
           }
         }
         es.indices.create(index=esindex, body=mapping)
         print(f'Created index {esindex}')

# Extract TEXT & MTEXT from dwg by Aspose library
def extract(file):
    image = cad.fileformats.cad.CadImage.load(file)
    castedImage = cast(cad.fileformats.cad.CadImage, image)
    data = []

    for block in castedImage.block_entities.values:
        for entity in block.entities:
            if entity.type_name == cad.fileformats.cad.cadconsts.CadEntityTypeName.TEXT:
                text = cast(cad.fileformats.cad.cadobjects.CadText, entity)
                data.append(text.default_value)
            if entity.type_name == cad.fileformats.cad.cadconsts.CadEntityTypeName.MTEXT:
                mtext = cast(cad.fileformats.cad.cadobjects.CadMText, entity)
                data.append(mtext.full_clear_text)

    return data

# Clean the data
# 1. Split the strings by new line characters
# 2. Remove leading & trailing spaces
# 3. Replace AutoCAD control codes with Unicode characters
def transform(lst):
    cleaned = []
    for s in lst:
        for x in s.splitlines():
            x = x.strip()
            if x != '':
                for k, v in re_dict.items():
                    x = (re.sub(k, v, x, flags=re.IGNORECASE))
                cleaned.append(x)
    return cleaned

# Load the data to elasticsearch
def load(data,fn,stat):
    es.index(
        index=esindex,
        body={
            "filename": fn,
            "size": stat.st_size,
            "path": "bar", #url path to your files
            "content": data,
            "edited": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        }
    )

es = Elasticsearch(escredential)
init_es()
for filename in os.listdir(directory):
    fullpath = os.path.join(directory, filename)
    ext = os.path.splitext(filename)[-1].lower()
    if os.path.isfile(fullpath) and ext == '.dwg':
        extracted = extract(fullpath)
        transformed = transform(extracted)
        load(transformed,filename,os.stat(fullpath))
        print(f'loaded file {filename}')

