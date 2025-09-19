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
        oneway_index = {}
        w = 2

        while root[w].tag == "way":
            nd_len = 0
            for i in root[w]:
                if i.tag == "nd":
                    nd_len += 1
                elif i.tag == "tag":
                    if i.get("k") == "oneway" and i.get("v") == "yes":
                        for nd in range(len(root[w])):
                            if root[w][nd].tag == "nd":
                                oneway_index[int(root[w][nd].get("ref"))] = nd 
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

        return roads, coordinates, oneway_index

source = 202176692
end = 10127810693


def bfs(source, end, roads, coordinates, oneway_index):
    from collections import deque
    seen = set() 
    seen.add(source)
    q = deque()
    q.append(source)
    parent = {source: None}

    path = []
    path_found = False
    while q:
        node = q.popleft()

        if node not in oneway_index:
            for nei_node in roads[node]:
                if nei_node not in seen:
                    seen.add(nei_node)
                    q.append(nei_node)
                    path.append(nei_node)
                    parent[nei_node] = node
                    if nei_node == end:
                        print(True)
                        path_found = True
                        break

        elif node in oneway_index:
            for nei_node in roads[node]:
                if nei_node not in seen:
                    if nei_node in oneway_index:
                        if oneway_index[node] < oneway_index[nei_node]:
                                seen.add(nei_node)
                                q.append(nei_node)
                                path.append(nei_node)
                                parent[nei_node] = node
                                if nei_node == end:
                                    print(True)
                                    path_found = True
                                    break
                    else:
                        seen.add(nei_node)
                        q.append(nei_node)
                        path.append(nei_node)
                        parent[nei_node] = node
                        if nei_node == end:
                            print(True)
                            path_found = True
                            break
        if path_found:
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

def A_star(source, end, roads, coordinates, oneway_index):
    import heapq
    import math

    def heuristic(source, end, coordinates):
        lat1, lat2 = math.radians(coordinates[source][0]), math.radians(coordinates[end][0])
        lon1, lon2 = math.radians(coordinates[source][1]), math.radians(coordinates[end][1])
        radius = 3959
        distance = (2*radius) * math.asin(math.sqrt(math.sin((lat2 - lat1)/ 2)**2) + math.cos(lat1) * math.sin((lon2 - lon1)/2)**2)
        return distance

    def cost(node1, node2, coordinates, currcost):
        lat1, lat2 = math.radians(coordinates[node1][0]), math.radians(coordinates[node2][0])
        lon1, lon2 = math.radians(coordinates[node1][1]), math.radians(coordinates[node2][1])
        radius = 3959
        distance = (2*radius) * math.asin(math.sqrt(math.sin((lat2 - lat1)/ 2)**2) + math.cos(lat1) * math.sin((lon2 - lon1)/2)**2)
        return distance + currcost

    seen = set()
    seen.add(source)
    open = []
    heapq.heapify(open)
    heapq.heappush(open, (0, source))
    open.append((0, source))
    parent = {source: None}
    g_score = {source: 0}
    h_score = {source: heuristic(source, end, coordinates)}
    f_score = {source: g_score[source] + h_score[source]}

    while open:
        node = heapq.heappop(open)[1]

        for nei_node in roads[node]:
            if nei_node not in seen:
                g_score[nei_node] = cost(node, nei_node, coordinates, g_score[node])
                h_score[nei_node] = heuristic(nei_node, end, coordinates)
                f_score[nei_node] = g_score[nei_node] + h_score[nei_node]
                heapq.heappush(open, (f_score[nei_node], nei_node))
                seen.add(nei_node)
                parent[nei_node] = node
                if nei_node == end:
                    open = []
                    print(True)
                    break

    if end not in parent:
        return [], False
    
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    return path, coordinates

tree = ET.parse("Nashville_Chunck.osm")
root = tree.getroot()
#bfsbruh = bfs(202176692, 7740969065, Graph().connect(root)[0], Graph().connect(root)[1], Graph().connect(root)[2])
Abruh = A_star(202176692, 7740969065, Graph().connect(root)[0], Graph().connect(root)[1], Graph().connect(root)[2])
def write_gpx(path, coordinates):
    for i in path:
        print(f"<trkpt lat=\"{coordinates[i][0]}\" lon=\"{coordinates[i][1]}\"/>")
            
write_gpx(Abruh[0], Abruh[1])