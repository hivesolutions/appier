#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2022 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2022 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import defines
from . import queuing

class Graph(object):
    """
    Graph structure and associated algorithms. Made up by a dictionary of
    sources to destinations and costs (weighted edges).
    Edges are unidirectional by default.
    Costs default to a unit.
    """

    def __init__(self, *args):
        self.edges = dict()
        if len(args) > 0 and isinstance(args[0], list):
            self.add_edges(args[0])

    @classmethod
    def _build_path(cls, prev, src, dst):
        """
        Builds the shortest path given dictionary
        of previous nodes.
        """

        cur, path = dst, []
        while not cur == src:
            path.append(cur)
            if not cur in prev: return []
            cur = prev[cur]
        path.append(src)
        path.reverse()
        return path

    def add_edges(self, edges):
        for edge in edges:
            if len(edge) < 2: continue
            src, dst = edge[0], edge[1]
            cost = edge[2] if len(edge) > 2 and isinstance(edge[2], int) else 1
            bidirectional = edge[3] if len(edge) > 3 and isinstance(edge[3], bool) else False
            self.add_edge(src, dst, cost = cost, bidirectional = bidirectional)

    def add_edge(self, src, dst, cost = 1, bidirectional = False):
        if not src in self.edges: self.edges[src] = []
        self.edges[src].append((dst, cost))

        if bidirectional: self.add_edge(dst, src, cost = cost, bidirectional = False)

    def dijkstra(self, src, dst):
        """
        Dijkstra's algorithm with priority queue implementation
        useing the appier's memory queue.

        :type src: Object
        :param src: The initial node from which a node path to
        the destination should be found.
        :type dst: Object
        :param dst: The destination node to find the path to.
        :see: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
        """

        if src == dst: return [src], 0

        cls = self.__class__
        dist, prev = dict(), dict()
        dist[src] = 0

        queue = queuing.MemoryQueue()
        queue.push(src, priority = 0)

        while queue.length() > 0:
            (_, _, top) = queue.pop(full = True)
            dist[top] = dist[top] if top in dist else defines.INFINITY

            edges = self.edges[top] if top in self.edges else []
            for (nxt, cost) in edges:
                dist[nxt] = dist[nxt] if nxt in dist else defines.INFINITY

                alt = dist[top] + cost
                if alt < dist[nxt]:
                    dist[nxt] = alt
                    prev[nxt] = top
                    queue.push(nxt, priority = dist[nxt])

        path = cls._build_path(prev, src, dst)
        cost = dist[dst] if dst in dist else defines.INFINITY
        return path, cost
