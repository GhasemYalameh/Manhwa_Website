"use client";

import { useEffect, useState } from "react";
import { timeAgo } from "@/lib/utils/time";
import Link from "next/link";
import { getMyComments, type MyCommentApiItem } from "@/lib/api/comment";
import { ThumbsUpIcon, ThumbsDownIcon, ReplyIcon } from "@/components/icons";


export function MyCommentsSection() {
  const [comments, setComments] = useState<MyCommentApiItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getMyComments()
      .then(setComments)
      .catch(() => setComments([]))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <h2 className="mb-4 text-lg font-bold text-text-primary">کامنت‌های من</h2>

      {isLoading ? (
        <p className="text-sm text-text-secondary">در حال بارگذاری...</p>
      ) : comments.length === 0 ? (
        <p className="text-sm text-text-secondary">شما هنوز کامنتی ثبت نکرده‌اید.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {comments.map((comment) => (
            <li key={comment.id} className="rounded-card bg-surface p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Link
                  href={`/manhwa/${comment.manhwa.title_slug}?highlightComment=${comment.id}`}
                  className="text-sm font-semibold text-accent hover:underline"
                  dir="auto"
                >
                  {comment.manhwa.fa_title || comment.manhwa.en_title}
                </Link>
                <span className="text-xs text-text-secondary">{timeAgo(comment.created_at)}</span>
              </div>

              <p dir="auto" className="mt-2 text-sm text-text-primary">
                {comment.text}
              </p>

              <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-text-secondary">
                {comment.is_spoiler && (
                  <span className="rounded-full bg-warning/15 px-2 py-0.5 font-semibold text-warning">
                    اسپویل
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <ThumbsUpIcon className="h-3.5 w-3.5" />
                  {comment.likes_count.toLocaleString("fa-IR")}
                </span>
                <span className="flex items-center gap-1">
                  <ThumbsDownIcon className="h-3.5 w-3.5" />
                  {comment.dis_likes_count.toLocaleString("fa-IR")}
                </span>
                {comment.replies_count > 0 && (
                  <span className="flex items-center gap-1">
                    <ReplyIcon className="h-3.5 w-3.5" />
                    {comment.replies_count.toLocaleString("fa-IR")} پاسخ
                  </span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
