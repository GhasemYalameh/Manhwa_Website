"use client";

import { useEffect, useRef, useState } from "react";
import { getAccessToken } from "@/lib/api/client";
import {
  getWatchList,
  addToWatchlist,
  updateWatchlistStatus,
  removeFromWatchlist,
  type WatchingStatus,
} from "@/lib/api/watchlist";
import { useToast } from "@/components/ui/Toast";
import { ChevronDownIcon } from "@/components/icons";

interface WatchlistButtonProps {
  manhwaSlug: string;
}

const STATUS_LABELS: Record<WatchingStatus, string> = {
  wr: "بعدا میخونم",
  nr: "در حال خواندن",
  st: "متوقف شده",
  fn: "تمام کردم",
};

const STATUS_ORDER: WatchingStatus[] = ["wr", "nr", "st", "fn"];

export function WatchlistButton({ manhwaSlug }: WatchlistButtonProps) {
  const { showToast } = useToast();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [entryId, setEntryId] = useState<number | null>(null);
  const [status, setStatus] = useState<WatchingStatus | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isBusy, setIsBusy] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loggedIn = !!getAccessToken();
    setIsLoggedIn(loggedIn);
    if (!loggedIn) return;

    getWatchList()
      .then((res) => {
        const existing = res.results.find((w) => w.manhwa.slug === manhwaSlug);
        if (existing) {
          setEntryId(existing.id);
          setStatus(existing.watching_status ?? null);
        }
      })
      .catch(() => { });
  }, [manhwaSlug]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleSelect(newStatus: WatchingStatus) {
    setIsBusy(true);
    try {
      if (entryId === null) {
        const created = await addToWatchlist(manhwaSlug, newStatus);
        setEntryId(created.id);
        setStatus(created.watching_status ?? newStatus);
      } else {
        await updateWatchlistStatus(entryId, newStatus);
        setStatus(newStatus);
      }
      showToast(`وضعیت به «${STATUS_LABELS[newStatus]}» تغییر کرد.`, "success");
    } catch {
      showToast("ثبت وضعیت با خطا مواجه شد. دوباره تلاش کنید.", "error");
    } finally {
      setIsBusy(false);
      setIsOpen(false);
    }
  }

  async function handleRemove() {
    if (entryId === null) return;
    setIsBusy(true);
    try {
      await removeFromWatchlist(entryId);
      setEntryId(null);
      setStatus(null);
      showToast("از لیست شما حذف شد.", "success");
    } catch {
      showToast("حذف با خطا مواجه شد. دوباره تلاش کنید.", "error");
    } finally {
      setIsBusy(false);
      setIsOpen(false);
    }
  }

  if (!isLoggedIn) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-text-secondary">وضعیت مطالعه:</span>

      <div ref={containerRef} className="relative">
        <button
          type="button"
          disabled={isBusy}
          onClick={() => setIsOpen((v) => !v)}
          className={`flex items-center gap-2 rounded-card border px-4 py-2.5 text-sm font-semibold transition-colors disabled:opacity-60 ${status
              ? "border-accent text-accent hover:bg-accent-light"
              : "border-divider text-text-primary hover:border-accent hover:text-accent"
            }`}
        >
          {status ? STATUS_LABELS[status] : "افزودن به لیست"}
          <ChevronDownIcon className={`transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </button>

        {isOpen && (
          <div className="absolute start-0 top-full z-50 mt-2 w-52 rounded-card border border-divider bg-surface py-2 shadow-lg">
            {STATUS_ORDER.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => handleSelect(s)}
                className={`flex w-full items-center justify-between px-4 py-2 text-right text-sm transition-colors hover:bg-accent-light ${status === s ? "font-semibold text-accent" : "text-text-primary"
                  }`}
              >
                {STATUS_LABELS[s]}
                {status === s && <span>✓</span>}
              </button>
            ))}
            {entryId !== null && (
              <>
                <div className="my-1 border-t border-divider" />
                <button
                  type="button"
                  onClick={handleRemove}
                  className="block w-full px-4 py-2 text-right text-sm text-error hover:bg-accent-light"
                >
                  حذف از لیست
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}