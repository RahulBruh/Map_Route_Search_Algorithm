// Pathfinding Visualizer: BFS, DFS, Dijkstra, A*
// Grid-based demo accompanying the OSM A*/Dijkstra route-search project.

const ROWS = 20;
const COLS = 36;

let grid = [];
let start = { row: 10, col: 6 };
let end = { row: 10, col: 29 };
let isMouseDown = false;
let draggingStart = false;
let draggingEnd = false;
let isRunning = false;

const gridEl = document.getElementById("grid");
const statusEl = document.getElementById("status");
const algoSelect = document.getElementById("algo");
const speedSelect = document.getElementById("speed");

function buildGrid() {
  grid = [];
  gridEl.style.gridTemplateColumns = `repeat(${COLS}, 24px)`;
  gridEl.innerHTML = "";
  for (let r = 0; r < ROWS; r++) {
    const row = [];
    for (let c = 0; c < COLS; c++) {
      const cellEl = document.createElement("div");
      cellEl.className = "cell";
      cellEl.dataset.row = r;
      cellEl.dataset.col = c;
      gridEl.appendChild(cellEl);
      row.push({ row: r, col: c, isWall: false, el: cellEl });
    }
    grid.push(row);
  }
  render();
  attachMouseHandlers();
}

function render() {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const cell = grid[r][c];
      const classes = ["cell"];
      if (cell.isWall) classes.push("wall");
      if (r === start.row && c === start.col) classes.push("start");
      if (r === end.row && c === end.col) classes.push("end");
      cell.el.className = classes.join(" ");
    }
  }
}

function attachMouseHandlers() {
  gridEl.addEventListener("mousedown", (e) => {
    if (isRunning) return;
    const target = e.target.closest(".cell");
    if (!target) return;
    const r = +target.dataset.row;
    const c = +target.dataset.col;
    isMouseDown = true;

    if (r === start.row && c === start.col) {
      draggingStart = true;
    } else if (r === end.row && c === end.col) {
      draggingEnd = true;
    } else {
      toggleWall(r, c);
    }
  });

  gridEl.addEventListener("mouseover", (e) => {
    if (!isMouseDown || isRunning) return;
    const target = e.target.closest(".cell");
    if (!target) return;
    const r = +target.dataset.row;
    const c = +target.dataset.col;

    if (draggingStart) {
      if (!(r === end.row && c === end.col)) {
        start = { row: r, col: c };
        render();
      }
    } else if (draggingEnd) {
      if (!(r === start.row && c === start.col)) {
        end = { row: r, col: c };
        render();
      }
    } else {
      toggleWall(r, c, true);
    }
  });

  document.addEventListener("mouseup", () => {
    isMouseDown = false;
    draggingStart = false;
    draggingEnd = false;
  });
}

function toggleWall(r, c, forceOn) {
  if ((r === start.row && c === start.col) || (r === end.row && c === end.col)) return;
  const cell = grid[r][c];
  cell.isWall = forceOn ? true : !cell.isWall;
  render();
}

function neighbors(r, c) {
  const deltas = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  const result = [];
  for (const [dr, dc] of deltas) {
    const nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && !grid[nr][nc].isWall) {
      result.push([nr, nc]);
    }
  }
  return result;
}

function heuristic(r, c) {
  return Math.abs(r - end.row) + Math.abs(c - end.col);
}

function key(r, c) { return `${r},${c}`; }

// Each algorithm returns { visitedOrder: [[r,c], ...], path: [[r,c], ...] }

function bfs() {
  const visitedOrder = [];
  const seen = new Set([key(start.row, start.col)]);
  const parent = new Map();
  const queue = [[start.row, start.col]];
  let found = false;

  while (queue.length) {
    const [r, c] = queue.shift();
    visitedOrder.push([r, c]);
    if (r === end.row && c === end.col) { found = true; break; }
    for (const [nr, nc] of neighbors(r, c)) {
      const k = key(nr, nc);
      if (!seen.has(k)) {
        seen.add(k);
        parent.set(k, [r, c]);
        queue.push([nr, nc]);
      }
    }
  }
  return { visitedOrder, path: found ? reconstructPath(parent) : [] };
}

function dfs() {
  const visitedOrder = [];
  const seen = new Set();
  const parent = new Map();
  const stack = [[start.row, start.col]];
  let found = false;

  while (stack.length) {
    const [r, c] = stack.pop();
    const k = key(r, c);
    if (seen.has(k)) continue;
    seen.add(k);
    visitedOrder.push([r, c]);
    if (r === end.row && c === end.col) { found = true; break; }
    for (const [nr, nc] of neighbors(r, c)) {
      const nk = key(nr, nc);
      if (!seen.has(nk)) {
        if (!parent.has(nk)) parent.set(nk, [r, c]);
        stack.push([nr, nc]);
      }
    }
  }
  return { visitedOrder, path: found ? reconstructPath(parent) : [] };
}

function dijkstra() {
  return weightedSearch(() => 0);
}

function astar() {
  return weightedSearch((r, c) => heuristic(r, c));
}

// Generic priority-queue search; dist + h decides order. h=0 gives Dijkstra.
function weightedSearch(h) {
  const visitedOrder = [];
  const dist = new Map([[key(start.row, start.col), 0]]);
  const parent = new Map();
  const seen = new Set();
  // simple binary-heap-free priority queue (array + sort) — grid is small enough
  const open = [[0 + h(start.row, start.col), start.row, start.col]];
  let found = false;

  while (open.length) {
    open.sort((a, b) => a[0] - b[0]);
    const [, r, c] = open.shift();
    const k = key(r, c);
    if (seen.has(k)) continue;
    seen.add(k);
    visitedOrder.push([r, c]);
    if (r === end.row && c === end.col) { found = true; break; }

    for (const [nr, nc] of neighbors(r, c)) {
      const nk = key(nr, nc);
      const newDist = dist.get(k) + 1;
      if (!dist.has(nk) || newDist < dist.get(nk)) {
        dist.set(nk, newDist);
        parent.set(nk, [r, c]);
        open.push([newDist + h(nr, nc), nr, nc]);
      }
    }
  }
  return { visitedOrder, path: found ? reconstructPath(parent) : [] };
}

function reconstructPath(parent) {
  const path = [];
  let cur = [end.row, end.col];
  const startKey = key(start.row, start.col);
  while (key(cur[0], cur[1]) !== startKey) {
    path.push(cur);
    cur = parent.get(key(cur[0], cur[1]));
    if (!cur) break;
  }
  path.push([start.row, start.col]);
  path.reverse();
  return path;
}

const ALGORITHMS = { bfs, dfs, dijkstra, astar };
const ALGO_NAMES = {
  bfs: "Breadth-First Search",
  dfs: "Depth-First Search",
  dijkstra: "Dijkstra",
  astar: "A* Search",
};

async function visualize() {
  if (isRunning) return;
  isRunning = true;
  clearPathVisuals();

  const algoKey = algoSelect.value;
  const delay = +speedSelect.value;
  statusEl.textContent = `Running ${ALGO_NAMES[algoKey]}...`;

  const { visitedOrder, path } = ALGORITHMS[algoKey]();

  for (const [r, c] of visitedOrder) {
    if (r === start.row && c === start.col) continue;
    if (r === end.row && c === end.col) continue;
    grid[r][c].el.classList.add("visited");
    await sleep(delay);
  }

  if (path.length) {
    for (const [r, c] of path) {
      if (r === start.row && c === start.col) continue;
      if (r === end.row && c === end.col) continue;
      grid[r][c].el.classList.add("path");
      await sleep(delay);
    }
    statusEl.textContent = `${ALGO_NAMES[algoKey]} found a path of length ${path.length - 1} after visiting ${visitedOrder.length} cells.`;
  } else {
    statusEl.textContent = `${ALGO_NAMES[algoKey]} explored ${visitedOrder.length} cells — no path exists.`;
  }

  isRunning = false;
}

function sleep(ms) { return new Promise((res) => setTimeout(res, ms)); }

function clearPathVisuals() {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      grid[r][c].el.classList.remove("visited", "visiting", "path");
    }
  }
  statusEl.textContent = "Drag the start/end nodes, click to draw walls, then press Visualize.";
}

function clearWalls() {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      grid[r][c].isWall = false;
    }
  }
  render();
  clearPathVisuals();
}

function randomMaze() {
  clearPathVisuals();
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const isStartOrEnd = (r === start.row && c === start.col) || (r === end.row && c === end.col);
      grid[r][c].isWall = !isStartOrEnd && Math.random() < 0.28;
    }
  }
  render();
}

document.getElementById("visualize-btn").addEventListener("click", visualize);
document.getElementById("clear-walls-btn").addEventListener("click", clearWalls);
document.getElementById("clear-path-btn").addEventListener("click", clearPathVisuals);
document.getElementById("maze-btn").addEventListener("click", randomMaze);

buildGrid();
