import { apiGet } from "./client";
import type { PaginatedResponse } from "./manhwa";

export interface CommentAuthor {
  id: string;
  first_name: string;
  is_subscriber: boolean;
  avatar: string | null;
}

export interface CommentApiItem {
  id: number;
  author: CommentAuthor;
  text: string;
  parent: number | null;
  level: number;
  likes_count: number;
  dis_likes_count: number;
  replies_count: number;
  user_reaction: "lk" | "dlk" | null;
}

// فقط کامنت‌های سطح صفر (level 0) — فرم ارسال و ریپلای بعداً اضافه میشه
export function getComments(
  manhwaSlug: string,
  page = 1
): Promise<PaginatedResponse<CommentApiItem>> {
  return apiGet<PaginatedResponse<CommentApiItem>>(
    `/api/manhwas/${manhwaSlug}/comments/?page=${page}`
  );
}
