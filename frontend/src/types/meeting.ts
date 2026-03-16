export interface Attendee {
  id: number;
  meeting_id: number;
  email: string;
  name?: string | null;
  response_status?: string | null;
  notified_at?: string | null;
}

export interface ActionItem {
  id: number;
  meeting_id: number;
  text: string;
  assignee_email: string | null;
  due_date: string | null;
  status: string;
  priority?: string | null;
  completed: boolean;
  created_at: string;
}

export interface Meeting {
  id: number;
  title: string;
  start_time: string;
  end_time: string;
  calendar_id: string;
  external_id?: string | null;
  google_event_id: string | null;
  status: string;
  meet_url: string | null;
  recall_bot_id?: string | null;
  transcript: string | null;
  transcript_path: string | null;
  summary: string | null;
  summary_key_points: Record<string, unknown> | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  attendees: Attendee[];
  action_items: ActionItem[];
}

export interface MeetingCreate {
  title: string;
  start_time: string;
  end_time: string;
  calendar_id?: string;
  transcript?: string | null;
  notes?: string | null;
  google_event_id?: string | null;
  external_id?: string | null;
  status?: string;
  meet_url?: string | null;
}

export interface MeetingUpdate {
  title?: string;
  start_time?: string;
  end_time?: string;
  transcript?: string | null;
  notes?: string | null;
  status?: string;
  meet_url?: string | null;
}

export type MeetingStatus = "scheduled" | "live" | "completed" | "failed";
