"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Bot, User, Loader2, Phone } from "lucide-react";
import clsx from "clsx";
import CallbackForm from "./CallbackForm";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SUGGESTED_QUESTIONS = [
  "What is the Nissan Qashqai e-POWER?",
  "Tell me about the Nissan Juke",
  "What electric vehicles does Nissan offer?",
  "What are the X-Trail features?",
];

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showCallbackForm, setShowCallbackForm] = useState(false);
  const [callbackSuccess, setCallbackSuccess] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const streamingRef = useRef("");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const updateStreamingContent = useCallback((text: string) => {
    streamingRef.current = text;
    setStreamingContent(text);
  }, []);

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageText.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    streamingRef.current = "";
    setStreamingContent("");

    try {
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: messageText.trim(),
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let newSessionId = sessionId;

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const text = decoder.decode(value, { stream: true });
        const lines = text.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (data === "[DONE]") continue;

            try {
              const parsed = JSON.parse(data);
              if (parsed.text) {
                streamingRef.current += parsed.text;
                // Force immediate update
                setStreamingContent(streamingRef.current);
              }
              if (parsed.session_id && !newSessionId) {
                newSessionId = parsed.session_id;
                setSessionId(parsed.session_id);
              }
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }

      // Add completed message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: streamingRef.current,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      streamingRef.current = "";
      setStreamingContent("");
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      streamingRef.current = "";
      setStreamingContent("");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !streamingContent ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-nissan-red/10 rounded-full flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-nissan-red" />
            </div>
            <h2 className="text-xl font-semibold text-nissan-gray-900 mb-2">
              Welcome to Nissan UK Assistant
            </h2>
            <p className="text-nissan-gray-500 mb-6 max-w-md">
              I can help you with information about Nissan vehicles, features,
              specifications, and more. How can I assist you today?
            </p>

            {/* Suggested Questions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {SUGGESTED_QUESTIONS.map((question, index) => (
                <button
                  key={index}
                  onClick={() => sendMessage(question)}
                  className="text-left p-3 bg-white border border-nissan-gray-200 rounded-lg hover:border-nissan-red hover:bg-nissan-red/5 transition-colors text-sm text-nissan-gray-700"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={clsx(
                  "flex gap-3 message-animate",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {message.role === "assistant" && (
                  <div className="w-8 h-8 bg-nissan-red rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={clsx(
                    "max-w-[70%] rounded-2xl px-4 py-3",
                    message.role === "user"
                      ? "bg-nissan-red text-white rounded-br-md"
                      : "bg-white border border-nissan-gray-200 text-nissan-gray-900 rounded-bl-md"
                  )}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <span
                    className={clsx(
                      "text-xs mt-1 block",
                      message.role === "user"
                        ? "text-white/70"
                        : "text-nissan-gray-400"
                    )}
                  >
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>

                {message.role === "user" && (
                  <div className="w-8 h-8 bg-nissan-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-nissan-gray-600" />
                  </div>
                )}
              </div>
            ))}

            {/* Streaming Response */}
            {(isLoading || streamingContent) && (
              <div className="flex gap-3 items-start message-animate">
                <div className="w-8 h-8 bg-nissan-red rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="max-w-[70%] bg-white border border-nissan-gray-200 text-nissan-gray-900 rounded-2xl rounded-bl-md px-4 py-3">
                  {streamingContent ? (
                    <>
                      <p className="whitespace-pre-wrap">{streamingContent}</p>
                      <span className="inline-block w-2 h-4 bg-nissan-red/60 animate-pulse ml-1"></span>
                    </>
                  ) : (
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-nissan-gray-400 rounded-full typing-dot"></span>
                      <span className="w-2 h-2 bg-nissan-gray-400 rounded-full typing-dot"></span>
                      <span className="w-2 h-2 bg-nissan-gray-400 rounded-full typing-dot"></span>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Form */}
      <div className="border-t border-nissan-gray-200 bg-white p-4">
        {/* Call me button */}
        <div className="flex justify-center mb-3">
          <button
            onClick={() => setShowCallbackForm(true)}
            className={clsx(
              "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors",
              callbackSuccess
                ? "bg-green-100 text-green-700"
                : "bg-nissan-gray-100 text-nissan-gray-700 hover:bg-nissan-red/10 hover:text-nissan-red"
            )}
          >
            <Phone className="w-4 h-4" />
            {callbackSuccess ? "Call requested!" : "Prefer a call? Talk to Rashi"}
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about Nissan vehicles..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-nissan-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-nissan-red/50 focus:border-nissan-red"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={clsx(
              "rounded-xl px-4 py-3 font-medium transition-colors flex items-center justify-center",
              input.trim() && !isLoading
                ? "bg-nissan-red text-white hover:bg-nissan-red/90"
                : "bg-nissan-gray-200 text-nissan-gray-400 cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
        <p className="text-xs text-nissan-gray-400 mt-2 text-center">
          Nissan Assistant may make mistakes. Verify important information with a dealer.
        </p>
      </div>

      {/* Callback Form Modal */}
      {showCallbackForm && (
        <CallbackForm
          sessionId={sessionId}
          onClose={() => setShowCallbackForm(false)}
          onSuccess={() => {
            setCallbackSuccess(true);
            setTimeout(() => setCallbackSuccess(false), 10000);
          }}
        />
      )}
    </div>
  );
}
