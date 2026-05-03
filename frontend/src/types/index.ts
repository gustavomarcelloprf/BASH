export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

export interface Project {
  id: number;
  name: string;
  budget_hours: number;
  status: string;
}

export interface TimeEntry {
  id: number;
  project_id: number;
  user_id: number;
  date: string;
  hours: number;
  activity: string | null;
  source: string;
  created_at: string;
}

export interface ParseResult {
  hours: number | null;
  project: string | null;
  date: string;
  activity: string | null;
  confidence: number;
  source: string;
  clarification_needed?: string;
}

export interface DashboardSummary {
  total_hours: number;
  active_projects: number;
  roi_hours_saved: number;
  roi_cost_saved: number;
}

export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  hours_this_month: number;
}

export interface RoiData {
  since: string | null;
  total_entries_automated: number;
  total_hours_saved: number;
  total_cost_saved: number;
  avg_minutes_per_entry_manual: number;
}
