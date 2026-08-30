import assert from "node:assert/strict";
import test from "node:test";
import { isConfirmableProposal, reviewActionLabel } from "./confirmability.ts";
import type { Proposal } from "./types.ts";

function proposal(status: string, missingFields: string[] = []): Proposal {
  return {
    input_id: "input-1",
    proposal_id: "proposal-1",
    lifecycle_status: "PROPOSED",
    interpretation_status: status,
    operation: { type: "PAYMENT_RECEIVED", amount: 5 },
    question: "Revisa",
    warnings: [],
    missing_fields: missingFields,
    original_text: "Me abonó cinco",
    final_operation: null,
  };
}

test("only complete proposals without missing fields are confirmable", () => {
  assert.equal(isConfirmableProposal(proposal("COMPLETE")), true);
  for (const status of [
    "NEEDS_CONTEXT", "NEEDS_CONFIRMATION", "AMBIGUOUS", "UNSAFE",
    "OUT_OF_SCOPE", "UNRECOGNIZED", "COMPOUND_OPERATION",
  ]) {
    assert.equal(isConfirmableProposal(proposal(status)), false, status);
  }
  assert.equal(isConfirmableProposal(proposal("COMPLETE", ["customer"])), false);
});

test("incomplete proposals ask for information instead of confirmation", () => {
  assert.equal(reviewActionLabel("NEEDS_CONTEXT"), "Completar información");
  assert.equal(reviewActionLabel("NEEDS_CONFIRMATION"), "Completar información");
  assert.equal(reviewActionLabel("AMBIGUOUS"), "Corregir");
});
