export type OperationType = "SALE" | "EXPENSE" | "RECEIVABLE" | "PAYMENT_RECEIVED";

export interface Operation {
  type: OperationType | string;
  product?: string;
  quantity?: number;
  unit?: string;
  unit_price?: number;
  total?: number;
  category?: string;
  customer?: string;
  amount?: number;
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
