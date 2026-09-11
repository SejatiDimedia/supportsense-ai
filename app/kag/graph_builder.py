import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import networkx as nx

logger = logging.getLogger(__name__)

class SupportKnowledgeGraph:
    """
    In-memory Knowledge Graph powered by NetworkX MultiDiGraph.
    Represents relational customer support entities:
    Customer, Order, Product, Issue, Agent.
    """
    def __init__(self, seed_path: Optional[Path] = None):
        self.seed_path = seed_path or Path("data/graph_seed.json")
        self.graph = nx.MultiDiGraph()
        self._load_seed_data()

    def _load_seed_data(self):
        if not self.seed_path.exists():
            logger.warning(f"Graph seed file not found at {self.seed_path}. Initializing empty graph.")
            return

        with open(self.seed_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Add nodes
        for node in data.get("nodes", []):
            node_id = node["id"]
            label = node.get("label", "Unknown")
            properties = node.get("properties", {})
            self.graph.add_node(node_id, label=label, **properties)

        # Add edges
        for edge in data.get("edges", []):
            src = edge["source"]
            tgt = edge["target"]
            rel = edge.get("relation", "RELATED_TO")
            props = edge.get("properties", {})
            self.graph.add_edge(src, tgt, key=rel, relation=rel, **props)

        logger.info(f"Knowledge Graph initialized: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if node_id in self.graph.nodes:
            return {"id": node_id, **self.graph.nodes[node_id]}
        return None

    def find_order(self, order_num: str) -> Optional[Dict[str, Any]]:
        """
        Find an Order node by order_number (e.g. '#4521' or '4521').
        """
        clean_target = order_num.strip().lstrip("#")
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("label") == "Order":
                order_val = str(attrs.get("order_number", "")).strip().lstrip("#")
                if order_val == clean_target:
                    return {"id": node_id, **attrs}
        return None

    def find_customer(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Find a Customer node by email, name, or ID.
        """
        clean_ident = identifier.strip().lower()
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("label") == "Customer":
                name = str(attrs.get("name", "")).strip().lower()
                email = str(attrs.get("email", "")).strip().lower()
                if clean_ident in (name, email, node_id.lower()):
                    return {"id": node_id, **attrs}
        return None

    def get_neighbors(self, node_id: str, relation: Optional[str] = None, direction: str = "out") -> List[Dict[str, Any]]:
        """
        Retrieves neighbor nodes filtered by relation and direction ('out', 'in', or 'both').
        """
        neighbors = []
        if node_id not in self.graph:
            return []

        if direction in ("out", "both"):
            for _, tgt, key, edge_data in self.graph.out_edges(node_id, keys=True, data=True):
                if relation is None or edge_data.get("relation") == relation:
                    node_attrs = self.graph.nodes.get(tgt, {})
                    neighbors.append({
                        "node_id": tgt,
                        "relation": edge_data.get("relation"),
                        "direction": "out",
                        "edge_data": edge_data,
                        "node_data": node_attrs
                    })

        if direction in ("in", "both"):
            for src, _, key, edge_data in self.graph.in_edges(node_id, keys=True, data=True):
                if relation is None or edge_data.get("relation") == relation:
                    node_attrs = self.graph.nodes.get(src, {})
                    neighbors.append({
                        "node_id": src,
                        "relation": edge_data.get("relation"),
                        "direction": "in",
                        "edge_data": edge_data,
                        "node_data": node_attrs
                    })

        return neighbors

    def summary(self) -> Dict[str, Any]:
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "labels": list(set(nx.get_node_attributes(self.graph, "label").values()))
        }
