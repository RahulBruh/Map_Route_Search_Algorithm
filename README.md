# Map_Route_Search_Algorithm
Finding the fastest route from one location to another using different search alogirhtms, and visually show the differences between each search alogirthm.

OSM Pathfinding with Python
📌 Overview

This project parses OpenStreetMap (.osm) data into a graph structure and runs search algorithms (like DFS, BFS, Greedy, Dijkstra, A*) to find paths between points.
The graph is built from ways and nodes:

Ways = roads (e.g., "Cleveland Avenue")

Nodes = points along those roads (lat/lon coordinates)

Supports handling oneway streets, intersections, and exporting results to GPX so they can be visualized in JOSM or other map editors.

⚡ Features

Parse .osm XML files into a Python graph.

Build adjacency lists from <way> and <nd> references.

Support for oneway=yes / no / -1 and defaults.

Run BFS (and extendable to A*, Dijkstra, etc.) for pathfinding.

Export results as GPX tracks for visualization in JOSM.
