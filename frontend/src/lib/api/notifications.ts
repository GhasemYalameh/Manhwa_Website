import { apiGet, apiPatch } from "./client";
import type { PaginatedResponse } from "./manhwa";
import type { ChapterDetailApiItem } from "./episode";
import type { CommentApiItem, CommentAuthor } from "./comment";

const NOTIFICATIONS_PREFIX = "/api/notifications";

export interface UnreadCountResponse {
  unread_count: number;
}

export function getUnreadNotificationsCount(): Promise<UnreadCountResponse> {
  return apiGet<UnreadCountResponse>(`${NOTIFICATIONS_PREFIX}/unread_count/`, { auth: true });
}

export type NotifLevel = "suc" | "inf" | "war" | "fal";
export type NotifType = "epp" | "rac" | "rpc" | "sys";

export interface NotificationApiItem {
  id: number;
  sender: CommentAuthor | null;
  target_content_type: "chapter" | "comment" | null;
  target_object: ChapterDetailApiItem | CommentApiItem | null;
  is_read: boolean;
  notif_level: NotifLevel;
  notif_type: NotifType;
  created_at: string;
}

export function getNotifications(page = 1): Promise<PaginatedResponse<NotificationApiItem>> {
  return apiGet<PaginatedResponse<NotificationApiItem>>(
    `${NOTIFICATIONS_PREFIX}/?page=${page}`,
    { auth: true }
  );
}

export function markNotificationRead(id: number): Promise<{ is_read: boolean }> {
  return apiPatch<{ is_read: boolean }>(
    `${NOTIFICATIONS_PREFIX}/${id}/`,
    { is_read: true },
    { auth: true }
  );
}