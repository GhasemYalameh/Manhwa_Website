import Link from "next/link";
import { StarIcon, FlameIcon } from "@/components/icons";

export interface MangaCardProps {
  slug: string; // lookup_field بک‌اند title_slug هست، نه id — لینک/href باید بر همین اساس ساخته بشه
  coverUrl: string;
  title: string;
  rating?: number; // avg_rating از سریالایزر
  lastUpload: string; // مثل "S01-E03" — رشته‌ست، نه عدد فصل
  // TODO: isNew و isHot فعلاً از بک‌اند نمیان؛ فیلدی برای این‌ها تو ManhwaSerializer نیست.
  // فعلاً با مقدار mock/الکی صدا زده میشن تا وقتی بک‌اند این فیلدها رو اضافه کنه.
  isNew?: boolean;
  isHot?: boolean;
  // TODO: ردیف «زمان نسبی» (مثل «۲ ساعت پیش») کنار lastUpload حذف شده چون
  // ManhwaSerializer فیلد timestamp برای آخرین آپدیت نداره. وقتی بک‌اند این فیلد رو
  // اضافه کرد (مثلاً last_upload_at)، این ردیف برگردونده بشه.
}

export function MangaCard({
  slug,
  coverUrl,
  title,
  rating,
  lastUpload,
  isNew,
  isHot,
}: MangaCardProps) {
  return (
    <Link href={`/manhwa/${slug}`} className="group block bg-surface rounded-card">
      <div className="relative aspect-[3/4] w-full overflow-hidden p-1 pb-0">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={coverUrl}
          alt={title}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105  rounded-t-card overflow-hidden backdrop-blur-lg"
        />

        {isHot && (
          <span className="absolute top-2 right-2 flex items-center gap-1 rounded-full bg-error px-2 py-0.5 text-[11px] font-bold text-white">
            <FlameIcon />
            داغ
          </span>
        )}

        {isNew && (
          <span className="absolute top-2 left-2 rounded-full bg-accent px-2 py-0.5 text-[11px] font-bold text-white">
            جدید
          </span>
        )}

        {typeof rating === "number" && (
          <span className="absolute bottom-3 left-3 flex gap-1 rounded-xl  pl-1 pr-2 pb-0.5 pt-1 text-[14px] font-semibold text-white bg-divider">
            {rating.toFixed(1)}
            <StarIcon className="text-warning" />

          </span>
        )}
      </div>
      <div className="p-3 pt-0">
        <h3
          className="mt-2 mb-4 truncate text-sm font-medium text-text-primary"
          title={title}
        >
          {title}
        </h3>

        <p className="mt-0.5 text-xs text-text-secondary">{lastUpload !== "Not Uploaded" ? lastUpload : "اپلود نشده"}</p>
      </div>

    </Link>
  );
}
