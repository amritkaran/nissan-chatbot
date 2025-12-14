/**
 * API client for Nissan chatbot backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
  response: string;
  session_id: string;
  sources: string[];
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  created_at: number;
}

/**
 * Send a chat message and get a response
 */
export async function sendChatMessage(
  message: string,
  sessionId?: string | null
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  return response.json();
}

/**
 * Stream a chat response
 */
export async function* streamChatMessage(
  message: string,
  sessionId?: string | null
): AsyncGenerator<{ text: string; session_id: string }> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Stream request failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") {
          return;
        }
        try {
          yield JSON.parse(data);
        } catch {
          // Skip invalid JSON
        }
      }
    }
  }
}

/**
 * Transcribe audio to text
 */
export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "audio.webm");

  const response = await fetch(`${API_URL}/voice/transcribe`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Transcription failed: ${response.status}`);
  }

  const data = await response.json();
  return data.transcript;
}

/**
 * Synthesize text to speech
 */
export async function synthesizeSpeech(
  text: string,
  voiceId?: string
): Promise<Blob> {
  const response = await fetch(`${API_URL}/voice/synthesize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text,
      voice_id: voiceId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Speech synthesis failed: ${response.status}`);
  }

  return response.blob();
}

/**
 * Get chat history for a session
 */
export async function getSessionHistory(
  sessionId: string
): Promise<{ history: Message[] }> {
  const response = await fetch(`${API_URL}/session/${sessionId}/history`);

  if (!response.ok) {
    throw new Error(`Failed to get history: ${response.status}`);
  }

  return response.json();
}

/**
 * Delete a chat session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_URL}/session/${sessionId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Failed to delete session: ${response.status}`);
  }
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<{
  status: string;
  assistant_configured: boolean;
  voice_configured: boolean;
  vapi_configured: boolean;
}> {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json();
}

/**
 * Request a callback from Rashi (Vapi voice assistant)
 */
export interface CallbackRequest {
  phone_number: string;
  country_code: string;
  session_id: string | null;
  language: string;
}

export interface CallbackResponse {
  call_id: string;
  status: string;
  message: string;
}

export async function requestCallback(
  data: CallbackRequest
): Promise<CallbackResponse> {
  const response = await fetch(`${API_URL}/call/request`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `Callback request failed: ${response.status}`);
  }

  return response.json();
}
