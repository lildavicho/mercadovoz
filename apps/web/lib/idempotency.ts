type CryptoSource = Pick<Crypto, "getRandomValues"> & Partial<Pick<Crypto, "randomUUID">>;

let fallbackSequence = 0;

/** Generate a request identifier on HTTPS and on the pilot's temporary HTTP mode. */
export function createIdempotencyKey(source: CryptoSource | undefined = globalThis.crypto): string {
  if (typeof source?.randomUUID === "function") {
    return source.randomUUID();
  }
  if (typeof source?.getRandomValues === "function") {
    const bytes = new Uint8Array(16);
    source.getRandomValues(bytes);
    return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
  }
  fallbackSequence += 1;
  return `fallback-${Date.now().toString(36)}-${fallbackSequence.toString(36)}-${Math.random().toString(36).slice(2)}`;
}
