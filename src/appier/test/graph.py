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

__copyright__ = "Copyright (c) 2008-2021 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import unittest

import appier

class GraphTest(unittest.TestCase):

    def test__build_path(self):
        prev = dict(
            A = "B",
            B = "C",
            C = "F",
            F = "G"
        )
        path = appier.Graph._build_path(prev, "A", "G")
        self.assertEqual(path, ["A", "B", "C", "F", "G"])

    def test_create(self):
        graph = appier.Graph()
        self.assertEqual(len(graph.edges), 0)

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

    def test_dijkstra_src_equal_dst(self):
        graph = appier.Graph()
        path = graph.dijkstra("A", "A")
        self.assertEqual(path, ["A"])

    def test_dijkstra_simple(self):
        edges = [
            ("A", "B"),
            ("B", "C")
        ]
        graph = appier.Graph()
        graph.add_edges(edges)
        path = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "B", "C"])

    def test_dijkstra_costs(self):
        edges = [
            ("A", "B"),
            ("B", "C", 10),
            ("B", "D", 4),
            ("D", "C", 9)
        ]
        graph = appier.Graph()
        graph.add_edges(edges)
        path = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "B", "D", "C"])

    def test_dijkstra_loop(self):
        edges = [
            ("A", "B"),
            ("B", "B"),
            ("B", "C")
        ]
        graph = appier.Graph()
        graph.add_edges(edges)
        path = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "B", "C"])

    def test_dijkstra_big(self):
        edges = [
            ("A", "B", 2),
            ("A", "C", 6),
            ("B", "D", 5),
            ("C", "D", 8),
            ("D", "E", 10),
            ("D", "F", 15),
            ("E", "F", 6),
            ("E", "G", 2),
            ("F", "G", 6)
        ]
        graph = appier.Graph()
        graph.add_edges(edges)

        path = graph.dijkstra("A", "A")
        self.assertEqual(path, ["A"])

        path = graph.dijkstra("A", "B")
        self.assertEqual(path, ["A", "B"])

        path = graph.dijkstra("A", "C")
        self.assertEqual(path, ["A", "C"])

        path = graph.dijkstra("A", "D")
        self.assertEqual(path, ["A", "B", "D"])

        path = graph.dijkstra("A", "E")
        self.assertEqual(path, ["A", "B", "D", "E"])

        path = graph.dijkstra("A", "F")
        self.assertEqual(path, ["A", "B", "D", "F"])

        path = graph.dijkstra("A", "G")
        self.assertEqual(path, ["A", "B", "D", "E", "G"])

        path = graph.dijkstra("C", "G")
        self.assertEqual(path, ["C", "D", "E", "G"])

        path = graph.dijkstra("C", "F")
        self.assertEqual(path, ["C", "D", "F"])
