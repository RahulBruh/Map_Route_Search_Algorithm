from collections import defaultdict
import xml.etree.ElementTree as ET
class Node(object):
    def __init__(self, val = 0, lat = 0, long = 0):
        self.val = val
        self.lat = lat
        self.long = long
        
class Graph(object):
    def connect(self, node):
        roads = defaultdict(list)
        coordinates = {}

        w = 2

        while root[w].tag == "way":
            for nd in root[w]:
                if nd.tag == "nd":
                    roads[int(root[w].get("id"))].append(int(nd.get("ref")))
            w += 1
        
        while w < len(root) and root[w].tag == "node":
            coordinates[int(root[w].get("id"))] = (float(root[w].get("lat")), float(root[w].get("lon")))
            w += 1

        return coordinates
    
tree = ET.parse("Nashville_Chunck.osm")
root = tree.getroot()
print(Graph().connect(root))