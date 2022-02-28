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

import unittest

import appier

class GraphTest(unittest.TestCase):

    def test__build_path(self):
        prev = dict(
            B = "A",
            C = "A",
            D = "B",
            E = "D",
            F = "D",
            G = "E"
        )

        path = appier.Graph._build_path(prev, "A", "F")
        self.assertEqual(path, ["A", "B", "D", "F"])

    def test_create(self):
        graph = appier.Graph()
        self.assertEqual(len(graph.edges), 0)

    def test_create_with_argument(self):
        graph = appier.Graph([
            ("A", "B"),
            ("B", "D", 20, True)
        ])
        self.assertEqual(len(graph.edges), 3)

    def test_add_edges(self):
        graph = appier.Graph()
        edges = [
            ("A", "B"),
            ("B", "D", 20),
            ("B", "C", 10, True),
            ("D", "F"),
            ("F", "D")
        ]
        graph.add_edges(edges)

        self.assertEqual(graph.edges["A"], [("B", 1)])
        self.assertEqual(graph.edges["B"], [("D", 20), ("C", 10)])
        self.assertEqual(graph.edges["D"], [("F", 1)])
        self.assertEqual(graph.edges["F"], [("D", 1)])

    def test_add_edges_handle_invalid(self):
        graph = appier.Graph()
        edges = [
            ("A", "B", "invalid", "invalid"),
            ("B", "D", 20),
            ("B", "C", 10, True),
            ("D", "F"),
            ("F", "D"),
            (),
            ("A")
        ]
        graph.add_edges(edges)

        self.assertEqual(graph.edges["A"], [("B", 1)])
        self.assertEqual(graph.edges["B"], [("D", 20), ("C", 10)])
        self.assertEqual(graph.edges["D"], [("F", 1)])
        self.assertEqual(graph.edges["F"], [("D", 1)])

    def test_add_edge(self):
        graph = appier.Graph()

        graph.add_edge("A", "B")
        self.assertEqual(graph.edges["A"], [("B", 1)])

        graph.add_edge("B", "D", cost = 20)
        graph.add_edge("B", "C", cost = 10)
        self.assertEqual(graph.edges["B"], [("D", 20), ("C", 10)])

        graph.add_edge("D", "F", bidirectional = True)
        self.assertEqual(graph.edges["D"], [("F", 1)])
        self.assertEqual(graph.edges["F"], [("D", 1)])

    def test_disjktra_no_path(self):
        graph = appier.Graph([
            ("A", "B"),
            ("B", "C"),
            ("F", "G")
        ])

        path, cost = graph.dijkstra("C", "A")
        self.assertEqual(path, [])
        self.assertEqual(cost, appier.defines.INFINITY)

        path, cost = graph.dijkstra("C", "B")
        self.assertEqual(path, [])
        self.assertEqual(cost, appier.defines.INFINITY)

        path, cost = graph.dijkstra("A", "F")
        self.assertEqual(path, [])
        self.assertEqual(cost, appier.defines.INFINITY)

    def test_dijkstra_src_equal_dst(self):
        graph = appier.Graph()

        path, cost = graph.dijkstra("A", "A")
        self.assertEqual(path, ["A"])
        self.assertEqual(cost, 0)

    def test_dijkstra_simple(self):
        graph = appier.Graph([
            ("A", "B"),
            ("B", "C")
        ])

        path, cost = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "B", "C"])
        self.assertEqual(cost, 2)

    def test_dijkstra_costs(self):
        graph = appier.Graph([
            ("A", "B"),
            ("B", "C", 10),
            ("B", "D", 4),
            ("D", "C", 5)
        ])

        path, cost = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "B", "D", "C"])
        self.assertEqual(cost, 10)

    def test_dijkstra_loop(self):
        graph = appier.Graph([
            ("A", "B"),
            ("B", "B"),
            ("B", "C")
        ])

        path, cost = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "B", "C"])
        self.assertEqual(cost, 2)

    def test_dijkstra_big(self):
        graph = appier.Graph([
            ("A", "B", 2),
            ("A", "C", 6),
            ("B", "D", 5),
            ("C", "D", 8),
            ("D", "E", 10),
            ("D", "F", 15),
            ("E", "F", 6),
            ("E", "G", 2),
            ("F", "G", 6)
        ])

        path, cost = graph.dijkstra("A", "A")
        self.assertEqual(path, ["A"])
        self.assertEqual(cost, 0)

        path, cost = graph.dijkstra("A", "B")
        self.assertEqual(path, ["A", "B"])
        self.assertEqual(cost, 2)

        path, cost = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "C"])
        self.assertEqual(cost, 6)

        path, cost = graph.dijkstra("A", "D")
        self.assertEqual(path, ["A", "B", "D"])
        self.assertEqual(cost, 7)

        path, cost = graph.dijkstra("A", "E")
        self.assertEqual(path, ["A", "B", "D", "E"])
        self.assertEqual(cost, 17)

        path, cost = graph.dijkstra("A", "F")
        self.assertEqual(path, ["A", "B", "D", "F"])
        self.assertEqual(cost, 22)

        path, cost = graph.dijkstra("A", "G")
        self.assertEqual(path, ["A", "B", "D", "E", "G"])
        self.assertEqual(cost, 19)

        path, cost = graph.dijkstra("C", "G")
        self.assertEqual(path, ["C", "D", "E", "G"])
        self.assertEqual(cost, 20)

        path, cost = graph.dijkstra("C", "F")
        self.assertEqual(path, ["C", "D", "F"])
        self.assertEqual(cost, 23)
