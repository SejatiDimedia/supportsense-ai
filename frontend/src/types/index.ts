export type RouteType = 'rag' | 'kag' | 'hybrid' | 'direct' | 'escalated';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  route_taken?: RouteType;
  confidence_score?: number;
  escalated?: boolean;
  latency_ms?: number;
  trace_id?: string;
  context_used?: string;
  isStreaming?: boolean;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  trace_id: string;
  answer: string;
  route_taken: RouteType;
  confidence_score: number;
  escalated: boolean;
  latency_ms: number;
  context_used: string;
}

export interface TelemetryData {
  status: string;
  app_name: string;
  chroma_count: number;
  graph_nodes: number;
  graph_edges: number;
  pending_escalations: number;
  models: {
    llm: string;
    embedding: string;
  };
  database: {
    engine?: string;
    connected: boolean;
  };
}

export interface ScenarioItem {
  id: string;
  title: string;
  category: string;
  prompt: string;
  expectedRoute: RouteType;
}

export interface SessionItem {
  id: string;
  title: string;
  updatedAt: number;
}

