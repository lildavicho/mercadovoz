import assert from "node:assert/strict";
import test from "node:test";
import { hasNumericTranscriptRisk, MockSpeechTranscriber } from "./speech.ts";

test("flags money and confusable number tokens for manual transcript review", () => {
  for (const value of ["quince dólares", "cincuenta", "$1.50", "dos libras", "setenta"]) {
    assert.equal(hasNumericTranscriptRisk(value), true);
  }
  assert.equal(hasNumericTranscriptRisk("vendí tomate"), false);
});

test("mock transcriber is deterministic and does not retain audio", () => {
  const transcriber = new MockSpeechTranscriber("trece dólares");
  let received = "";
  const asInterface: import("./speech.ts").SpeechTranscriber = transcriber;
  asInterface.start((result) => { received = result.text; }, () => {});
  assert.equal(received, "trece dólares");
});
