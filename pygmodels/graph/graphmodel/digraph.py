"""!
\file digraph.py

# Directed Graph

This is basically a Graph with directed edges. This has implications on several
algorithms. Most notably connected components algorithm does not work the same
way. The minimum spanning tree also does not work. We need to differentiate the
positioning of nodes in edges as well. Sometimes it is also represented as \f[
G = (V, A) \f] where A is arcs.

Whenever possible we simply change the edge generation strategy in order to use
the parent's algorithm.

"""
from typing import Callable, Set
from uuid import uuid4

from pygmodels.graph.graphfunc.graphanalyzer import BaseGraphAnalyzer
from pygmodels.graph.graphmodel.graph import Graph
from pygmodels.graph.graphmodel.undigraph import UndiGraph
from pygmodels.graph.graphfunc.digraphops import DiGraphBoolOps
from pygmodels.graph.graphfunc.graphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphOps,
)
from pygmodels.graph.graphfunc.graphsearcher import BaseGraphSearcher
from pygmodels.graph.graphtype.abstractobj import AbstractDiGraph, EdgeType
from pygmodels.graph.graphtype.basegraph import BaseGraph
from pygmodels.graph.graphtype.edge import Edge
from pygmodels.graph.graphtype.node import Node


class DiGraph(AbstractDiGraph, BaseGraph):
    """!
    \brief Directed graph implementation
    """

    def __init__(
        self,
        gid: str,
        data={},
        nodes: Set[Node] = None,
        edges: Set[Edge] = None,
    ):
        """!
        \brief Constructor for DiGraph

        More or less what we have in Graph.
        We just make sure every edge is a directed edge.
        \sa Graph for parameters.

        \throws ValueError if there is any undirected edge among the argument
        edge set.
        """
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        if edges is not None:
            if not self.check_edge_type(etype=EdgeType.DIRECTED):
                raise ValueError(
                    "Can not instantiate directed graph with" + " undirected edges"
                )
        self.path_props = {v.id: self.find_shortest_paths(v) for v in self.V}
        self.dprops = BaseGraphSearcher.depth_first_search(
            self,
            edge_generator=lambda x: BaseGraphEdgeOps.outgoing_edges_of(self, x),
            check_cycle=True,
        )

    @classmethod
    def from_graph(cls, g: Graph):
        """!
        \brief make DiGraph from Graph

        \param g argument graph

        We give a random id for the resulting DiGraph.
        """
        return DiGraph(
            gid=str(uuid4()),
            data=g.data(),
            nodes=g.V,
            edges=g.E,
        )

    def to_undirected(self) -> UndiGraph:
        """!
        to undirected graph
        """
        nodes = self.V
        edges = self.E
        nedges = set()
        nnodes = set([n for n in nodes])
        for e in edges:
            e.set_type(etype=EdgeType.UNDIRECTED)
            nedges.add(e)
        return UndiGraph(gid=str(uuid4()), data=self.data(), nodes=nnodes, edges=nedges)

    def find_shortest_paths(self, n: Node):
        """!
        \todo directed graphs don't yield shortest path with bfs but with
        optimal branching.
        """
        return BaseGraphSearcher.breadth_first_search(
            self,
            n1=n,
            edge_generator=lambda x: BaseGraphEdgeOps.outgoing_edges_of(self, x),
        )

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        path_props = self.path_props[n1.id]
        pset = path_props.path_set
        return n2 in pset

    def __find_transitive_closure(self) -> Graph:
        """!
        From algorithmic graph theory Joyner, Phillips, Nguyen, 2013, p.134
        """
        T = BaseGraphAnalyzer.transitive_closure_matrix(self)
        nodes = set()
        edges = set()
        for tpl, tval in T.items():
            if tval is False:
                n1 = self.V[tpl[0]]
                n2 = self.V[tpl[1]]
                nodes.add(n1)
                nodes.add(n2)
                e = Edge(
                    edge_id=str(uuid4()),
                    start_node=n1,
                    end_node=n2,
                    edge_type=EdgeType.DIRECTED,
                )
                edges.add(e)

        return DiGraph(gid=str(uuid4()), nodes=nodes, edges=edges)

    def find_transitive_closure(self) -> Graph:
        """!
        From algorithmic graph theory Joyner, Phillips, Nguyen, 2013, p.134
        """
        raise NotImplementedError("algorithm not yet implemented")
