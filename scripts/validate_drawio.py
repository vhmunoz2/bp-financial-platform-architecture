import xml.etree.ElementTree as ET
from pathlib import Path

path = Path('diagrams/Arquitectura_C4_Banca_Digital_BP.drawio')
root = ET.parse(path).getroot()
pages = root.findall('diagram')
print('page_count:', len(pages))
dangling = []
for page in pages:
    cells = page.findall('.//mxCell')
    ids = {cell.attrib['id'] for cell in cells}
    vertices = sum(cell.attrib.get('vertex') == '1' for cell in cells)
    edges = sum(cell.attrib.get('edge') == '1' for cell in cells)
    for cell in cells:
        if cell.attrib.get('edge') == '1':
            if cell.attrib.get('source') not in ids or cell.attrib.get('target') not in ids:
                dangling.append((page.attrib['name'], cell.attrib['id']))
    print(page.attrib['name'], 'vertices:', vertices, 'edges:', edges)
print('dangling_edges:', dangling)
if len(pages) != 3 or dangling:
    raise SystemExit(1)
