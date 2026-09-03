import { apiGet } from "./client";

const STUDIO_PREFIX = "/api/studio";

export interface StudioApiItem {
  id: number;
  title: string;
  description: string;
}

// مشابه genre.ts — طبق تست واقعی، آرایه‌ی flat برمیگرده نه پیجینیت‌شده
export function getStudios(): Promise<StudioApiItem[]> {
  return apiGet<StudioApiItem[]>(`${STUDIO_PREFIX}/`);
}
