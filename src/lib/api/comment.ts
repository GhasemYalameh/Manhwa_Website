import { apiGet, apiPost } from "./client";
import type { PaginatedResponse } from "./manhwa";

export interface CommentAuthor {
  id: string;
  first_name: string;
  is_subscriber: boolean;
  avatar: string | null;
}

export type CommentReaction = "lk" | "dlk";

export interface CommentApiItem {
  id: number;
  manhwa_slug: string;
  author: CommentAuthor;
  text: string;
  parent: number | null;
  level: number;
  likes_count: number;
  dis_likes_count: number;
  replies_count: number;
  user_reaction: CommentReaction | null;
  is_spoiler: boolean;
}

export function getComments(
  manhwaSlug: string,
  page = 1
): Promise<PaginatedResponse<CommentApiItem>> {
  return apiGet<PaginatedResponse<CommentApiItem>>(
    `/api/manhwas/${manhwaSlug}/comments/?page=${page}`
  );
}

export function getComment(manhwaSlug: string, id: number): Promise<CommentApiItem> {
  return apiGet<CommentApiItem>(`/api/manhwas/${manhwaSlug}/comments/${id}/`);
}

export function getCommentReplies(
  manhwaSlug: string,
  commentId: number
): Promise<CommentApiItem[]> {
  return apiGet<CommentApiItem[]>(
    `/api/manhwas/${manhwaSlug}/comments/${commentId}/replies/`
  );
}

export interface CreateCommentResponse {
  id: number;
  author: CommentAuthor;
  text: string;
  parent: number | null;
  is_spoiler: boolean;
}

export function createComment(
  manhwaSlug: string,
  text: string,
  parent: number | null = null,
  isSpoiler = false
): Promise<CreateCommentResponse> {
  return apiPost<CreateCommentResponse>(
    `/api/manhwas/${manhwaSlug}/comments/`,
    { text, parent, is_spoiler: isSpoiler },
    { auth: true }
  );
}

export interface ReactionResponse {
  action: "created" | "updated" | "deleted";
  comment: { likes_count: number; dis_likes_count: number };
  reaction: { reaction: CommentReaction } | null;
}

export function toggleCommentReaction(
  manhwaSlug: string,
  commentId: number,
  reaction: CommentReaction
): Promise<ReactionResponse> {
  return apiPost<ReactionResponse>(
    `/api/manhwas/${manhwaSlug}/comments/${commentId}/reaction/`,
    { reaction },
    { auth: true }
  );
}