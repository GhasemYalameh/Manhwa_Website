import { getCoverUrl } from "@/lib/api/manhwa";
import type { CommentApiItem } from "@/lib/api/comment";

interface CommentListProps {
  comments: CommentApiItem[];
  totalCount: number;
}

export function CommentList({ comments, totalCount }: CommentListProps) {
  return (
    <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-text-primary">
          نظرات <span className="text-text-secondary">({totalCount.toLocaleString("fa-IR")})</span>
        </h2>
      </div>

      {/* فرم ارسال کامنت + مکانیزم ریپلای بعداً اضافه میشه */}
      {comments.length === 0 ? (
        <p className="text-sm text-text-secondary">هنوز نظری ثبت نشده است.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {comments.map((comment) => (
            <li key={comment.id} className="rounded-card bg-surface p-4">
              <div className="flex items-center gap-2">
                {comment.author.avatar ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={getCoverUrl(comment.author.avatar)}
                    alt=""
                    className="h-8 w-8 rounded-full object-cover"
                  />
                ) : (
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent-light text-sm font-semibold text-accent">
                    {comment.author.first_name.charAt(0)}
                  </span>
                )}
                <span className="text-sm font-medium text-text-primary">
                  {comment.author.first_name}
                </span>
                {comment.author.is_subscriber && (
                  <span className="rounded-full bg-accent-light px-2 py-0.5 text-[11px] font-semibold text-accent">
                    مشترک
                  </span>
                )}
              </div>
              <p className="mt-2 text-sm text-text-primary">{comment.text}</p>
              <div className="mt-2 flex items-center gap-4 text-xs text-text-secondary">
                <span>{comment.likes_count} لایک</span>
                <span>{comment.dis_likes_count} دیس‌لایک</span>
                {comment.replies_count > 0 && <span>{comment.replies_count} پاسخ</span>}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
