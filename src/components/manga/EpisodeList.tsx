"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { EpisodeApiItem } from "@/lib/api/episode";

interface EpisodeListProps {
  episodes: EpisodeApiItem[];
}

const PAGE_SIZE_OPTIONS = [24, 48, 96] as const;

export function EpisodeList({ episodes }: EpisodeListProps) {
  const [fromNumber, setFromNumber] = useState("");
  const [toNumber, setToNumber] = useState("");
  const [pageSize, setPageSize] = useState<number>(24);
  const [page, setPage] = useState(1);

  const sorted = useMemo(() => [...episodes].sort((a, b) => b.number - a.number), [episodes]);

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
          <div className="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-3">
            {pageItems.map((episode) => (
              <Link
                key={episode.id}
                href={episode.file}
                className="group flex flex-col overflow-hidden rounded-card bg-surface transition-colors hover:bg-accent-light"
              >
                {/* TODO: جای کاور اختصاصی اپیزود — فعلاً بلوک رنگی placeholder تا وقتی کاور واقعی اضافه بشه */}
                <div className="flex aspect-[3/4] items-center justify-center bg-accent-light text-2xl font-bold text-accent transition-colors group-hover:bg-accent group-hover:text-white">
                  {episode.number.toLocaleString("fa-IR")}
                </div>
                <div className="px-2 py-2 text-center text-xs text-text-secondary">
                  {new Date(episode.datetime_created).toLocaleDateString("fa-IR")}
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