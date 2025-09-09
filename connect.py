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
        tree = ET.parse("Nashville_Chunck.osm")
        root = tree.getroot()

        w = 2
        while root[w].tag == "way":
            for nd in root[w]:
                if nd.tag == "nd":
                    roads[Node(int(root[w].id))].append(int(nd.ref))
            w += 1