import { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { WelcomeHero } from './components/WelcomeHero';
import { ScenarioCards } from './components/ScenarioCards';
import { InputConsole } from './components/InputConsole';
import { ChatStream } from './components/ChatStream';
import { GroundingDrawer } from './components/GroundingDrawer';
import { TelemetryModal } from './components/TelemetryModal';
import { ErrorBoundary } from './components/ErrorBoundary';
import { sendChatMessage, getTelemetryData, getHealthStatus } from './services/api';
import { ChatMessage, TelemetryData, SessionItem } from './types';

const SESSIONS_STORAGE_KEY = 'supportsense_sessions';
const ACTIVE_SESSION_KEY = 'supportsense_session_id';
const HISTORY_STORAGE_PREFIX = 'supportsense_history_';

function generateSessionId(): string {
  return `sess_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 7)}`;
}

function loadStoredSessions(): SessionItem[] {
  try {
    const raw = localStorage.getItem(SESSIONS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function loadStoredMessages(sessionId: string): ChatMessage[] {
  try {
    const raw = localStorage.getItem(`${HISTORY_STORAGE_PREFIX}${sessionId}`);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function AppContent() {
  const [sessions, setSessions] = useState<SessionItem[]>(() => loadStoredSessions());
  const [sessionId, setSessionId] = useState<string>(() => {
    const saved = localStorage.getItem(ACTIVE_SESSION_KEY);
    if (saved) return saved;
    const newId = generateSessionId();
    localStorage.setItem(ACTIVE_SESSION_KEY, newId);
    return newId;
  });

  const [messages, setMessages] = useState<ChatMessage[]>(() => loadStoredMessages(sessionId));
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [_isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [selectedMessage, setSelectedMessage] = useState<ChatMessage | null>(null);
  const [isTelemetryModalOpen, setIsTelemetryModalOpen] = useState<boolean>(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);

  // Synchronize messages to localStorage per session
  useEffect(() => {
    try {
      localStorage.setItem(`${HISTORY_STORAGE_PREFIX}${sessionId}`, JSON.stringify(messages));
    } catch {
      // Storage quota or privacy fallback
    }
  }, [messages, sessionId]);

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

  const handleSelectSession = (id: string) => {
    setSessionId(id);
    localStorage.setItem(ACTIVE_SESSION_KEY, id);
    setMessages(loadStoredMessages(id));
    setSelectedMessage(null);
    setIsMobileSidebarOpen(false);
  };

  const handleResetSession = () => {
    const newId = generateSessionId();
    localStorage.setItem(ACTIVE_SESSION_KEY, newId);
    setSessionId(newId);
    setMessages([]);
    setSelectedMessage(null);
    setIsMobileSidebarOpen(false);
  };

  const handleDeleteSession = (id: string) => {
    const updated = sessions.filter((s) => s.id !== id);
    setSessions(updated);
    try {
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(updated));
      localStorage.removeItem(`${HISTORY_STORAGE_PREFIX}${id}`);
    } catch {
      // Quota fallback
    }
    if (id === sessionId) {
      handleResetSession();
    }
  };

  const handleStreamingComplete = (msgId: string) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, isStreaming: false } : m))
    );
  };

  const handleSendMessage = async (userText: string) => {
    if (!userText.trim() || isLoading) return;

    // Register active session in the sessions list if not already present
    setSessions((prev) => {
      const exists = prev.some((s) => s.id === sessionId);
      if (!exists) {
        const title = userText.trim().length > 36 ? `${userText.trim().slice(0, 36)}...` : userText.trim();
        const newSession: SessionItem = {
          id: sessionId,
          title,
          updatedAt: Date.now(),
        };
        const updated = [newSession, ...prev];
        try {
          localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(updated));
        } catch {
          // Quota fallback
        }
        return updated;
      }
      return prev;
    });

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
        isStreaming: true,
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
        isStreaming: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#070A0F] text-slate-900 overflow-hidden font-sans relative">
      {/* 1. Left Dark Sidebar with Mobile Drawer support */}
      <Sidebar
        onNewChat={handleResetSession}
        telemetry={telemetry}
        onOpenTelemetryModal={() => setIsTelemetryModalOpen(true)}
        isMobileOpen={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
        sessions={sessions}
        currentSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
      />

      {/* 2. Floating Canvas with Responsive Margin and Radius */}
      <main className="m-0 rounded-none md:my-2.5 md:mr-2.5 md:rounded-[24px] flex flex-1 flex-col overflow-hidden bg-white shadow-2xl border border-white/[0.05]">
        {/* Canvas Top Bar with Mobile Hamburger, Model Dropdown & Profile */}
        <Header
          sessionId={sessionId}
          onResetSession={handleResetSession}
          onToggleMobileSidebar={() => setIsMobileSidebarOpen((prev) => !prev)}
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
                  onStreamingComplete={handleStreamingComplete}
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

export function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}

export default App;
