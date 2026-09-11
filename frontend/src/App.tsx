import { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { WelcomeHero } from './components/WelcomeHero';
import { ScenarioCards } from './components/ScenarioCards';
import { InputConsole } from './components/InputConsole';
import { ChatStream } from './components/ChatStream';
import { GroundingDrawer } from './components/GroundingDrawer';
import { TelemetryModal } from './components/TelemetryModal';
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
  const [_isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [selectedMessage, setSelectedMessage] = useState<ChatMessage | null>(null);
  const [isTelemetryModalOpen, setIsTelemetryModalOpen] = useState<boolean>(false);

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
    } catch {
      // Graceful fallback
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
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
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
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        route_taken: res.route_taken,
        confidence_score: res.confidence_score,
        escalated: res.escalated,
        latency_ms: res.latency_ms || clientLatency,
        trace_id: res.trace_id,
        context_used: res.context_used,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (assistantMessage.context_used) {
        setSelectedMessage(assistantMessage);
      }

      refreshTelemetry();
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: `msg_err_${Date.now()}`,
        sender: 'assistant',
        text: `Error connecting to assistant engine: ${err.message || 'Unknown network error'}. Please verify FastAPI backend on port 8000.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
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
    <div className="flex h-screen w-screen bg-[#070A0F] text-slate-900 overflow-hidden font-sans">
      {/* 1. Left Dark Sidebar (Matching Reference Screenshot) */}
      <Sidebar
        onNewChat={handleResetSession}
        telemetry={telemetry}
        onOpenTelemetryModal={() => setIsTelemetryModalOpen(true)}
      />

      {/* 2. Floating High-Radius White Canvas */}
      <main className="my-2.5 mr-2.5 flex flex-1 flex-col overflow-hidden rounded-[24px] bg-white shadow-2xl border border-white/[0.05]">
        {/* Canvas Top Bar with Model Dropdown & Profile */}
        <Header
          sessionId={sessionId}
          onResetSession={handleResetSession}
        />

        {/* Canvas Body: Welcome Hero (if empty) vs Chat Stream (if active) */}
        <div className="flex flex-1 overflow-hidden">
          <div className="flex flex-1 flex-col overflow-y-auto">
            {messages.length === 0 ? (
              <div className="flex flex-1 flex-col justify-center pb-12">
                <WelcomeHero />
                <InputConsole
                  onSendMessage={handleSendMessage}
                  isLoading={isLoading}
                />
                <ScenarioCards
                  onSelectScenario={handleSendMessage}
                  disabled={isLoading}
                />
              </div>
            ) : (
              <div className="flex flex-1 flex-col justify-between overflow-hidden">
                <ChatStream
                  messages={messages}
                  isLoading={isLoading}
                  onInspectContext={(msg) => setSelectedMessage(msg)}
                  selectedMessageId={selectedMessage?.id}
                />
                <div className="pb-4 bg-white/80 backdrop-blur-sm">
                  <InputConsole
                    onSendMessage={handleSendMessage}
                    isLoading={isLoading}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Collapsible Grounding Audit Inspector */}
          {selectedMessage && (
            <GroundingDrawer
              message={selectedMessage}
              onClose={() => setSelectedMessage(null)}
            />
          )}
        </div>
      </main>

      {/* Telemetry & Cluster Architecture Modal */}
      <TelemetryModal
        isOpen={isTelemetryModalOpen}
        onClose={() => setIsTelemetryModalOpen(false)}
        telemetry={telemetry}
      />
    </div>
  );
}

export default App;
