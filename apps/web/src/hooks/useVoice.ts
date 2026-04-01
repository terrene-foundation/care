"use client";

import { useCallback, useRef, useState } from "react";

interface UseVoiceReturn {
  isListening: boolean;
  isSupported: boolean;
  transcript: string;
  startListening: () => void;
  stopListening: () => void;
  showPrivacyNotice: boolean;
  dismissPrivacyNotice: () => void;
}

/**
 * Voice input hook using Web Speech API.
 *
 * Privacy: Web Speech API sends audio to external servers (typically Google)
 * for processing. This hook shows a disclosure notice on first use.
 * Voice is opt-in — text input is always the default.
 */
export function useVoice(onResult: (text: string) => void): UseVoiceReturn {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [showPrivacyNotice, setShowPrivacyNotice] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const isSupported =
    typeof window !== "undefined" &&
    ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  const startListening = useCallback(() => {
    if (!isSupported) return;

    // Show privacy notice on first use
    if (!privacyAccepted) {
      setShowPrivacyNotice(true);
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = "";
      let final = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      if (final) {
        onResult(final);
        setTranscript("");
      } else {
        setTranscript(interim);
      }
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  }, [isSupported, privacyAccepted, onResult]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  const acceptVoice = useCallback(() => {
    setPrivacyAccepted(true);
    setShowPrivacyNotice(false);
    // After accepting, immediately start listening
    setTimeout(() => startListening(), 100);
  }, [startListening]);

  const declineVoice = useCallback(() => {
    setShowPrivacyNotice(false);
    // Do NOT set privacyAccepted — voice stays disabled
  }, []);

  const dismissPrivacyNotice = acceptVoice;

  return {
    isListening,
    isSupported,
    transcript,
    startListening,
    stopListening,
    showPrivacyNotice,
    dismissPrivacyNotice,
    acceptVoice,
    declineVoice,
  };
}
