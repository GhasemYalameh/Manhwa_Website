"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { getAccessToken } from "@/lib/api/client";
import { getEpisodes, type EpisodeApiItem } from "@/lib/api/episode";
import { getCoverUrl } from "@/lib/api/manhwa";
import { LockIcon } from "@/components/icons";

interface EpisodeListProps {
  manhwaSlug: string;
}

const PAGE_SIZE_OPTIONS = [24, 48, 96] as const;

export function EpisodeList({ manhwaSlug }: EpisodeListProps) {
  const [episodes, setEpisodes] = useState<EpisodeApiItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  const [fromNumber, setFromNumber] = useState("");
  const [toNumber, setToNumber] = useState("");
  const [pageSize, setPageSize] = useState<number>(24);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const loggedIn = !!getAccessToken();
    setIsLoggedIn(loggedIn);
    setHasCheckedAuth(true);
    if (!loggedIn) {
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    getEpisodes(manhwaSlug)
      .then((res) => {
        if (!cancelled) setEpisodes(res);
      })
      .catch(() => {
        if (!cancelled) setEpisodes([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [manhwaSlug]);

  // const sorted = useMemo(() => [...episodes].sort((a, b) => b.number - a.number), [episodes]);
  const sorted = useMemo(() => [...episodes].sort((a, b) => a.number - b.number), [episodes]);

  const filtered = useMemo(() => {
    const from = fromNumber ? Number(fromNumber) : null;
    const to = toNumber ? Number(toNumber) : null;
    return sorted.filter((ep) => {
      if (from !== null && ep.number < from) return false;
      if (to !== null && ep.number > to) return false;
      return true;
    });
  }, [sorted, fromNumber, toNumber]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const pageItems = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  function handleRangeChange(setter: (v: string) => void) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setter(e.target.value);
      setPage(1);
    };
  }

  if (!hasCheckedAuth || isLoading) {
    return (
      <section id="episodes" className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
        <p className="text-sm text-text-secondary">در حال بارگذاری قسمت‌ها...</p>
      </section>
    );
  }

  if (!isLoggedIn) {
    return (
      <section id="episodes" className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
        <h2 className="text-lg font-bold text-text-primary">قسمت‌ها</h2>
        <div className="mt-4 rounded-card bg-surface p-6 text-center">
          <p className="text-sm text-text-secondary">
            برای مشاهده‌ی قسمت‌ها ابتدا وارد حساب کاربری خود شوید.
          </p>
          <Link
            href="/login"
            className="mt-3 inline-block rounded-card bg-accent px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-dark"
          >
            ورود
          </Link>
        </div>
      </section>
    );
  }
  
  return (
    <section id="episodes" className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-bold text-text-primary">
          قسمت‌ها <span className="text-text-secondary">({episodes.length.toLocaleString("fa-IR")})</span>
        </h2>

        <div className="flex flex-wrap items-center gap-2 text-sm">
          <input
            type="number"
            inputMode="numeric"
            placeholder="از"
            value={fromNumber}
            onChange={handleRangeChange(setFromNumber)}
            className="w-20 rounded-card border border-divider bg-bg px-2 py-1.5 text-center text-text-primary outline-none focus:border-accent"
          />
          <span className="text-text-secondary">تا</span>
          <input
            type="number"
            inputMode="numeric"
            placeholder="تا"
            value={toNumber}
            onChange={handleRangeChange(setToNumber)}
            className="w-20 rounded-card border border-divider bg-bg px-2 py-1.5 text-center text-text-primary outline-none focus:border-accent"
          />
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="rounded-card border border-divider bg-bg px-2 py-1.5 text-text-primary outline-none focus:border-accent"
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size.toLocaleString("fa-IR")} تا در صفحه
              </option>
            ))}
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="text-sm text-text-secondary">قسمتی با این بازه پیدا نشد.</p>
      ) : (
        <>
          <div className="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] content-end gap-3">
            {pageItems.map((episode) => (
              <Link
                key={episode.id}
                href={`/manhwa/${manhwaSlug}/chapter/${episode.id}`}
                className={`group flex flex-col overflow-hidden rounded-card bg-surface transition-colors ${episode.is_accessible ? "hover:bg-accent-light" : ""
                  }`}
              >
                <div
                  className={`relative flex aspect-[3/4] items-center justify-center overflow-hidden text-2xl font-bold transition-colors ${episode.cover
                    ? "bg-bg"
                    : episode.is_accessible
                      ? "bg-accent-light text-accent group-hover:bg-accent group-hover:text-white"
                      : "bg-accent-light/40 text-text-secondary/50"
                    }`}
                >
                  {episode.cover ? (
                    <>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={getCoverUrl(episode.cover)}
                        alt={`قسمت ${episode.number}`}
                        className={`h-full w-full object-cover transition-transform duration-300 ${episode.is_accessible ? "group-hover:scale-105" : "brightness-50"
                          }`}
                      />
                      <span className="absolute inset-x-0 bottom-0 bg-black/60 py-1 text-center text-sm text-white">
                        {new Date(episode.created_at).toLocaleDateString("fa-IR")}
                      </span>
                    </>
                  ) : (
                    new Date(episode.created_at).toLocaleDateString("fa-IR")
                  )}
                  {!episode.is_accessible && (
                    <span className="absolute inset-0 flex items-center justify-center bg-black/45">
                      <LockIcon className="h-6 w-6 text-white" />
                    </span>
                  )}
                </div>
                <div className="px-2 py-2 text-center text-s font-semibold text-text-secondary">
                  {episode.number.toLocaleString("fa-IR")}
                </div>
              </Link>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                type="button"
                disabled={currentPage === 1}
                onClick={() => setPage((p) => p - 1)}
                className="rounded-card border border-divider px-3 py-1.5 text-sm text-text-primary disabled:opacity-40"
              >
                قبلی
              </button>
              <span className="text-sm text-text-secondary">
                {currentPage.toLocaleString("fa-IR")} از {totalPages.toLocaleString("fa-IR")}
              </span>
              <button
                type="button"
                disabled={currentPage === totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-card border border-divider px-3 py-1.5 text-sm text-text-primary disabled:opacity-40"
              >
                بعدی
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}