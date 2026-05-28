# ============================================================
#  bidirectional_search.py  —  AI Concept: Bi-Directional Search
#  Finds shortest therapy path between two emotional states
#  by running BFS simultaneously from BOTH ends.
# ============================================================

from collections import deque
from knowledge_base import EMOTIONAL_STATES, THERAPY_ACTIONS, GOAL_STATE


def _reverse_graph(graph):
    rev = {n: [] for n in graph}
    for node, neighbors in graph.items():
        for nb in neighbors:
            rev.setdefault(nb, []).append(node)
    return rev


def bidirectional_search(start, goal=GOAL_STATE):
    if start == goal:
        return {"path": [start], "actions": [], "nodes_explored": 0, "found": True}

    fwd_graph = EMOTIONAL_STATES
    bwd_graph = _reverse_graph(EMOTIONAL_STATES)

    fwd_visited = {start: None}
    bwd_visited = {goal:  None}
    fwd_queue   = deque([start])
    bwd_queue   = deque([goal])
    nodes_explored = 0
    meeting = None

    while fwd_queue or bwd_queue:
        if fwd_queue:
            node = fwd_queue.popleft()
            nodes_explored += 1
            for nb in fwd_graph.get(node, []):
                if nb not in fwd_visited:
                    fwd_visited[nb] = node
                    fwd_queue.append(nb)
                if nb in bwd_visited:
                    meeting = nb
                    break
            if node in bwd_visited:
                meeting = node
                break

        if bwd_queue and not meeting:
            node = bwd_queue.popleft()
            nodes_explored += 1
            for nb in bwd_graph.get(node, []):
                if nb not in bwd_visited:
                    bwd_visited[nb] = node
                    bwd_queue.append(nb)
                if nb in fwd_visited:
                    meeting = nb
                    break
            if node in fwd_visited:
                meeting = node
                break

        if meeting:
            break

    if not meeting:
        return {"path": [], "actions": [], "nodes_explored": nodes_explored, "found": False}

    # Reconstruct path
    fwd_half = []
    cur = meeting
    while cur is not None:
        fwd_half.append(cur)
        cur = fwd_visited[cur]
    fwd_half.reverse()

    bwd_half = []
    cur = bwd_visited.get(meeting)
    while cur is not None:
        bwd_half.append(cur)
        cur = bwd_visited[cur]

    path    = fwd_half + bwd_half
    actions = [THERAPY_ACTIONS.get((path[i], path[i+1]), "supportive conversation")
               for i in range(len(path)-1)]

    return {"path": path, "actions": actions, "nodes_explored": nodes_explored, "found": True}


def get_next_therapy_step(current, goal=GOAL_STATE):
    result = bidirectional_search(current, goal)
    if not result["found"] or len(result["path"]) < 2:
        return {"next_state": current, "action": "supportive presence", "full_path": [current]}
    return {"next_state": result["path"][1], "action": result["actions"][0], "full_path": result["path"]}
