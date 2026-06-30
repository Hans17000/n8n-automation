import xml.etree.ElementTree as ET
import sys

xml_file = sys.argv[1]
for _, elem in ET.iterparse(xml_file, events=('end',)):
    if elem.tag != 'product':
        continue
    pid = elem.get('id','')
    if pid == '155703':
        for child in elem:
            text = (child.text or '').strip()
            if len(text) > 100:
                text = text[:100] + '...'
            print(f'  <{child.tag}> = {text}')
        break
    elem.clear()