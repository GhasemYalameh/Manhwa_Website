import { apiGet, apiPost, apiPatch } from "./client";
import type { PaginatedResponse } from "./manhwa";

const TICKETS_PREFIX = "/api/tickets";

export type TicketStatus = "op" | "cl";
export type MessageSender = "user" | "admin";

export interface TicketUserRef {
  id: string;
  avatar: string | null;
  first_name: string;
  last_name: string;
}

export interface TicketApiItem {
  id: number;
  title: string;
  user: string | TicketUserRef; // uuid برای کاربر عادی، آبجکت کامل برای ادمین
  status: TicketStatus;
  is_seen: boolean;
  messages_count: number;
  created_at: string;
}

export function isTicketUserObject(user: TicketApiItem["user"]): user is TicketUserRef {
  return typeof user !== "string";
}

export interface GetTicketsParams {
  page?: number;
  ordering?: string; // "is_seen", "status", "created_at" (با پیشوند - برای نزولی)
}

export function getTickets(params: GetTicketsParams = {}): Promise<PaginatedResponse<TicketApiItem>> {
  const query = new URLSearchParams();
  query.set("page", String(params.page ?? 1));
  if (params.ordering) query.set("ordering", params.ordering);
  return apiGet<PaginatedResponse<TicketApiItem>>(`${TICKETS_PREFIX}/?${query.toString()}`, {
    auth: true,
  });
}

export function getTicket(ticketId: number): Promise<TicketApiItem> {
  return apiGet<TicketApiItem>(`${TICKETS_PREFIX}/${ticketId}/`, { auth: true });
}

export function createTicket(text: string, title?: string): Promise<TicketApiItem> {
  return apiPost<TicketApiItem>(
    `${TICKETS_PREFIX}/`,
    { text, ...(title ? { title } : {}) },
    { auth: true }
  );
}

// فقط برای ادمین معتبره — بک‌اند خودش دسترسی رو کنترل می‌کنه
export interface UpdateTicketPayload {
  status?: TicketStatus;
  is_seen?: boolean;
}

export function updateTicket(
  ticketId: number,
  payload: UpdateTicketPayload
): Promise<TicketApiItem> {
  return apiPatch<TicketApiItem>(`${TICKETS_PREFIX}/${ticketId}/`, payload, { auth: true });
}

export interface TicketMessage {
  id: number;
  user: string | TicketUserRef;
  text: string;
  message_sender: MessageSender;
  created_at: string;
  modified_at: string;
}

export function getTicketMessages(
  ticketId: number,
  page = 1
): Promise<PaginatedResponse<TicketMessage>> {
  return apiGet<PaginatedResponse<TicketMessage>>(
    `${TICKETS_PREFIX}/${ticketId}/messages/?page=${page}`,
    { auth: true }
  );
}

export interface CreateTicketMessageResponse {
  id: number;
  text: string;
  message_sender: MessageSender;
  created_at: string;
}

export function sendTicketMessage(
  ticketId: number,
  text: string
): Promise<CreateTicketMessageResponse> {
  return apiPost<CreateTicketMessageResponse>(
    `${TICKETS_PREFIX}/${ticketId}/messages/`,
    { text },
    { auth: true }
  );
}