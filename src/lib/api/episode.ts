import { apiGet } from "./client";

export interface EpisodeApiItem {
  id: number;
  manhwa_slug: string;
  number: number;
  file: string;
  datetime_created: string;
}

// نیاز به احراز هویت — سایت اشتراکیه، بدون لاگین لیست چپترها برنمیگرده
export function getEpisodes(manhwaSlug: string): Promise<EpisodeApiItem[]> {
  return apiGet<EpisodeApiItem[]>(`/api/manhwas/${manhwaSlug}/chapters/`, { auth: true });
}

export interface ChapterImage {
  image_number: string;
  image_url: string;
}

export interface ChapterDetailApiItem {
  id: number;
  manhwa_slug: string;
  number: number;
  images: ChapterImage[];
  created_at: string;
}

// نیاز به احراز هویت
export function getChapterDetail(
  manhwaSlug: string,
  chapterId: number | string
): Promise<ChapterDetailApiItem> {
  return apiGet<ChapterDetailApiItem>(
    `/api/manhwas/${manhwaSlug}/chapters/${chapterId}/`,
    { auth: true }
  );
}