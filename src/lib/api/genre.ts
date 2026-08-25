import { apiGet } from "./client";

const GENRE_PREFIX = "/api/genre";

export interface GenreApiItem {
  id: number;
  title: string;
  description: string;
}

export function getGenres(): Promise<GenreApiItem[]> {
  return apiGet<GenreApiItem[]>(`${GENRE_PREFIX}/`);
}