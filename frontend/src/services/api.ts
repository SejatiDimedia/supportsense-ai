import { ChatRequest, ChatResponse, TelemetryData } from '../types';

const BASE_URL = '';

export async function sendChatMessage(req: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Chat API error (${response.status}): ${errorText}`);
  }

  return response.json();
}

export async function getTelemetryData(): Promise<TelemetryData> {
  const response = await fetch(`${BASE_URL}/api/telemetry`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    }
  });

  if (!response.ok) {
    throw new Error(`Telemetry API error (${response.status})`);
  }

  return response.json();
}

export async function getHealthStatus(): Promise<{ status: string; ollama: boolean }> {
  const response = await fetch(`${BASE_URL}/health`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    }
  });

  if (!response.ok) {
    throw new Error(`Health API error (${response.status})`);
  }

  return response.json();
}
