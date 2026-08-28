import { apiGet, apiPost, apiPatch, apiDelete } from "./client";
import type { PaginatedResponse, ManhwaApiItem } from "./manhwa";

const WATCHLIST_PREFIX = "/api/watchlist";

export type WatchingStatus = "wr" | "nr" | "st" | "fn";

export interface WatchListApiItem {
  id: number;
  manhwa: ManhwaApiItem
  watching_status?: WatchingStatus;
}

export function getWatchList(): Promise<PaginatedResponse<WatchListApiItem>> {
  return apiGet<PaginatedResponse<WatchListApiItem>>(`${WATCHLIST_PREFIX}/`, { auth: true });
}

export function addToWatchlist(
  manhwaSlug: string,
  watchingStatus: WatchingStatus
): Promise<WatchListApiItem> {
  return apiPost<WatchListApiItem>(
    `${WATCHLIST_PREFIX}/`,
    { manhwa_slug: manhwaSlug, watching_status: watchingStatus },
    { auth: true }
  );
}

export function updateWatchlistStatus(
  id: number,
  watchingStatus: WatchingStatus
): Promise<{ watching_status: WatchingStatus }> {
  return apiPatch<{ watching_status: WatchingStatus }>(
    `${WATCHLIST_PREFIX}/${id}/`,
    { watching_status: watchingStatus },
    { auth: true }
  );
}

export function removeFromWatchlist(id: number): Promise<void> {
  return apiDelete(`${WATCHLIST_PREFIX}/${id}/`, { auth: true });
}