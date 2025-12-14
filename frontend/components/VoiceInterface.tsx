"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Volume2, Bot, User, Loader2 } from "lucide-react";
import clsx from "clsx";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function VoiceInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
        stream.getTracks().forEach((track) => track.stop());
        await processAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError("Could not access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true);

    try {
      // 1. Transcribe audio
      const formData = new FormData();
      formData.append("audio", audioBlob, "audio.webm");

      const transcribeResponse = await fetch(`${API_URL}/voice/transcribe`, {
        method: "POST",
        body: formData,
      });

      if (!transcribeResponse.ok) {
        throw new Error("Transcription failed");
      }

      const { transcript } = await transcribeResponse.json();

      if (!transcript.trim()) {
        setError("Could not understand audio. Please try again.");
        setIsProcessing(false);
        return;
      }

      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: transcript,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // 2. Get chat response
      const chatResponse = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: transcript,
          session_id: sessionId,
        }),
      });

      if (!chatResponse.ok) {
        throw new Error("Chat request failed");
      }

      const chatData = await chatResponse.json();

      if (!sessionId) {
        setSessionId(chatData.session_id);
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: chatData.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // 3. Synthesize speech
      await speakText(chatData.response);
    } catch (err) {
      console.error("Error processing audio:", err);
      setError("An error occurred. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const speakText = async (text: string) => {
    setIsSpeaking(true);

    try {
      const response = await fetch(`${API_URL}/voice/synthesize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error("Speech synthesis failed");
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.onended = () => {
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
        };
        await audioRef.current.play();
      }
    } catch (err) {
      console.error("Error synthesizing speech:", err);
      setIsSpeaking(false);
    }
  };

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsSpeaking(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      {/* Hidden audio element for playback */}
      <audio ref={audioRef} className="hidden" />

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 bg-nissan-red/10 rounded-full flex items-center justify-center mb-4">
              <Mic className="w-10 h-10 text-nissan-red" />
            </div>
            <h2 className="text-xl font-semibold text-nissan-gray-900 mb-2">
              Voice Assistant
            </h2>
            <p className="text-nissan-gray-500 mb-6 max-w-md">
              Press and hold the microphone button to ask your question.
              Release to send.
            </p>
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

            {/* Processing Indicator */}
            {isProcessing && (
              <div className="flex gap-3 items-start message-animate">
                <div className="w-8 h-8 bg-nissan-red rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white border border-nissan-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-nissan-gray-400 rounded-full typing-dot"></span>
                    <span className="w-2 h-2 bg-nissan-gray-400 rounded-full typing-dot"></span>
                    <span className="w-2 h-2 bg-nissan-gray-400 rounded-full typing-dot"></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Voice Controls */}
      <div className="border-t border-nissan-gray-200 bg-white p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm text-center">
            {error}
          </div>
        )}

        <div className="flex flex-col items-center gap-4">
          {/* Status Text */}
          <p className="text-sm text-nissan-gray-500">
            {isRecording
              ? "Listening... Release to send"
              : isProcessing
              ? "Processing..."
              : isSpeaking
              ? "Speaking..."
              : "Hold to speak"}
          </p>

          {/* Control Buttons */}
          <div className="flex items-center gap-4">
            {/* Stop Speaking Button */}
            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                className="w-12 h-12 rounded-full bg-nissan-gray-200 flex items-center justify-center hover:bg-nissan-gray-300 transition-colors"
              >
                <Volume2 className="w-6 h-6 text-nissan-gray-600" />
              </button>
            )}

            {/* Main Microphone Button */}
            <button
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={stopRecording}
              onTouchStart={startRecording}
              onTouchEnd={stopRecording}
              disabled={isProcessing || isSpeaking}
              className={clsx(
                "w-20 h-20 rounded-full flex items-center justify-center transition-all",
                isRecording
                  ? "bg-nissan-red recording-pulse scale-110"
                  : isProcessing || isSpeaking
                  ? "bg-nissan-gray-300 cursor-not-allowed"
                  : "bg-nissan-red hover:bg-nissan-red/90 hover:scale-105"
              )}
            >
              {isProcessing ? (
                <Loader2 className="w-8 h-8 text-white animate-spin" />
              ) : isRecording ? (
                <MicOff className="w-8 h-8 text-white" />
              ) : (
                <Mic className="w-8 h-8 text-white" />
              )}
            </button>

            {/* Placeholder for symmetry */}
            {isSpeaking && <div className="w-12 h-12" />}
          </div>
        </div>

        <p className="text-xs text-nissan-gray-400 mt-4 text-center">
          Nissan Assistant may make mistakes. Verify important information with
          a dealer.
        </p>
      </div>
    </div>
  );
}
