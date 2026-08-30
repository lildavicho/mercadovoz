import assert from "node:assert/strict";
import test from "node:test";

import { createIdempotencyKey } from "./idempotency.ts";

test("uses randomUUID exactly once when secure-context support exists", () => {
  let calls = 0;
  const source = {
    randomUUID: () => { calls += 1; return "00000000-0000-4000-8000-000000000001" as `${string}-${string}-${string}-${string}-${string}`; },
    getRandomValues: <T extends ArrayBufferView | null>(array: T) => array,
  };
  assert.equal(createIdempotencyKey(source), "00000000-0000-4000-8000-000000000001");
  assert.equal(calls, 1);
});

test("uses getRandomValues when randomUUID is unavailable over temporary HTTP", () => {
  const source = {
    getRandomValues: <T extends ArrayBufferView | null>(array: T) => {
      if (array instanceof Uint8Array) array.fill(10);
      return array;
    },
  };
  assert.equal(createIdempotencyKey(source), "0a".repeat(16));
});

test("last-resort keys remain distinct when Web Crypto is unavailable", () => {
  assert.notEqual(createIdempotencyKey(undefined), createIdempotencyKey(undefined));
});
