"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { getAccessToken, ApiError, apiGetBlob } from "@/lib/api/client";
import { getChapterDetail, getEpisodes, type ChapterDetailApiItem } from "@/lib/api/episode";

interface ChapterReaderProps {
  slug: string;
  chapterId: string;
}

const PRELOAD_MARGIN = "800px";

function LazyPage({ url, index }: { url: string; index: number }) {
  const [isVisible, setIsVisible] = useState(false);
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: PRELOAD_MARGIN }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!isVisible) return;
    let cancelled = false;
    let createdUrl: string | null = null;

    apiGetBlob(url, { auth: true })
      .then((blob) => {
        if (cancelled) return;
        createdUrl = URL.createObjectURL(blob);
        setObjectUrl(createdUrl);
      })
      .catch(() => {
        if (!cancelled) setHasError(true);
      });

    return () => {
      cancelled = true;
      if (createdUrl) URL.revokeObjectURL(createdUrl);
    };
  }, [isVisible, url]);

  return (
    <div ref={ref} className="w-full">
      {objectUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={objectUrl}
          alt={`صفحه ${index + 1}`}
          draggable={false}
          onContextMenu={(e) => e.preventDefault()}
          className="block w-full select-none"
        />
      ) : hasError ? (
        <div className="flex aspect-[2/3] w-full items-center justify-center bg-surface text-xs text-text-secondary">
          خطا در بارگذاری تصویر
        </div>
      ) : (
        <div className="aspect-[2/3] w-full animate-pulse bg-surface" />
      )}
    </div>
  );
}

export function ChapterReader({ slug, chapterId }: ChapterReaderProps) {
  const [chapter, setChapter] = useState<ChapterDetailApiItem | null>(null);
  const [prevEpisodeId, setPrevEpisodeId] = useState<number | null>(null);
  const [nextEpisodeId, setNextEpisodeId] = useState<number | null>(null);
  const [status, setStatus] = useState<"loading" | "unauthorized" | "forbidden" | "notfound" | "ready">(
    "loading"
  );

  useEffect(() => {
    if (!getAccessToken()) {
      setStatus("unauthorized");
      return;
    }
    let cancelled = false;

    Promise.all([getChapterDetail(slug, chapterId), getEpisodes(slug)])
      .then(([chapterRes, episodesList]) => {
        if (cancelled) return;
        setChapter(chapterRes);

        const sorted = [...episodesList].sort((a, b) => a.number - b.number);
        const currentIndex = sorted.findIndex((e) => e.id === chapterRes.id);
        setPrevEpisodeId(currentIndex > 0 ? sorted[currentIndex - 1].id : null);
        setNextEpisodeId(
          currentIndex >= 0 && currentIndex < sorted.length - 1 ? sorted[currentIndex + 1].id : null
        );

        // چک سطح چپتر — قبل از رندر هیچ تصویری، اگه اشتراک کافی نیست پیام یکبار نشون داده بشه
        setStatus(chapterRes.is_accessible ? "ready" : "forbidden");
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          setStatus("unauthorized");
        } else if (err instanceof ApiError && err.status === 403) {
          setStatus("forbidden");
        } else {
          setStatus("notfound");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [slug, chapterId]);

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg">
        <p className="text-sm text-text-secondary">در حال بارگذاری...</p>
      </div>
    );
  }

  if (status === "unauthorized") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg px-4 text-center">
        <p className="text-text-primary">برای خواندن این قسمت باید وارد حساب کاربری شوید.</p>
        <Link
          href="/login"
          className="rounded-card bg-accent px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-dark"
        >
          ورود
        </Link>
      </div>
    );
  }

  if (status === "forbidden") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg px-4 text-center">
        <p className="text-text-primary">برای خواندن این قسمت نیاز به اشتراک فعال دارید.</p>
        <Link
          href="/profile"
          className="rounded-card bg-accent px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-dark"
        >
          خرید اشتراک
        </Link>
        <Link
          href={`/manhwa/${slug}`}
          className="text-sm text-text-secondary hover:text-accent"
        >
          بازگشت به صفحه‌ی مانهوا
        </Link>
      </div>
    );
  }

  if (status === "notfound" || !chapter) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg px-4 text-center">
        <p className="text-text-primary">این قسمت پیدا نشد.</p>
        <Link
          href={`/manhwa/${slug}`}
          className="rounded-card border border-divider px-5 py-2.5 text-sm text-text-primary hover:border-accent hover:text-accent"
        >
          بازگشت به صفحه‌ی مانهوا
        </Link>
      </div>
    );
  }

  const sortedImages = [...chapter.images].sort(
    (a, b) => Number(a.image_number) - Number(b.image_number)
  );

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col bg-black" style={{ userSelect: "none" }}>
      <div className="sticky top-0 z-10 flex items-center justify-between bg-surface px-4 py-3">
        <Link href={`/manhwa/${slug}`} className="text-sm text-text-secondary hover:text-accent">
          بازگشت
        </Link>
        <span className="text-sm font-semibold text-text-primary">
          قسمت {chapter.number.toLocaleString("fa-IR")}
        </span>
        <span className="w-12" />
      </div>

      <div className="flex flex-1 flex-col">
        {sortedImages.map((img, index) => (
          <LazyPage key={img.image_number} url={img.image_url} index={index} />
        ))}
      </div>

      <div className="flex items-center justify-between gap-3 bg-surface px-4 py-4">
        {prevEpisodeId ? (
          <Link
            href={`/manhwa/${slug}/chapter/${prevEpisodeId}`}
            className="rounded-card border border-divider px-4 py-2.5 text-sm text-text-primary hover:border-accent hover:text-accent"
          >
            قسمت قبلی
          </Link>
        ) : (
          <span />
        )}
        {nextEpisodeId ? (
          <Link
            href={`/manhwa/${slug}/chapter/${nextEpisodeId}`}
            className="rounded-card bg-accent px-4 py-2.5 text-sm font-semibold text-white hover:bg-accent-dark"
          >
            قسمت بعدی
          </Link>
        ) : (
          <span />
        )}
      </div>
    </div>
  );
}