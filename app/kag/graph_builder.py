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
        loaded = self._load_from_database()
        if not loaded:
            self._load_seed_data()

    def _load_from_database(self) -> bool:
        """
        Dynamically constructs the Knowledge Graph directly from PostgreSQL
        (with local SQLite fallback).
        """
        conn = None
        try:
            import psycopg2
            from app.config import settings
            pg_url = getattr(settings, "postgres_url", "postgresql://postgres:postgres@localhost:5433/supportsense")
            conn = psycopg2.connect(pg_url, connect_timeout=3)
            cursor = conn.cursor()
        except Exception:
            try:
                import sqlite3
                db_path = Path("data/relational_sample.db")
                if not db_path.exists():
                    return False
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
            except Exception:
                return False

        try:
            # 1. Add Customers
            cursor.execute("SELECT id, name, email, phone FROM customers;")
            for row in cursor.fetchall():
                c_id, name, email, phone = row[0], row[1], row[2], row[3]
                self.graph.add_node(c_id, label="Customer", name=name, email=email, phone=phone)

            # 2. Add Products
            cursor.execute("SELECT id, sku, name, category, price_idr FROM products;")
            for row in cursor.fetchall():
                p_id, sku, name, category, price = row[0], row[1], row[2], row[3], row[4]
                self.graph.add_node(p_id, label="Product", sku=sku, name=name, category=category, price=price)

            # 3. Add Agents
            cursor.execute("SELECT id, name, role, email FROM agents;")
            for row in cursor.fetchall():
                a_id, name, role, email = row[0], row[1], row[2], row[3]
                self.graph.add_node(a_id, label="Agent", name=name, role=role, email=email)

            # 4. Add Orders & (Customer -[PLACED]-> Order) edges
            cursor.execute("SELECT id, order_number, customer_id, status, tracking_number, carrier, created_at FROM orders;")
            for row in cursor.fetchall():
                o_id, order_num, cust_id, status, tracking, carrier, created_at = row[0], row[1], row[2], row[3], row[4], row[5], str(row[6])
                self.graph.add_node(
                    o_id,
                    label="Order",
                    order_number=order_num,
                    status=status,
                    tracking_number=tracking,
                    shipping_carrier=carrier,
                    order_date=created_at[:10] if created_at else None,
                    created_at=created_at
                )
                if cust_id and cust_id in self.graph:
                    self.graph.add_edge(cust_id, o_id, key="PLACED", relation="PLACED")

            # 5. Add (Order -[CONTAINS]-> Product) edges
            cursor.execute("SELECT id, order_id, product_id, quantity FROM order_items;")
            for row in cursor.fetchall():
                _, o_id, p_id, qty = row[0], row[1], row[2], row[3]
                if o_id in self.graph and p_id in self.graph:
                    self.graph.add_edge(o_id, p_id, key="CONTAINS", relation="CONTAINS", quantity=qty)

            # 6. Add Issues, (Order -[HAS_ISSUE]-> Issue), and (Issue -[ASSIGNED_TO]-> Agent)
            cursor.execute("SELECT id, order_id, issue_type, issue_status, assigned_agent_id, notes FROM issues;")
            for row in cursor.fetchall():
                iss_id, o_id, iss_type, iss_status, agt_id, notes = row[0], row[1], row[2], row[3], row[4], row[5]
                self.graph.add_node(
                    iss_id,
                    label="Issue",
                    ticket_id=iss_id,
                    title=iss_type,
                    status=iss_status,
                    priority="High",
                    notes=notes
                )
                if o_id and o_id in self.graph:
                    self.graph.add_edge(o_id, iss_id, key="HAS_ISSUE", relation="HAS_ISSUE")
                if agt_id and agt_id in self.graph:
                    self.graph.add_edge(iss_id, agt_id, key="ASSIGNED_TO", relation="ASSIGNED_TO")

            conn.close()
            logger.info(f"Knowledge Graph initialized directly from database: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")
            return True
        except Exception as e:
            logger.error(f"Error loading Knowledge Graph from database: {e}", exc_info=True)
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            return False

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

        logger.info(f"Knowledge Graph initialized from seed file: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")

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
