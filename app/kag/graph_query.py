import re
import logging
from typing import Dict, Any, Optional, List
from app.kag.graph_builder import SupportKnowledgeGraph

logger = logging.getLogger(__name__)

def extract_order_number(text: str) -> Optional[str]:
    """
    Extracts order numbers from queries such as:
    'Where is my order #4521?', 'order 4521', '#4521', 'Order Number: 4521'
    """
    if not text:
        return None

    # Matches #1234 or words like 'order 1234', 'order #1234'
    pattern = re.compile(r'(?:order\s*(?:number\s*|id\s*|#\s*)?|#)(\d{4,8})\b', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return f"#{match.group(1)}"

    # Standalone hashtag number fallback (e.g. '#4521')
    hash_match = re.search(r'#(\d{3,8})\b', text)
    if hash_match:
        return f"#{hash_match.group(1)}"

    return None

class GraphQueryEngine:
    """
    High-level query engine for the Knowledge Graph and Relational Database.
    Traverses relational paths: Customer -> Order -> Product -> Issue -> Agent.
    Falls back seamlessly to SQLRelationalQueryEngine (PostgreSQL / SQLite)
    for orders seeded into the relational database.
    """
    def __init__(
        self,
        knowledge_graph: Optional[SupportKnowledgeGraph] = None,
        sql_engine: Optional[Any] = None
    ):
        self.kg = knowledge_graph or SupportKnowledgeGraph()
        if sql_engine is None:
            from app.kag.sql_query import SQLRelationalQueryEngine
            self.sql_engine = SQLRelationalQueryEngine()
        else:
            self.sql_engine = sql_engine

    def query_order_context(self, order_num: str) -> Dict[str, Any]:
        """
        Traverses all relations connected to the given order number
        and generates a clean, structured context string for LLM ingestion.
        Checks Knowledge Graph first; if not present, queries live Relational Database.
        """
        order = self.kg.find_order(order_num)
        if not order:
            if self.sql_engine:
                sql_res = self.sql_engine.query_order_context(order_num)
                if sql_res.get("found"):
                    logger.info(f"Order '{order_num}' found in relational database ({sql_res.get('engine')}).")
                    return sql_res

            logger.info(f"Order '{order_num}' not found in knowledge graph or relational database.")
            return {
                "found": False,
                "order_number": order_num,
                "summary": f"Order {order_num} was not found in our records. Please verify the order number.",
                "data": {}
            }

        order_id = order["id"]

        # 1. Traverse incoming Customer (Customer -[PLACED]-> Order)
        customers = self.kg.get_neighbors(order_id, relation="PLACED", direction="in")
        customer = customers[0]["node_data"] if customers else {}

        # 2. Traverse outgoing Products (Order -[CONTAINS]-> Product)
        products_raw = self.kg.get_neighbors(order_id, relation="CONTAINS", direction="out")
        products = [p["node_data"] for p in products_raw]

        # 3. Traverse outgoing Issues (Order -[HAS_ISSUE]-> Issue)
        issues_raw = self.kg.get_neighbors(order_id, relation="HAS_ISSUE", direction="out")
        issues_list = []

        for item in issues_raw:
            iss_id = item["node_id"]
            iss_data = dict(item["node_data"])

            # Traverse Issue -[ASSIGNED_TO]-> Agent
            agent_raw = self.kg.get_neighbors(iss_id, relation="ASSIGNED_TO", direction="out")
            assigned_agent = agent_raw[0]["node_data"] if agent_raw else None
            iss_data["assigned_agent"] = assigned_agent
            issues_list.append(iss_data)

        # Build clean formatted text summary
        summary_lines = [
            "[RELATIONAL ORDER CONTEXT]",
            f"• Order Number    : {order.get('order_number')}",
            f"• Order Date      : {order.get('order_date')}",
            f"• Order Status    : {order.get('status', '').replace('_', ' ').title()}",
            f"• Shipping Carrier: {order.get('shipping_carrier', 'N/A')} (Tracking: {order.get('tracking_number', 'N/A')})",
            f"• Est. Delivery   : {order.get('estimated_delivery') or order.get('delivered_date', 'N/A')}",
        ]

        if customer:
            tier = customer.get('tier', 'Standard')
            summary_lines.append(f"• Customer Name   : {customer.get('name')} (Tier: {tier}, Email: {customer.get('email')})")

        if products:
            prod_names = [f"{p.get('name')} (${p.get('price')})" for p in products]
            summary_lines.append(f"• Items in Order  : {', '.join(prod_names)}")

        if issues_list:
            summary_lines.append("\n[ACTIVE ISSUES & ASSIGNED SUPPORT AGENT]")
            for iss in issues_list:
                summary_lines.append(f"• Issue Ticket    : {iss.get('ticket_id')} — {iss.get('title')}")
                summary_lines.append(f"• Ticket Status   : {iss.get('status')} (Priority: {iss.get('priority')})")
                if iss.get("notes"):
                    summary_lines.append(f"• Notes           : {iss.get('notes')}")
                agent = iss.get("assigned_agent")
                if agent:
                    summary_lines.append(f"• Handling Agent  : {agent.get('name')} ({agent.get('role')})")
                    summary_lines.append(f"• Agent Contact   : {agent.get('email')}")
        else:
            summary_lines.append("\n[ACTIVE ISSUES]")
            summary_lines.append("• No reported issues or complaints logged for this order.")

        summary_text = "\n".join(summary_lines)

        return {
            "found": True,
            "order_number": order.get("order_number"),
            "summary": summary_text,
            "data": {
                "order": order,
                "customer": customer,
                "products": products,
                "issues": issues_list
            }
        }

    def query_by_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extracts order number from user text and retrieves full context.
        Returns None if no order number pattern is found.
        """
        extracted_order = extract_order_number(text)
        if extracted_order:
            return self.query_order_context(extracted_order)
        return None
