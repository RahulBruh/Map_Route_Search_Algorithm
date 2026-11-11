"""Unit tests for the route-search algorithms on a small synthetic graph."""
import random
from collections import defaultdict

import pytest

from connect import ALGORITHMS, Graph, a_star, bfs, dfs, dijkstra, route_stats


def make_graph(edges, coords, mph=None, oneway=()):
    roads = defaultdict(list)
    for a, b in edges:
        roads[a].append(b)
        if (a, b) not in oneway:
            roads[b].append(a)
    return Graph(roads, coords, mph or {n: 25 for n in coords})


@pytest.fixture
def diamond():
    # 1 -> 2 -> 4 is shorter in hops-equal but slow; 1 -> 3 -> 4 is a fast highway.
    coords = {1: (36.16, -86.78), 2: (36.165, -86.775), 3: (36.155, -86.775), 4: (36.16, -86.77)}
    mph = {1: 65, 2: 10, 3: 65, 4: 65}
    return make_graph([(1, 2), (2, 4), (1, 3), (3, 4)], coords, mph)


@pytest.mark.parametrize("algo", ALGORITHMS.values())
def test_finds_route(diamond, algo):
    path, _ = algo(diamond, 1, 4)
    assert path[0] == 1 and path[-1] == 4


def test_weighted_algorithms_prefer_fast_road(diamond):
    assert dijkstra(diamond, 1, 4)[0] == [1, 3, 4]
    assert a_star(diamond, 1, 4)[0] == [1, 3, 4]


@pytest.mark.parametrize("algo", ALGORITHMS.values())
def test_unreachable(algo):
    g = make_graph([(1, 2)], {1: (0, 0), 2: (0, 0.01), 3: (1, 1)})
    assert algo(g, 1, 3)[0] == []


def test_oneway_respected():
    coords = {1: (0, 0), 2: (0, 0.01)}
    g = make_graph([(1, 2)], coords, oneway={(1, 2)})
    assert bfs(g, 1, 2)[0] == [1, 2]
    assert bfs(g, 2, 1)[0] == []


def test_haversine_known_distance():
    # Nashville -> Memphis is roughly 197 miles great-circle.
    g = Graph(coordinates={1: (36.1627, -86.7816), 2: (35.1495, -90.0490)})
    assert g.distance(1, 2) == pytest.approx(197, abs=3)


def test_astar_matches_dijkstra_on_random_grids():
    rng = random.Random(7)
    for _ in range(50):
        n = 12
        coords = {r * n + c: (36 + r * 0.001, -86 + c * 0.001) for r in range(n) for c in range(n)}
        edges = []
        for r in range(n):
            for c in range(n):
                if c + 1 < n and rng.random() > 0.25:
                    edges.append((r * n + c, r * n + c + 1))
                if r + 1 < n and rng.random() > 0.25:
                    edges.append((r * n + c, (r + 1) * n + c))
        mph = {k: rng.choice([10, 25, 45, 65]) for k in coords}
        g = make_graph(edges, coords, mph)
        d_path, d_exp = dijkstra(g, 0, n * n - 1)
        a_path, a_exp = a_star(g, 0, n * n - 1)
        assert bool(d_path) == bool(a_path) == bool(dfs(g, 0, n * n - 1)[0])
        if d_path:
            assert route_stats(g, a_path)[1] == pytest.approx(route_stats(g, d_path)[1])
            assert a_exp <= d_exp
