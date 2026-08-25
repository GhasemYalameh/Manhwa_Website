import { apiGet } from "./client";

const NOTIFICATIONS_PREFIX = "/api/notifications";

export interface UnreadCountResponse {
  unread_count: number;
}

export function getUnreadNotificationsCount(): Promise<UnreadCountResponse> {
  return apiGet<UnreadCountResponse>(`${NOTIFICATIONS_PREFIX}/unread_count/`, { auth: true });
}
