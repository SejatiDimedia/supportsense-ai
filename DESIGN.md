---
name: SupportSense AI Console
description: High-density graphite developer and operator console for AI customer support
colors:
  primary: "#10B981"
  primary-hover: "#34D399"
  primary-tint: "rgba(16, 185, 129, 0.12)"
  surface-ground: "#070A0F"
  surface-card: "#0B0F17"
  surface-panel: "#111722"
  border-subtle: "rgba(255, 255, 255, 0.08)"
  border-active: "rgba(52, 211, 153, 0.4)"
  text-primary: "#F8FAFC"
  text-secondary: "#94A3B8"
  text-muted: "#64748B"
  route-rag: "#34D399"
  route-kag: "#A78BFA"
  route-hybrid: "#FBBF24"
  route-direct: "#60A5FA"
  route-escalated: "#F87171"
typography:
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    letterSpacing: "-0.02em"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  tabular:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
    fontSize: "0.75rem"
    fontWeight: 500
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
---

## Overview

SupportSense AI Console is an operational, high-density interface built for customer support specialists and technical evaluators. It prioritizes scanability, sub-millisecond route attribution, transparent grounding inspection, and resilient human escalation.

## Colors

The interface employs a dark-first graphite palette anchored on `#070A0F` and `#0B0F17` with hairline seams (`rgba(255, 255, 255, 0.08)`):

- **Primary Accent**: Emerald (`#10B981`, `#34D399`) for primary actions, connection health, and verified document grounding.
- **Route Tints**:
  - `RAG`: Emerald (`#34D399`, bg `rgba(16, 185, 129, 0.12)`)
  - `KAG`: Violet (`#A78BFA`, bg `rgba(139, 92, 246, 0.12)`)
  - `Hybrid`: Amber (`#FBBF24`, bg `rgba(245, 158, 11, 0.12)`)
  - `Direct`: Sky Blue (`#60A5FA`, bg `rgba(59, 130, 246, 0.12)`)
  - `Escalated`: Coral Red (`#F87171`, bg `rgba(239, 68, 68, 0.14)`)

## Typography

- **Interface Sans**: Apple system stack / Segoe UI / Roboto for natural reading ergonomics.
- **Monospaced Numerals**: `ui-monospace` for tabular data, timestamps, session IDs, latencies, and trace IDs.

## Layout

A three-tier operational shell:
1. **Header & Cockpit Bar**: Compact fixed status header with live ChromaDB, PostgreSQL, and escalation queue counters.
2. **Interactive Workspace**: Split view accommodating the central conversational stream (2/3 width) and the collapsible Grounding Audit Drawer (1/3 width).
3. **Ergonomic Input Console**: Bottom-docked keyboard console supporting Enter to send and Shift+Enter for multiline input.

## Elevation & Depth

Tonal elevation with 1px hairline seams rather than heavy drop shadows. Focus states utilize a 2px emerald outline with 1px offset.

## Shapes

- Containers and panels: Rounded 8px (`rounded-lg`) or 12px (`rounded-xl`).
- Chips and badges: Fully rounded pills (`rounded-full`) or 4px (`rounded`).

## Components

- **Header**: Top navigation, session ID display with copy confirmation, and backend status indicator.
- **TelemetryBar**: Live cluster metrics bar tracking vector store and relational graph counts.
- **ScenarioChips**: Horizontal prompt launcher chips with category badges.
- **ChatStream**: Multi-turn message list with route tags, confidence scores, latency badges, and inline grounding inspector toggles.
- **GroundingDrawer**: Collapsible side inspection drawer displaying verified document excerpts and relational graph records.
- **InputConsole**: Text input with send trigger and keyboard shortcut hints.

## Do's and Don'ts

### Do
- Use Lucide React SVG icons with uniform 1.5px stroke.
- Format all latency and score numbers using monospaced font.
- Preserve zero-emoji compliance in all visual text, labels, and error states.

### Don't
- Do not use generic gradient text or colorful outer glows.
- Do not use emojis, emoticons, or Unicode symbols as iconography.
- Do not hide grounding or context details when an operator requests inspection.
