export type OperationType = "SALE" | "EXPENSE" | "RECEIVABLE" | "PAYMENT_RECEIVED";

export interface Operation {
  type: OperationType | string;
  product?: string;
  quantity?: number;
  unit?: string;
  unit_price?: number | null;
  total?: number;
  category?: string;
  customer?: string;
  amount?: number;
  receivable_id?: string;
  settlement_role?: string;
  line_items?: Array<{
    line_item_id: string;
    product: string;
    quantity: number;
    unit: string;
    unit_price: number;
    total: number;
  }>;
}

export type BatchItemState =
  | "COMPLETE"
  | "NEEDS_CONFIRMATION"
  | "NEEDS_CONTEXT"
  | "AMBIGUOUS"
  | "COMPOUND_OPERATION"
  | "OUT_OF_SCOPE"
  | "UNSAFE"
  | "UNRECOGNIZED"
  | "REJECTED"
  | "CANCELLED";

export interface BatchSegment {
  segment_id: string;
  sequence: number;
  source_span: { start: number; end: number };
  source_text: string;
  state: BatchItemState;
  operation: Operation | null;
  fields_extracted: Record<string, unknown>;
  computed_fields: Record<string, unknown>;
  field_provenance: Record<string, { source: string; derived: boolean; formula?: string }>;
  context_used: Array<Record<string, unknown>>;
  warnings: string[];
  depends_on: string[];
  confirmable: boolean;
  lifecycle_status?: string;
}

export interface TransactionGroup {
  group_id: string;
  type: string;
  customer?: string;
  related_segment_ids: string[];
  derived_relationships: Array<Record<string, unknown>>;
}

export interface BatchInterpretation {
  batch_id: string;
  source_text: string;
  input_mode: "TEXT_SINGLE" | "TEXT_BATCH" | "VOICE_TRANSCRIPT";
  engine_version: string;
  underlying_engine_version: string;
  schema_version: string;
  segmenter_version: string;
  segments: BatchSegment[];
  groups: TransactionGroup[];
  warnings: string[];
  status: "READY" | "PARTIALLY_READY" | "NEEDS_REVIEW" | "BLOCKED";
  confirmable_item_ids: string[];
  latency_ms: number;
}

export interface BatchConfirmation {
  confirmation_id: string;
  batch_id: string;
  status: "PARTIALLY_CONFIRMED" | "CONFIRMED";
  confirmed_at: string;
  operations: StoredOperation[];
}

export interface Interpretation {
  input_id: string;
  interpretation_id: string;
  status: string;
  lifecycle_status: string | null;
  operation: Operation | null;
  question: string;
  warnings: string[];
  missing_fields: string[];
  original_text: string;
}

export interface Proposal {
  input_id: string;
  proposal_id: string;
  lifecycle_status: string;
  interpretation_status: string;
  operation: Operation;
  question: string;
  warnings: string[];
  missing_fields: string[];
  original_text: string;
  final_operation: Operation | null;
}

export interface StoredOperation {
  id: string;
  type: string;
  operation: Operation;
  original_text: string;
  confirmed_at: string;
  participant_id: string | null;
  session_id: string | null;
  input_id: string | null;
}

export interface PilotConfig {
  engine_version: string;
  parser_version: string;
  schema_version: string;
  pilot_version: string;
  ui_version: string;
  consent_version: string;
  field_validation_status: string;
  input_mode: "TEXT";
}

export interface PilotAccess {
  access_token: string;
  participant_id: string;
  expires_in_hours: number;
}

export interface PilotSession {
  id: string;
  participant_id: string;
  pilot_version: string;
  engine_version: string;
  started_at: string;
  ended_at: string | null;
  consent_version: string;
  device_class: string;
  input_mode: "TEXT";
  event_count: number;
}

export interface Receivable {
  id: string;
  customer_label: string;
  original_amount: number;
  balance: number;
  status: string;
}
