---
name: SupportSense AI Console
description: Dual-tone enterprise console with dark navigation sidebar, floating white workspace canvas, and chartreuse accents
colors:
  primary-lime: "#D4F638"
  primary-lime-hover: "#B5E424"
  sidebar-bg: "#0E1116"
  sidebar-card: "#181C23"
  sidebar-border: "rgba(255, 255, 255, 0.08)"
  sidebar-text: "#9CA3AF"
  canvas-bg: "#FFFFFF"
  canvas-surface: "#F8F9FA"
  canvas-border: "#E5E7EB"
  canvas-text: "#111827"
  canvas-muted: "#6B7280"
  route-rag: "#10B981"
  route-kag: "#8B5CF6"
  route-hybrid: "#F59E0B"
  route-direct: "#3B82F6"
  route-escalated: "#EF4444"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 700
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    letterSpacing: "-0.01em"
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
  sm: "6px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  2xl: "24px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "32px"
---

## Overview

SupportSense AI Console is an operational, dual-tone AI assistant interface inspired by high-craft modern design. It pairs a dark charcoal navigation sidebar with a high-radius white canvas workspace, anchored by vibrant chartreuse/lime accents.

## Colors

- **Left Sidebar**: Deep charcoal (`#0E1116`) with hairline borders (`rgba(255, 255, 255, 0.08)`), dark telemetry card (`#181C23`), and muted text (`#9CA3AF`).
- **Accent Highlight**: Electric Lime / Chartreuse (`#D4F638` / `#C6F432`) for active icon badge squares and primary audit CTA buttons.
- **Main Canvas**: Crisp white card (`#FFFFFF`) with subtle border (`#E5E7EB`), soft off-white secondary surfaces (`#F8F9FA`), and high-contrast dark text (`#111827`, `#374151`).
- **Semantic Route Tokens**:
  - `RAG`: Emerald (`#10B981`, bg `rgba(16, 185, 129, 0.12)`)
  - `KAG`: Violet (`#8B5CF6`, bg `rgba(139, 92, 246, 0.12)`)
  - `Hybrid`: Amber (`#F59E0B`, bg `rgba(245, 158, 11, 0.12)`)
  - `Direct`: Sky Blue (`#3B82F6`, bg `rgba(59, 130, 246, 0.12)`)
  - `Escalated`: Coral Red (`#EF4444`, bg `rgba(239, 68, 68, 0.12)`)

## Typography

- **Interface Sans**: Apple system stack / Segoe UI / Roboto for high readability.
- **Monospaced Figures**: `ui-monospace` for tabular data, latency metrics, session IDs, and trace IDs.

## Layout

1. **Outer Shell**: Deep dark frame (`#070A0F`).
2. **Left Navigation Sidebar**: Fixed 64-width sidebar containing the brand mark, "New chat" button with `⌘ N`, search, recent session list, telemetry status card, and documentation links.
3. **Floating Canvas**: Large rounded white card (`rounded-[24px]`) inside the outer frame containing the model selector header, centered welcome hero, prominent floating input container, and 3 scenario cards with lime icon boxes.
4. **Conversational Stream**: Switches to a clean chat stream when active, with dark user bubbles and light assistant cards.
5. **Grounding Drawer**: Collapsible side audit inspector revealing raw database records and ChromaDB excerpts.

## Elevation & Depth

- The canvas floats on the dark background with `rounded-[24px]` and soft depth (`shadow-2xl`).
- Cards inside the canvas use subtle borders (`border-slate-200/90`) and gentle hover elevations.

## Shapes

- Canvas container: `rounded-[24px]` (`24px`).
- Feature cards & Input container: `rounded-2xl` (`16px`).
- Buttons & icon boxes: `rounded-lg` (`8px`) or `rounded-xl` (`12px`).

## Components

- **Sidebar**: Dark navigation, New Chat button, cluster status card with lime action button.
- **Header**: Top canvas bar with model selector dropdown and operator avatar.
- **WelcomeHero**: Centered greeting and subtitle.
- **InputConsole**: Floating input bar with `+` action, audio indicator, and black circular upward arrow.
- **ScenarioCards**: 3 white cards with vibrant lime square icon boxes.
- **ChatStream**: Conversation history with semantic route badges, confidence scores, and latency.
- **GroundingDrawer**: Side inspector displaying raw grounding context.
- **TelemetryModal**: Detailed modal presenting cluster metrics.

## Do's and Don'ts

### Do
- Use Lucide React SVG icons with uniform 1.5px stroke.
- Ensure text on lime backgrounds is strictly `#000000` (pure black) for maximum contrast.
- Preserve zero-emoji compliance across all visual text, labels, and error states.

### Don't
- Do not use generic gradient text or neon glows.
- Do not use emojis or emoticons as iconography.
- Do not hide grounding or context details when an operator requests inspection.
