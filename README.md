# Map Route Search Algorithm

Finding the fastest route between two points on real OpenStreetMap road data for downtown Nashville, and comparing how BFS, DFS, Dijkstra, and A* search.

## 🎮 Live Demo

[**Try the interactive visualizer →**](https://rahulmoka.com/projects/astar-route-search)

Pick BFS, DFS, Dijkstra, or A*, draw walls and weighted traffic, drag the start and end nodes, and watch each algorithm search the grid step by step. A dependency-free standalone version lives in [`/docs`](./docs): open `docs/index.html` in a browser, or serve it with GitHub Pages (Settings → Pages → `main` / `/docs`).

## Overview

`connect.py` parses an `.osm` file into a graph:

- **Ways** = roads (e.g. "Cleveland Avenue"), filtered to drivable `highway` types with a speed per road class
- **Nodes** = points along those roads (lat/lon)

It handles `oneway=yes/-1`, builds an adjacency list, runs a search, and exports the route as GPX so you can overlay it on the map in JOSM.

| Algorithm | Optimises | Notes |
|-----------|-----------|-------|
| BFS | fewest road segments | unweighted |
| DFS | nothing (finds *a* route) | shows why uninformed depth-first is a bad router |
| Dijkstra | travel time | edge cost = haversine distance ÷ road speed |
| A* | travel time | heuristic = straight-line distance at top speed (admissible) |

Sample run on the included Nashville data:

```
     bfs: 81 nodes, 2.38 mi, 3.2 min drive, 9,136 expanded
     dfs: 1,611 nodes, 27.02 mi, 103.1 min drive, 34,982 expanded
dijkstra: 117 nodes, 2.20 mi, 2.9 min drive, 7,857 expanded
   astar: 117 nodes, 2.20 mi, 2.9 min drive, 2,458 expanded
```

A* finds the same fastest route as Dijkstra while expanding about 3× fewer nodes.

## Usage

```bash
python connect.py --algo astar --source 202176692 --end 5741054510
python connect.py --algo all        # compare every algorithm
python -m pytest                    # unit tests
```

Then open `Nashville_Chunck.osm` in JOSM (`josm-tested.jar` is included) and load `path.gpx` on top of it to see the route. To pick your own endpoints, select two nodes in JOSM and pass their ids as `--source` and `--end`.
