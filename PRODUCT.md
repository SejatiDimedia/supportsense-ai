# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React (Vite), Tailwind CSS, Lucide React icons, communicating with existing FastAPI backend (port 8000).

## Users

Customer support specialists, operations managers, and test evaluators assessing the intelligence and reliability of an enterprise AI support assistant.

## Product Purpose

SupportSense AI provides a multi-path customer support assistant combining unstructured knowledge retrieval (RAG via ChromaDB), structured relational graph traversal (KAG via PostgreSQL), and zero-loss human escalation with live telemetry and grounding inspection.

## Positioning

Unlike typical chatbot wrappers that hallucinate order details or operate in a black box, SupportSense AI explicitly identifies the origin of every answer (RAG, KAG, Hybrid, Direct, Escalated), retains multi-turn relational context across orders and support tickets, and displays the exact grounding records used.

## Operating Context

Evaluators and operators use this interface in desktop and tablet viewports to interactively test inquiries, inspect query routing, review database-backed order details, check system health, and test escalation queues.

## Capabilities and Constraints

- Dynamic intent routing: RAG (policies, manuals), KAG (order and ticket graph), Hybrid, Direct (<5ms greetings), and Escalation.
- Resilient zero-loss human escalation via webhook queue.
- Live observability: Latency (ms), route badges, confidence scores, and raw grounding drawer.
- Zero emoji or emoticon rule in all interface copy and communications.
- Real-time telemetry: PostgreSQL connection, ChromaDB collection count, Knowledge Graph node/edge count, and pending webhook queue depth.

## Brand Commitments

- Name: SupportSense AI
- Tone: Precise, operational, highly credible, professional enterprise tool.
- Visual Mode: Operate (dense, scannable, high contrast, clean typography, deliberate micro-interactions).

## Product Principles

- Transparency over magic: Always expose the reasoning path, route taken, and grounding context.
- Operational speed: Sub-second interactions for cached and direct routes, clear progress indicators for model inference.
- Reliable state: Unbroken multi-turn conversation flow with seamless session continuity.
