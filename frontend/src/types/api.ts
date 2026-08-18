export type Recording = {
  id: string;
  original_filename: string;
  stored_filename: string;
  content_type: string;
  size_bytes: number;
  status: "uploaded" | "transcribing" | "transcribed" | "failed";
  transcription_error?: string | null;
  transcription_started_at?: string | null;
  transcription_completed_at?: string | null;
  created_at: string;
};

export type RecordingListResponse = {
  items: Recording[];
};

export type TranscriptSegment = {
  id: string;
  segment_index: number;
  start_seconds: number;
  end_seconds: number;
  text: string;
  average_log_probability: number | null;
  no_speech_probability: number | null;
};

export type Transcript = {
  id: string;
  recording_id: string;
  text: string;
  language: string | null;
  model_name: string;
  duration_seconds: number | null;
  processing_seconds: number | null;
  created_at: string;
  segments: TranscriptSegment[];
};

export type ActionItem = {
  task: string;
  owner: string | null;
  due_date: string | null;
};

export type GeneratedNote = {
  id: string;
  transcript_id: string;
  summary: string;
  decisions: string[];
  action_items: ActionItem[];
  key_points: string[];
  follow_up_questions: string[];
  model_name: string;
  prompt_version: string;
  created_at: string;
};