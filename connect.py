"""Route search over OpenStreetMap road data (downtown Nashville).

Parses an .osm file into an adjacency list and finds a route between two
node ids with BFS, DFS, Dijkstra, or A*. The route is written to path.gpx so
it can be overlaid on the map in JOSM.

Usage:
    python connect.py --algo astar --source 202176692 --end 5741054510
    python connect.py --algo all            # run and compare every algorithm
"""
import argparse
import heapq
import math
import time
import xml.etree.ElementTree as ET
from collections import defaultdict, deque

EARTH_RADIUS_MILES = 3959

ROAD_SPEEDS_MPH = {
    "motorway": 65, "motorway_link": 45, "trunk": 55, "primary": 45,
    "primary_link": 40, "secondary": 40, "secondary_link": 35,
    "tertiary": 35, "tertiary_link": 30, "residential": 25,
    "living_street": 15, "service": 10, "alley": 10, "unclassified": 25,
    "track": 15,
}
MAX_SPEED_MPH = max(ROAD_SPEEDS_MPH.values())


class Graph:
    """Road network: adjacency list, node coordinates and per-node speed."""

    def __init__(self, roads=None, coordinates=None, mph=None):
        self.roads = roads if roads is not None else defaultdict(list)
        self.coordinates = coordinates if coordinates is not None else {}
        self.mph = mph if mph is not None else {}

    @classmethod
    def from_osm(cls, path):
        root = ET.parse(path).getroot()
        graph = cls()

        for node in root.iter("node"):
            graph.coordinates[int(node.get("id"))] = (
                float(node.get("lat")), float(node.get("lon")))

        for way in root.iter("way"):
            tags = {t.get("k"): t.get("v") for t in way.iter("tag")}
            speed = ROAD_SPEEDS_MPH.get(tags.get("highway"))
            if speed is None:
                continue  # not a drivable road
            refs = [int(nd.get("ref")) for nd in way.iter("nd")]
            refs = [r for r in refs if r in graph.coordinates]
            oneway = tags.get("oneway")
            if oneway == "-1":
                refs.reverse()
            forward_only = oneway in ("yes", "true", "1", "-1")

            for ref in refs:
                graph.mph[ref] = max(graph.mph.get(ref, 0), speed)
            for a, b in zip(refs, refs[1:]):
                graph.roads[a].append(b)
                if not forward_only:
                    graph.roads[b].append(a)
        return graph

    def distance(self, a, b):
        """Great-circle (haversine) distance in miles."""
        lat1, lon1 = map(math.radians, self.coordinates[a])
        lat2, lon2 = map(math.radians, self.coordinates[b])
        h = (math.sin((lat2 - lat1) / 2) ** 2
             + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
        return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(h))

    def travel_time(self, a, b):
        """Hours to drive edge a->b at the slower of the two nodes' speeds."""
        speed = min(self.mph.get(a, MAX_SPEED_MPH), self.mph.get(b, MAX_SPEED_MPH))
        return self.distance(a, b) / speed


def _reconstruct(parent, end):
    if end not in parent:
        return []
    path, cur = [], end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]


def bfs(graph, source, end):
    """Fewest road segments. Returns (path, nodes_expanded)."""
    parent = {source: None}
    queue = deque([source])
    expanded = 0
    while queue:
        node = queue.popleft()
        expanded += 1
        if node == end:
            break
        for nei in graph.roads[node]:
            if nei not in parent:
                parent[nei] = node
                queue.append(nei)
    return _reconstruct(parent, end), expanded


def dfs(graph, source, end):
    """Any route (not optimal); iterative to avoid recursion limits."""
    parent = {source: None}
    stack = [source]
    visited = set()
    expanded = 0
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        expanded += 1
        if node == end:
            break
        for nei in graph.roads[node]:
            if nei not in visited:
                parent[nei] = node
                stack.append(nei)
    if end not in visited:
        return [], expanded
    return _reconstruct(parent, end), expanded


def _best_first(graph, source, end, heuristic):
    """Shared Dijkstra / A* core, minimising travel time."""
    g = {source: 0.0}
    parent = {source: None}
    open_heap = [(heuristic(source), source)]
    closed = set()
    expanded = 0
    while open_heap:
        _, node = heapq.heappop(open_heap)
        if node in closed:
            continue
        closed.add(node)
        expanded += 1
        if node == end:
            break
        for nei in graph.roads[node]:
            if nei in closed:
                continue
            cost = g[node] + graph.travel_time(node, nei)
            if cost < g.get(nei, math.inf):
                g[nei] = cost
                parent[nei] = node
                heapq.heappush(open_heap, (cost + heuristic(nei), nei))
    if end not in closed:
        return [], expanded
    return _reconstruct(parent, end), expanded


def dijkstra(graph, source, end):
    """Fastest route by travel time."""
    return _best_first(graph, source, end, lambda n: 0.0)


def a_star(graph, source, end):
    """Fastest route; straight-line distance at top speed is admissible."""
    return _best_first(graph, source, end,
                       lambda n: graph.distance(n, end) / MAX_SPEED_MPH)


ALGORITHMS = {"bfs": bfs, "dfs": dfs, "dijkstra": dijkstra, "astar": a_star}


def route_stats(graph, path):
    miles = sum(graph.distance(a, b) for a, b in zip(path, path[1:]))
    minutes = 60 * sum(graph.travel_time(a, b) for a, b in zip(path, path[1:]))
    return miles, minutes


def write_gpx(path, coordinates, filename="path.gpx"):
    start, end = coordinates[path[0]], coordinates[path[-1]]
    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="Map_Route_Search_Algorithm">\n')
        f.write(f'  <wpt lat="{start[0]}" lon="{start[1]}"><name>Start</name></wpt>\n')
        f.write(f'  <wpt lat="{end[0]}" lon="{end[1]}"><name>End</name></wpt>\n')
        f.write('  <trk>\n    <name>path</name>\n    <trkseg>\n')
        for node in path:
            lat, lon = coordinates[node]
            f.write(f'      <trkpt lat="{lat}" lon="{lon}"/>\n')
        f.write('    </trkseg>\n  </trk>\n</gpx>\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--osm", default="Nashville_Chunck.osm")
    parser.add_argument("--source", type=int, default=202176692)
    parser.add_argument("--end", type=int, default=5741054510)
    parser.add_argument("--algo", choices=[*ALGORITHMS, "all"], default="astar")
    parser.add_argument("--gpx", default="path.gpx")
    args = parser.parse_args()

    graph = Graph.from_osm(args.osm)
    print(f"Loaded {len(graph.coordinates):,} nodes, "
          f"{sum(map(len, graph.roads.values())):,} directed road segments")

    names = list(ALGORITHMS) if args.algo == "all" else [args.algo]
    best = None
    for name in names:
        t0 = time.perf_counter()
        path, expanded = ALGORITHMS[name](graph, args.source, args.end)
        ms = (time.perf_counter() - t0) * 1000
        if not path:
            print(f"{name:>8}: no route found ({expanded:,} nodes expanded, {ms:.1f} ms)")
            continue
        miles, minutes = route_stats(graph, path)
        print(f"{name:>8}: {len(path):,} nodes, {miles:.2f} mi, {minutes:.1f} min drive, "
              f"{expanded:,} expanded, {ms:.1f} ms")
        if best is None or name == args.algo or name == "astar":
            best = path

    if best:
        write_gpx(best, graph.coordinates, args.gpx)
        print(f"Wrote {args.gpx}")


if __name__ == "__main__":
    main()
