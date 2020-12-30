"""
Undirected graph object
"""
from typing import Set, Optional, Callable, List, Tuple, Dict
from edge import Edge
from node import Node
from info import NodeInfo, SNodeInfo
from path import Path, Cycle
from abstractobj import EdgeType
from graph import Graph
from uuid import uuid4
import math


class UndirectedGraph(Graph):
    """!
    Unidrected graph whose edges are of type Undirected
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        ""
        if edges is not None:
            for edge in edges:
                if edge.type() == EdgeType.DIRECTED:
                    raise ValueError(
                        "Can not instantiate undirected graph with" + " directed edges"
                    )
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)

    def is_node_incident(self, n: Node, e: Edge) -> bool:
        ""
        return e.is_endvertice(n)

    def is_neighbour_of(self, n1: Node, n2: Node) -> bool:
        ""
        n1_edge_ids = set(self.gdata[n1.id()])
        n2_edge_ids = set(self.gdata[n2.id()])
        return len(n1_edge_ids.intersection(n2_edge_ids)) > 0

    def is_adjacent_of(self, e1: Edge, e2: Edge) -> bool:
        ""
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    def is_node_independant_of(self, n1: Node, n2: Node) -> bool:
        return not self.is_neighbour_of(n1, n2)

    def is_stable(self, ns: Set[Node]) -> bool:
        ""
        if not self.contains_vertices(ns):
            raise ValueError("node set is not contained in graph")
        node_list = list(ns)
        while node_list:
            n1 = node_list.pop()
            for n2 in node_list:
                if self.is_neighbour_of(n1=n1, n2=n2):
                    return False
        return True

    def neighbours_of(self, n1: Node) -> Set[Node]:
        ""
        if not self.is_in(n1):
            raise ValueError("node is not in graph")
        neighbours = set()
        for n2 in self.nodes():
            if self.is_neighbour_of(n1=n1, n2=n2):
                neighbours.add(n2)
        return neighbours

    def edges_of(self, n: Node) -> Set[Edge]:
        ""
        edge_ids = self.gdata[n.id()]
        return set([self.E[eid] for eid in edge_ids])

    def traverse_search_nodes(self, snode: dict, nlist: List[Node], elist: List[Node]):
        ""
        if snode["parent"] is None:
            nlist.append(snode["state"])
            return
        #
        nlist.append(snode["state"])
        elist.append(self.edge_by_id(snode["edge-id"]))
        self.traverse_search_nodes(snode["parent"], nlist, elist)

    def extract_path_from_search_node(self, search_node: dict) -> Path:
        ""
        nodelist: List[Node] = []
        edgelist: List[Edge] = []
        self.traverse_search_nodes(search_node, nlist=nodelist, elist=edgelist)
        if not edgelist:
            edgelist = None
        return Path(gid=str(uuid4()), nodes=nodelist, edges=edgelist)

    def find_shortest_path(self, n1: Node, n2: Node) -> Path:
        """
        find path between two nodes using uniform cost search
        """
        if not self.is_in(n1):
            raise ValueError("first node is not inside this graph")
        if not self.is_in(n2):
            raise ValueError("second node is not inside this graph")
        if n1 == n2:
            nset = [n1]
            return Path(gid=str(uuid4()), nodes=nset, edges=None)
        search_node = {"state": n1, "cost": 0, "parent": None, "edge-id": None}
        explored = set()
        frontier = [search_node]
        while frontier:
            explored_search_node = frontier.pop()
            explored_state = explored_search_node["state"]
            explored_id = explored_state.id()
            if explored_id == n2.id():
                return self.extract_path_from_search_node(explored_search_node)
            #
            explored.add(explored_id)
            path_cost = explored_search_node["cost"]
            for neighbour in self.neighbours_of(explored_state):
                parent_edge = self.edge_by_vertices(explored_state, neighbour)
                ncost = path_cost + 1
                child_search_node = {
                    "state": neighbour,
                    "cost": ncost,
                    "parent": explored_search_node,
                    "edge-id": parent_edge,
                }
                child_id = child_search_node["state"].id()
                if (child_id not in explored) and (
                    all(
                        [
                            front_node["state"].id() != child_id
                            for front_node in frontier
                        ]
                    )
                ):
                    #
                    frontier.append(child_search_node)
                    frontier.sort(key=lambda x: x["cost"])
                elif any(
                    [child_id == front_node["state"].id() for front_node in frontier]
                ):
                    frontcp = frontier.copy()
                    for i, snode in enumerate(frontcp):
                        snode_id = snode["state"].id()
                        if snode_id == child_id:
                            if snode["cost"] > child_search_node["cost"]:
                                frontier[i] = child_search_node
        #
        return

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        return self.find_shortest_path(n1, n2) is not None

    def shortest_path_length(self) -> int:
        "see proof Diestel p. 8"
        return self.min_degree()

    def find_shortest_path_per_node(self, n: Node) -> Path:
        "find shortest path for node n"
        nodes = self.nodes()
        result = None
        result_len = math.inf
        for node in nodes:
            if n.id() != node.id():
                path = self.find_shortest_path(n1=n, n2=node)
                if path is not None:
                    plen = path.length()
                    if plen < result_len:
                        result = path
                        result_len = plen
        return result

    def find_connected_components(self):
        """!
        Find connected components as per Roughgarden 2018, 8.8.3 UCC algorithm
        """
        # mark all vertices as unexplored
        vertices = {k: False for k in self.gdata.keys()}
        #
        numCC = 0
        components = {}
        for i, explored in vertices.items():
            if not explored:
                numCC += 1
                components[numCC] = set()
                frontier = [i]
                while frontier:
                    v = frontier.pop(0)
                    cc_v = numCC
                    node_v = self.V[v]
                    for w in self.neighbours_of(node_v):
                        wid = w.id()
                        if not vertices[wid]:
                            vertices[wid] = True
                            components[cc_v].add(wid)
        return components

    def find_minimum_spanning_tree(self):
        """!
        Find minimum spanning tree as per Prim's algorithm
        Christopher Griffin, Graph Theory lecture notes, 2016, p.39 - 42
        """
        e_prim: Set[str] = set()
        v_prim: Set[str] = set([[v for v in self.V][0]])
        weights: Dict[str, int] = {e: 1 for e in self.E}
        V: Set[str] = set([v for v in self.V])
        while v_prim != V:
            X = V.difference(v_prim)
            e: Edge = None
            w_star = math.inf
            u_prime: str = None
            for v in v_prim:
                for u in X:
                    vnode = self.V[v]
                    unode = self.V[u]
                    edge = self.edge_by_vertices(vnode, unode)
                    w_edge = weights[edge.id()]
                    if w_edge < w_star:
                        w_star = w_edge
                        e = edge
                        u_prime = u
            e_prim.add(e.id())
            v_prim.add(u_prime)
        #
        V_prime = set([self.V[v] for v in v_prim])
        E_prime = set([self.E[e] for v in e_prim])
        return UndirectedGraph(gid=str(uuid4()), nodes=V_prime, edges=E_prime)

    def dfs_forest(
        self,
        u: str,
        pred: Dict[str, str],
        marked: Dict[str, int],
        d: Dict[str, int],
        f: Dict[str, int],
        time: int,
        check_cycle: bool = True,
    ):
        """!
        adapted for cycle detection
        dfs recursive forest from Erciyes 2018, Guide Graph ..., p.152 alg. 6.7
        """
        marked[u] = True
        time += 1
        d[u] = time
        unode = self.V[u]
        for vnode in self.neighbours_of(unode):
            v = vnode.id()
            if marked[v] is False:
                pred[v] = u
                self.dfs_forest(v, pred, marked, d, f, time)
        #
        time += 1
        f[u] = time
        if check_cycle:
            for vnode in self.neighbours_of(unode):
                if d[vnode.id()] < f[u]:
                    return (vnode.id(), u)
        return

    #
    def find_cycle(self) -> Cycle:
        "find if graph has a cycle exit at first found cycle"
        time = 0
        marked = {n: False for n in self.V}
        pred = {n: None for n in self.V}
        d: Dict[str, int] = {}
        f: Dict[str, int] = {}
        for u in self.V:
            if marked[u] is False:
                res = self.dfs_forest(
                    u=u, pred=pred, marked=marked, d=d, f=f, time=time
                )
                if res is not None:
                    start_end_cycle, before_last = res
                    nlist: List[Node] = []
                    elist: List[Edge] = []
                    temp = pred[before_last]
                    while temp != start_end_cycle:
                        tnode = self.V[temp]
                        nlist.append(temp)
                        temp = pred[temp]
                        tnode2 = self.V[temp]
                        edge = self.edge_by_vertices(tnode, tnode2)
                        elist.append(edge)
                    return Cycle(gid=str(uuid4()), nodes=nlist, edges=elist)

    def has_cycle(self) -> bool:
        "check if graph has a cycle"
        cycle = self.find_cycle()
        return cycle is not None
