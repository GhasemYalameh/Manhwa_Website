"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { getManhwas, getCoverUrl, type ManhwaApiItem } from "@/lib/api/manhwa";
import { SearchIcon } from "@/components/icons";

interface SearchDropdownProps {
  variant?: "desktop" | "mobile";
  enableSlashShortcut?: boolean;
}

const DEBOUNCE_MS = 350;
const MAX_RESULTS = 5;
const MIN_QUERY_LENGTH = 2;

export function SearchDropdown({ variant = "desktop", enableSlashShortcut = false }: SearchDropdownProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ManhwaApiItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // دیبانس + فراخوانی API
  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < MIN_QUERY_LENGTH) {
      setResults([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    const timer = setTimeout(() => {
      getManhwas({ search: trimmed })
        .then((res) => setResults(res.results.slice(0, MAX_RESULTS)))
        .catch(() => setResults([]))
        .finally(() => setIsLoading(false));
    }, DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [query]);

  // بستن با کلیک بیرون
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // بستن با Escape
  useEffect(() => {
    function handleEscape(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setIsOpen(false);
        inputRef.current?.blur();
      }
    }
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, []);

  // میانبر "/" — فقط روی instance دسکتاپ فعال میشه (تا دوبار رجیستر نشه)
  useEffect(() => {
    if (!enableSlashShortcut) return;
    function handleKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement;
      const isTyping = target.tagName === "INPUT" || target.tagName === "TEXTAREA";
      if (e.key === "/" && !isTyping) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [enableSlashShortcut]);

  function handleSelect() {
    setIsOpen(false);
    setQuery("");
  }

  function handleSeeAll() {
    const trimmed = query.trim();
    if (trimmed.length < MIN_QUERY_LENGTH) return;
    setIsOpen(false);
    router.push(`/manhwa?search=${encodeURIComponent(trimmed)}`);
  }

  const showDropdown = isOpen && query.trim().length >= MIN_QUERY_LENGTH;

  return (
    <div ref={containerRef} className="relative">
      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary">
        <SearchIcon />
      </span>
      <input
        ref={inputRef}
        type="text"
        value={query}
        dir="auto"
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setIsOpen(true)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSeeAll();
        }}
        placeholder="جستجو کنید"
        className={`w-full rounded-card border border-divider bg-bg text-right text-sm text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent ${variant === "desktop" ? "py-2 pr-10 pl-10" : "py-2.5 pr-10 pl-4"
          }`}
      />
      {variant === "desktop" && (
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 rounded border border-divider px-1.5 py-0.5 text-xs text-text-secondary">
          /
        </span>
      )}

      {showDropdown && (
        <div className="absolute inset-x-0 top-full z-50 mt-2 max-h-80 overflow-y-auto rounded-card border border-divider bg-surface py-2 shadow-lg">
          {isLoading ? (
            <p className="px-4 py-3 text-sm text-text-secondary">در حال جستجو...</p>
          ) : results.length === 0 ? (
            <p className="px-4 py-3 text-sm text-text-secondary">نتیجه‌ای پیدا نشد.</p>
          ) : (
            results.map((item) => (
              <Link
                key={item.slug}
                href={`/manhwa/${item.slug}`}
                onClick={handleSelect}
                className="flex items-center gap-3 px-4 py-2 transition-colors hover:bg-accent-light"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={getCoverUrl(item.cover)}
                  alt={item.fa_title || item.en_title}
                  className="h-12 w-9 shrink-0 rounded object-cover"
                />
                <span dir="auto" className="truncate text-sm text-text-primary">
                  {item.fa_title || item.en_title}
                </span>
              </Link>
            ))
          )}

          {!isLoading && (
            <button
              type="button"
              onClick={handleSeeAll}
              className="mt-1 block w-full border-t border-divider px-4 py-2.5 text-center text-sm font-medium text-accent hover:bg-accent-light"
            >
              مشاهده همه‌ی نتایج
            </button>
          )}
        </div>
      )}
    </div>
  );
}
