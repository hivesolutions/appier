import math

import appier

class Graph(object):

    def __init__(self):
        self.edges = dict()

    @classmethod
    def _build_path(cls, prev, src, dst):
        """
        Builds the shortest path given dictionary
        of previous nodes.
        """

        cur, path = dst, []
        while cur != src:
            path.append(cur)
            cur = prev[cur]
        path.append(src)
        path.reverse()
        return path

    def add_edges(self, edges):
        for edge in edges:
            if len(edge) < 2: continue
            src, dst = edge[0], edge[1]
            cost = edge[2] if len(edge) > 2 else 1
            bidirectional = edge[3] if len(edge) > 3 else False
            self.add_edge(src, dst, cost = cost, bidirectional = bidirectional)

    def add_edge(self, src, dst, cost = 1, bidirectional = False):
        if src not in self.edges: self.edges[src] = []
        self.edges[src].append((dst, cost))

        if bidirectional: self.add_edge(dst, src, cost = cost, bidirectional = False)

    def dijkstra(self, src, dst):
        """
        Dijkstra's algorithm with priority queue implementation.
        Costs default to a unit.
        Edges are unidirectional by default.
        """

        if src == dst: return [src], 0

        dist, prev = dict(), dict()
        dist[src] = 0

        queue = appier.MemoryQueue()
        queue.push(src, priority = 0)

        while queue.length() > 0:
            (_, _, top) = queue.pop(full = True)
            dist[top] = math.inf if top not in dist else dist[top]

            edges = self.edges[top] if top in self.edges else []
            for (nxt, cost) in edges:
                dist[nxt] = math.inf if nxt not in dist else dist[nxt]

                alt = dist[top] + cost
                if alt < dist[nxt]:
                    dist[nxt] = alt
                    prev[nxt] = top
                    queue.push(nxt, priority = dist[nxt])

        return self._build_path(prev, src, dst), dist[dst]
