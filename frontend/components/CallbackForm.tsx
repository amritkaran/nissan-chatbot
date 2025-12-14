"use client";

import { useState } from "react";
import { X, Phone, Loader2, CheckCircle, AlertCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// European countries with dial codes
const COUNTRIES = [
  { code: "+44", name: "United Kingdom", flag: "🇬🇧", lang: "en" },
  { code: "+33", name: "France", flag: "🇫🇷", lang: "fr" },
  { code: "+49", name: "Germany", flag: "🇩🇪", lang: "de" },
  { code: "+34", name: "Spain", flag: "🇪🇸", lang: "es" },
  { code: "+39", name: "Italy", flag: "🇮🇹", lang: "it" },
  { code: "+31", name: "Netherlands", flag: "🇳🇱", lang: "nl" },
  { code: "+32", name: "Belgium", flag: "🇧🇪", lang: "fr" },
  { code: "+351", name: "Portugal", flag: "🇵🇹", lang: "pt" },
  { code: "+43", name: "Austria", flag: "🇦🇹", lang: "de" },
  { code: "+41", name: "Switzerland", flag: "🇨🇭", lang: "de" },
  { code: "+353", name: "Ireland", flag: "🇮🇪", lang: "en" },
  { code: "+48", name: "Poland", flag: "🇵🇱", lang: "pl" },
  { code: "+46", name: "Sweden", flag: "🇸🇪", lang: "sv" },
  { code: "+47", name: "Norway", flag: "🇳🇴", lang: "no" },
  { code: "+45", name: "Denmark", flag: "🇩🇰", lang: "da" },
];

interface CallbackFormProps {
  sessionId: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

type FormStatus = "idle" | "loading" | "success" | "error";

export default function CallbackForm({
  sessionId,
  onClose,
  onSuccess,
}: CallbackFormProps) {
  const [selectedCountry, setSelectedCountry] = useState(COUNTRIES[0]);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [status, setStatus] = useState<FormStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate phone number
    const cleanNumber = phoneNumber.replace(/\s/g, "");
    if (cleanNumber.length < 6 || cleanNumber.length > 15) {
      setErrorMessage("Please enter a valid phone number");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setErrorMessage("");

    try {
      const response = await fetch(`${API_URL}/call/request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone_number: cleanNumber,
          country_code: selectedCountry.code,
          session_id: sessionId,
          language: selectedCountry.lang,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to request callback");
      }

      setStatus("success");
      onSuccess();

      // Auto-close after success
      setTimeout(() => {
        onClose();
      }, 3000);
    } catch (error) {
      console.error("Callback request failed:", error);
      setErrorMessage(
        error instanceof Error ? error.message : "Failed to request callback"
      );
      setStatus("error");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-nissan-red text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Phone className="w-5 h-5" />
            <h2 className="font-semibold">Request a Callback</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-white/20 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {status === "success" ? (
            <div className="text-center py-8">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Call Requested!
              </h3>
              <p className="text-gray-600">
                Rashi will call you shortly at
                <br />
                <span className="font-medium">
                  {selectedCountry.code} {phoneNumber}
                </span>
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <p className="text-gray-600 text-sm">
                Our AI assistant Rashi will call you to help with your Nissan
                questions. She speaks multiple European languages.
              </p>

              {/* Country Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Country
                </label>
                <select
                  value={selectedCountry.code}
                  onChange={(e) => {
                    const country = COUNTRIES.find(
                      (c) => c.code === e.target.value
                    );
                    if (country) setSelectedCountry(country);
                  }}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nissan-red focus:border-transparent outline-none"
                  disabled={status === "loading"}
                >
                  {COUNTRIES.map((country) => (
                    <option key={country.code} value={country.code}>
                      {country.flag} {country.name} ({country.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Phone Number Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <div className="flex">
                  <span className="inline-flex items-center px-4 bg-gray-100 border border-r-0 border-gray-300 rounded-l-lg text-gray-600 font-medium">
                    {selectedCountry.code}
                  </span>
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => {
                      // Only allow numbers and spaces
                      const value = e.target.value.replace(/[^\d\s]/g, "");
                      setPhoneNumber(value);
                      if (status === "error") setStatus("idle");
                    }}
                    placeholder="7911 123456"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-r-lg focus:ring-2 focus:ring-nissan-red focus:border-transparent outline-none"
                    disabled={status === "loading"}
                    required
                  />
                </div>
              </div>

              {/* Error Message */}
              {status === "error" && (
                <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={status === "loading" || !phoneNumber.trim()}
                className="w-full bg-nissan-red text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {status === "loading" ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Requesting call...
                  </>
                ) : (
                  <>
                    <Phone className="w-5 h-5" />
                    Call me now
                  </>
                )}
              </button>

              <p className="text-xs text-gray-500 text-center">
                By requesting a call, you agree to receive an automated call
                from our AI assistant.
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
