from collections import defaultdict
import xml.etree.ElementTree as ET

class Coordinates(object):
    def __init__(self, val = 0, lat = 0, long = 0):
        self.val = val
        self.lat = lat
        self.long = long

class Properites:
    def __init__(self, oneway = False):
        self.oneway = oneway

        
class Graph(Properites):
    def connect(self, root):
        roads = defaultdict(list)
        coordinates = {}
        oneway = set()
        oneway_index = {}

        w = 2

        while root[w].tag == "way":
            nd_len = 0
            for i in root[w]:
                if i.tag == "nd":
                    nd_len += 1
                elif i.tag == "tag":
                    if i.get("k") == "oneway" and i.get("v") == "yes":
                        for nd in root[w]:
                            if nd.tag == "nd":
                                oneway.add(int(nd.get("ref")))
                else:
                    break
            
            for i in range(nd_len):
                if root[w][i].tag == "nd" and nd_len > 1:
                    
                    if i > 0 and i < nd_len - 1:
                        roads[int(root[w][i].get("ref"))].append(int(root[w][i - 1].get("ref")))
                        roads[int(root[w][i].get("ref"))].append(int(root[w][i + 1].get("ref")))
                        

                    elif i == 0:
                        roads[int(root[w][i].get("ref"))].append(int(root[w][i + 1].get("ref")))

                    elif i == nd_len - 1:
                        roads[int(root[w][i].get("ref"))].append(int(root[w][i - 1].get("ref")))
                 

            w += 1
        
        while w < len(root) and root[w].tag == "node":
            coordinates[int(root[w].get("id"))] = (float(root[w].get("lat")), float(root[w].get("lon")))
            w += 1

        return roads, coordinates

source = 202176692
end = 10127810693


def bfs(source, end, roads, coordinates):
    from collections import deque
    seen = set() 
    seen.add(source)
    q = deque()
    q.append(source)
    parent = {source: None}

    path = []
    while q:
        node = q.popleft()
        for nei_node in roads[node]:
            if nei_node not in seen:
                seen.add(nei_node)
                q.append(nei_node)
                path.append(nei_node)
                parent[nei_node] = node
                if nei_node == end:
                    print(True)
                    break

    if end not in parent:
        return []

    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path, coordinates

tree = ET.parse("Nashville_Chunck.osm")
root = tree.getroot()
filebruh = bfs(202176692, 7740969065, Graph().connect(root)[0], Graph().connect(root)[1])

def write_gpx(path, coordinates):
    for i in path:
        print(f"<trkpt lat=\"{coordinates[i][0]}\" lon=\"{coordinates[i][1]}\"/>")
            
print(filebruh[0]) 

