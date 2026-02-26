export interface ActionItemCreate {
  meeting_id: number;
  text: string;
  assignee_email?: string | null;
  due_date?: string | null;
  status?: string;
  priority?: string | null;
}

export interface ActionItemUpdate {
  text?: string;
  assignee_email?: string | null;
  due_date?: string | null;
  status?: string;
  priority?: string | null;
  completed?: boolean;
}

export interface CalendarEvent {
  id: number;
  external_id?: string | null;
  title: string;
  start: string;
  end: string;
  status?: string;
  meet_url?: string | null;
}

export interface ChatQueryRequest {
  query: string;
  history?: Array<{ role: string; content: string }>;
}

export interface ChatQueryResponse {
  response: string;
  sources?: Array<{ title?: string; timestamp?: string }>;
}
