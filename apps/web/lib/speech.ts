export interface TranscriptResult {
  text: string;
  language: string;
  provider: string;
  isFinal: boolean;
  confidence?: number;
}

export interface SpeechTranscriber {
  start(onResult: (result: TranscriptResult) => void, onError: (message: string) => void): void;
  stop(): void;
  cancel(): void;
}

interface BrowserRecognitionEvent {
  results: ArrayLike<ArrayLike<{ transcript: string; confidence: number }> & { isFinal: boolean }>;
}

interface BrowserRecognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: BrowserRecognitionEvent) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

type RecognitionConstructor = new () => BrowserRecognition;

declare global {
  interface Window {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  }
}

export class BrowserSpeechTranscriber implements SpeechTranscriber {
  private recognition: BrowserRecognition | null = null;

  start(onResult: (result: TranscriptResult) => void, onError: (message: string) => void) {
    const Recognition = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!Recognition) {
      onError("Este navegador no ofrece transcripción de voz compatible.");
      return;
    }
    const recognition = new Recognition();
    recognition.lang = "es-EC";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      const results = Array.from(event.results);
      const text = results.map((result) => result[0]?.transcript ?? "").join(" ").trim();
      const last = results.at(-1);
      if (text) {
        onResult({
          text,
          language: "es-EC",
          provider: "browser-web-speech",
          isFinal: Boolean(last?.isFinal),
          confidence: last?.[0]?.confidence,
        });
      }
    };
    recognition.onerror = (event) => onError(`No se pudo transcribir: ${event.error}.`);
    this.recognition = recognition;
    recognition.start();
  }

  stop() {
    this.recognition?.stop();
  }

  cancel() {
    this.recognition?.abort();
    this.recognition = null;
  }
}

export class MockSpeechTranscriber implements SpeechTranscriber {
  private readonly fixture: string;

  constructor(fixture = "Vendí dos panes a cincuenta centavos cada uno") {
    this.fixture = fixture;
  }

  start(onResult: (result: TranscriptResult) => void, _onError: (message: string) => void) {
    onResult({ text: this.fixture, language: "es-EC", provider: "mock", isFinal: true });
  }

  stop() {}
  cancel() {}
}

const numericRiskPattern = /(?:\$|\d|centav|dólar|dolar|dos|doce|trece|treinta|quince|cincuenta|sesenta|setenta)/i;

export function hasNumericTranscriptRisk(text: string) {
  return numericRiskPattern.test(text);
}
