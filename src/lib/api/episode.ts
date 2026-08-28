import { apiGet } from "./client";

export interface EpisodeApiItem {
  id: number;
  manhwa_slug: string;
  number: number;
  file: string;
  datetime_created: string;
}

// آرایه‌ی ساده، بدون pagination (طبق مستندات) — مرتب‌شده صعودی بر اساس number
export function getEpisodes(manhwaSlug: string): Promise<EpisodeApiItem[]> {
  return apiGet<EpisodeApiItem[]>(`/api/manhwas/${manhwaSlug}/episodes/`);
}
