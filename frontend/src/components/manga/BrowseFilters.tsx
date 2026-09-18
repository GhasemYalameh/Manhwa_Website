"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { GenreApiItem } from "@/lib/api/genre";
import type { StudioApiItem } from "@/lib/api/studio";

interface BrowseFiltersProps {
  genres: GenreApiItem[];
  studios: StudioApiItem[];
}

const DAY_OPTIONS = [
  { value: "", label: "همه‌ی روزها" },
  { value: "sat", label: "شنبه" },
  { value: "sun", label: "یکشنبه" },
  { value: "mon", label: "دوشنبه" },
  { value: "tue", label: "سه‌شنبه" },
  { value: "wed", label: "چهارشنبه" },
  { value: "thu", label: "پنج‌شنبه" },
  { value: "fri", label: "جمعه" },
];

const ORDER_OPTIONS = [
  { value: "-publication_datetime", label: "جدیدترین" },
  { value: "-avg_rating", label: "بیشترین امتیاز" },
  { value: "-views_count", label: "پربازدیدترین" },
];

const DEBOUNCE_MS = 400;

export function BrowseFilters({ genres, studios }: BrowseFiltersProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [search, setSearch] = useState(searchParams.get("search") ?? "");

  function updateParam(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.delete("page");
    router.push(`${pathname}?${params.toString()}`);
  }

  useEffect(() => {
    const current = searchParams.get("search") ?? "";
    if (search === current) return;
    const timer = setTimeout(() => updateParam("search", search), DEBOUNCE_MS);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  function handleReset() {
    setSearch("");
    router.push(pathname);
  }

  const hasActiveFilters =
    !!searchParams.get("search") ||
    !!searchParams.get("day_of_week") ||
    !!searchParams.get("genres") ||
    !!searchParams.get("studio");

  return (
    <div className="mb-6 flex flex-wrap items-center gap-3">
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="...جستجو در عنوان"
        dir="auto"
        className="w-full max-w-xs rounded-card border border-divider bg-bg px-3 py-2 text-sm text-right text-text-primary outline-none focus:border-accent"
      />

      <select
        value={searchParams.get("day_of_week") ?? ""}
        onChange={(e) => updateParam("day_of_week", e.target.value)}
        className="rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
      >
        {DAY_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>

      <select
        value={searchParams.get("genres") ?? ""}
        onChange={(e) => updateParam("genres", e.target.value)}
        className="rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
      >
        <option value="">همه‌ی ژانرها</option>
        {genres.map((g) => (
          <option key={g.id} value={g.id}>{g.title}</option>
        ))}
      </select>

      <select
        value={searchParams.get("studio") ?? ""}
        onChange={(e) => updateParam("studio", e.target.value)}
        className="rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
      >
        <option value="">همه‌ی استودیوها</option>
        {studios.map((s) => (
          <option key={s.id} value={s.id}>{s.title}</option>
        ))}
      </select>

      <select
        value={searchParams.get("ordering") ?? ORDER_OPTIONS[0].value}
        onChange={(e) => updateParam("ordering", e.target.value)}
        className="rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
      >
        {ORDER_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>

      {hasActiveFilters && (
        <button
          type="button"
          onClick={handleReset}
          className="rounded-card px-3 py-2 text-sm text-text-secondary hover:text-error"
        >
          پاک کردن فیلترها
        </button>
      )}
    </div>
  );
}
