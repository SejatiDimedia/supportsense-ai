import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { TelemetryBar } from './components/TelemetryBar';
import { ScenarioChips } from './components/ScenarioChips';
import { ChatStream } from './components/ChatStream';
import { GroundingDrawer } from './components/GroundingDrawer';
import { InputConsole } from './components/InputConsole';
import { sendChatMessage, getTelemetryData, getHealthStatus } from './services/api';
import { ChatMessage, TelemetryData } from './types';

function generateSessionId(): string {
  return `sess_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 7)}`;
}

export function App() {
  const [sessionId, setSessionId] = useState<string>(() => {
    const saved = localStorage.getItem('supportsense_session_id');
    if (saved) return saved;
    const newId = generateSessionId();
    localStorage.setItem('supportsense_session_id', newId);
    return newId;
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [isTelemetryLoading, setIsTelemetryLoading] = useState<boolean>(true);
  const [selectedMessage, setSelectedMessage] = useState<ChatMessage | null>(null);

  // Poll health & telemetry
  const refreshTelemetry = useCallback(async () => {
    try {
      const [healthRes, telemetryRes] = await Promise.all([
        getHealthStatus().catch(() => ({ status: 'down', ollama: false })),
        getTelemetryData().catch(() => null),
      ]);

      setIsBackendHealthy(healthRes.status === 'ok');
      if (telemetryRes) {
        setTelemetry(telemetryRes);
      }
    } finally {
      setIsTelemetryLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshTelemetry();
    const interval = setInterval(refreshTelemetry, 10000);
    return () => clearInterval(interval);
  }, [refreshTelemetry]);

  const handleResetSession = () => {
    const newId = generateSessionId();
    localStorage.setItem('supportsense_session_id', newId);
    setSessionId(newId);
    setMessages([]);
    setSelectedMessage(null);
  };

  const handleSendMessage = async (userText: string) => {
    if (!userText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `msg_user_${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const startTime = performance.now();
      const res = await sendChatMessage({
        message: userText,
        session_id: sessionId,
      });
      const clientLatency = performance.now() - startTime;

      const assistantMessage: ChatMessage = {
        id: `msg_ast_${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        route_taken: res.route_taken,
        confidence_score: res.confidence_score,
        escalated: res.escalated,
        latency_ms: res.latency_ms || clientLatency,
        trace_id: res.trace_id,
        context_used: res.context_used,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // If this message has context, automatically open or update drawer for inspection
      if (assistantMessage.context_used) {
        setSelectedMessage(assistantMessage);
      }

      // Refresh telemetry after interaction
      refreshTelemetry();
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: `msg_err_${Date.now()}`,
        sender: 'assistant',
        text: `Error contacting assistant engine: ${err.message || 'Unknown network error'}. Please ensure FastAPI backend is running on port 8000.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        route_taken: 'direct',
        confidence_score: 0,
        escalated: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen flex-col bg-[#070A0F] text-slate-100 antialiased select-none">
      {/* 1. Brand Header */}
      <Header
        sessionId={sessionId}
        isBackendHealthy={isBackendHealthy}
        onResetSession={handleResetSession}
      />

      {/* 2. Telemetry Cockpit */}
      <TelemetryBar
        telemetry={telemetry}
        isLoading={isTelemetryLoading}
      />

      {/* 3. Pre-Canned PRD Scenario Chips */}
      <ScenarioChips
        onSelectScenario={handleSendMessage}
        disabled={isLoading}
      />

      {/* 4. Main Body: Split View (Chat Stream + Grounding Drawer) */}
      <div className="flex flex-1 overflow-hidden select-text">
        <ChatStream
          messages={messages}
          isLoading={isLoading}
          onInspectContext={(msg) => setSelectedMessage(msg)}
          selectedMessageId={selectedMessage?.id}
        />

        {selectedMessage && (
          <GroundingDrawer
            message={selectedMessage}
            onClose={() => setSelectedMessage(null)}
          />
        )}
      </div>

      {/* 5. Input Console */}
      <InputConsole
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </div>
  );
}

export default App;
