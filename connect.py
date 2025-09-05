import xml.etree.ElementTree as ET

tree = ET.parse("Nashville_Chunck.osm")
root = tree.getroot()

print(root.tag)
print(len(root))

for i in range(len(root)):
    print(root[i].tag)