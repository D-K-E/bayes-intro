"""!
\file test_graphops.py Graph Analyzer Test for BaseGraph subclasses 
"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from pygmodels.gtype.abstractobj import AbstractGraph
from pygmodels.gtype.abstractobj import AbstractNode, AbstractEdge
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.node import Node
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.graphf.bgraphops import BaseGraphOps

from pygmodels.graphf.graphops import BaseGraphAlgOps, BaseGraphSetOps

import unittest
import pprint
import math


class BaseGraphAlgSetOps(unittest.TestCase):
    ""

    def setUp(self):
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        nset = set([self.n1, self.n2, self.n3, self.n4, self.n5])
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.UNDIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e4 = Edge(
            "e4", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )

        self.graph = BaseGraph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2]),
        )
        self.graph_2 = BaseGraph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3]),
        )
        #
        self.a = Node("a", {})  # b
        self.b = Node("b", {})  # c
        self.f = Node("f", {})  # d
        self.e = Node("e", {})  # e
        self.ae = Edge(
            "ae", start_node=self.a, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ab = Edge(
            "ab", start_node=self.a, end_node=self.b, edge_type=EdgeType.UNDIRECTED
        )
        self.af = Edge(
            "af", start_node=self.a, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )
        self.be = Edge(
            "be", start_node=self.b, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ef = Edge(
            "ef", start_node=self.e, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )

        # undirected graph
        self.ugraph2 = BaseGraph(
            "ug2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set([self.ae, self.ab, self.af, self.be, self.ef,]),
        )
        # ugraph2 :
        #   +-----+
        #  /       \
        # a -- b -- e
        #  \       /
        #   +-----f

        self.ugraph3 = BaseGraph(
            "ug3",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ab,
                    # self.af,
                    self.be,
                ]
            ),
        )
        # ugraph3 :
        #
        #
        # a -- b -- e
        #  \
        #   +-----f

        self.ugraph4 = BaseGraph(
            "ug4",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=BaseGraphOps.nodes(self.ugraph2).union(
                BaseGraphOps.nodes(self.graph_2)
            ),
            edges=BaseGraphOps.edges(self.ugraph2).union(
                BaseGraphOps.edges(self.graph_2)
            ),
        )
        # ugraph 4
        #   +-----+     n1 -- n2 -- n3 -- n4
        #  /       \     \                /
        # a -- b -- e     +--------------+
        #  \       /
        #   +-----f

        # make some directed edges
        self.bb = Node("bb", {})
        self.cc = Node("cc", {})
        self.dd = Node("dd", {})
        self.ee = Node("ee", {})

        self.bb_cc = Edge(
            "bb_cc", start_node=self.bb, end_node=self.cc, edge_type=EdgeType.DIRECTED
        )
        self.cc_dd = Edge(
            "cc_dd", start_node=self.cc, end_node=self.dd, edge_type=EdgeType.DIRECTED
        )
        self.dd_ee = Edge(
            "dd_ee", start_node=self.dd, end_node=self.ee, edge_type=EdgeType.DIRECTED
        )
        self.ee_bb = Edge(
            "ee_bb", start_node=self.ee, end_node=self.bb, edge_type=EdgeType.DIRECTED
        )
        self.bb_dd = Edge(
            "bb_dd", start_node=self.bb, end_node=self.dd, edge_type=EdgeType.DIRECTED
        )

    def test_intersection_v(self):
        n = Node("n646", {})

        vset = BaseGraphSetOps.intersection(self.graph, set([self.n1, n]))
        self.assertEqual(vset, set([self.n1]))

    def test_intersection_e(self):
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        eset = BaseGraphSetOps.intersection(self.graph, set([self.e1, e]))
        self.assertEqual(eset, set([self.e1]))

    def test_union_v(self):
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        vset = BaseGraphSetOps.union(self.graph, set([n]))
        self.assertEqual(vset, set([self.n1, self.n2, self.n3, self.n4, n]))

    def test_union_e(self):
        n = Node("n646", {})
        e = Edge("e8", start_node=self.n1, end_node=n, edge_type=EdgeType.UNDIRECTED)
        eset = BaseGraphSetOps.union(self.graph, set([e]))
        self.assertEqual(eset, set([e, self.e1, self.e2]))

    def test_contains_n(self):
        ""
        nodes = set([self.n2, self.n3])
        contains = BaseGraphSetOps.contains(self.graph, nodes)
        self.assertTrue(contains)

    def test_contains_e(self):
        ""
        es = set([self.e1, self.e2])
        contains = BaseGraphSetOps.contains(self.graph, es)
        self.assertTrue(contains)

    def test_contains_g(self):
        ""
        es = set([self.e1])
        g = BaseGraph(
            gid="temp", data={}, nodes=set([self.n1, self.n2, self.n3]), edges=es
        )
        contains = BaseGraphSetOps.contains(g, es)
        self.assertTrue(contains)

    def test_subtract_n(self):
        ""
        gs = BaseGraphAlgOps.subtract(self.graph, self.n2)
        nodes = set(gs.V.values())
        self.assertEqual(nodes, set([self.n1, self.n3, self.n4]))

    def test_subtract_e(self):
        ""
        gs = BaseGraphAlgOps.subtract(self.graph, self.e2)
        self.assertEqual(set(gs.E.values()), set([self.e1]))

    def test_add_edge(self):
        ""
        g = BaseGraphAlgOps.add(self.graph, self.e3)
        #
        self.assertEqual(set(self.graph.V.values()), set(g.V.values()))
        self.assertEqual(set(self.graph_2.E.values()), set(g.E.values()))