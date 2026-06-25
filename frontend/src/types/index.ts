export type Severity = 'LOW' | 'MEDIUM' | 'HIGH';
export type SemaphoreStatus = 'GREEN' | 'YELLOW' | 'RED';
export type ValidationStatus = 'APPROVED' | 'SUSPICIOUS' | 'REJECTED';

export interface Flag {
  layer: string;
  finding: string;
  severity: Severity;
  weight: number;
}

export interface ValidationDetails {
  producer: string | null;
  creator: string | null;
  creation_date: string | null;
  mod_date: string | null;
  pages: number | null;
  has_incremental_updates: boolean;
  incremental_update_count: number;
  suspicious_objects: string[];
  fonts: string[];
  images_count: number;
  images_without_metadata: number;
}

export interface ValidationResult {
  filename: string;
  status: ValidationStatus;
  semaphore: SemaphoreStatus;
  score: number;
  verdict: string;
  flags: Flag[];
  details: ValidationDetails;
  processed_at: string;
}

export interface ValidateResponse {
  result: ValidationResult;
  report_available: boolean;
}

export interface ValidationError {
  error: string;
  detail?: string;
  timestamp: string;
}