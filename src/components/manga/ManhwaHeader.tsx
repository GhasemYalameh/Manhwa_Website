import Link from "next/link";
import { StarIcon, EyeIcon, CommentIcon, FlameSolidIcon } from "@/components/icons";
import { getCoverUrl, type ManhwaDetailApiItem } from "@/lib/api/manhwa";
import {
  PUBLICATION_STATUS_LABEL,
  PUBLICATION_STATUS_COLOR,
} from "@/lib/constants/publicationStatus";
import { WatchlistButton } from "@/components/manga/WatchlistButton";
import { RatingBreakdown } from "@/components/manga/RatingBreakdown";

interface ManhwaHeaderProps {
  slug: string;
  detail: ManhwaDetailApiItem;
}

const DAY_LABELS: Record<string, string> = {
  sat: "شنبه",
  sun: "یکشنبه",
  mon: "دوشنبه",
  tue: "سه‌شنبه",
  wed: "چهارشنبه",
  thu: "پنج‌شنبه",
  fri: "جمعه",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("fa-IR");
}

export function ManhwaHeader({ slug, detail }: ManhwaHeaderProps) {
  const rating = Number(detail.rating_data.avg_rating);

  return (
    <section className="mx-auto max-w-[1400px] px-4 pt-6 lg:px-8">
      {/* توجه: بدون flex-row-reverse — توی dir=rtl، اولین فرزند (کاور) خودش سمت راست میفته */}
      <div className="flex flex-col gap-6 md:flex-row">
        {/* کاور */}
        <div className="relative w-full shrink-0 md:w-64">
          <div className="aspect-[3/4] w-full overflow-hidden rounded-card">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={getCoverUrl(detail.cover)}
              alt={detail.fa_title || detail.en_title}
              className="h-full w-full object-cover"
            />
          </div>

          {detail.is_hot && (
            <span className="absolute top-1 left-2 flex h-9 w-9 items-center justify-center ">
              <FlameSolidIcon className="h-8 w-8 text-error" />
            </span>
          )}

          <span
            className={`absolute top-2 right-2 rounded-full px-2.5 py-1 text-[11px] font-bold text-white ${PUBLICATION_STATUS_COLOR[detail.publication_status]
              }`}
          >
            {PUBLICATION_STATUS_LABEL[detail.publication_status]}
          </span>
        </div>

        {/* اطلاعات */}
        <div className="flex flex-1 flex-col justify-center">
          <h1 className="text-2xl font-bold text-text-primary lg:text-3xl">
            {detail.fa_title || detail.en_title}
          </h1>
          {detail.fa_title && detail.en_title && (
            <p dir="ltr" className="mt-3 text-right text-sm text-text-secondary">
              {detail.en_title}
            </p>
          )}

          {detail.genres.length > 0 && (
            <div className="mt-8 flex flex-wrap gap-2">
              {detail.genres.map((genre) => (
                <Link
                  key={genre.id}
                  href={`/manhwa?genres=${genre.id}`}
                  className="rounded-full bg-accent-light px-3 py-1 text-xs font-medium text-accent transition-colors hover:bg-accent hover:text-white"
                >
                  {genre.title}
                </Link>
              ))}
            </div>
          )}

          <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-text-secondary">
            <span className="flex items-center gap-1">

              {detail.views_count.toLocaleString("fa-IR")}
              <EyeIcon />
            </span>

            <span className="flex items-center gap-1">

              {detail.comments_count.toLocaleString("fa-IR")}
              <CommentIcon />
            </span>

            <span>فصل {detail.season}</span>

            <span>روز پخش: {DAY_LABELS[detail.day_of_week] ?? detail.day_of_week}</span>

            <span>استودیو:  <Link href={`/manhwa?studio=${detail.studio.id}`} className="text-accent hover:underline">              {detail.studio.title}
            </Link>
            </span>
          </div>

          <div className="mt-2 flex flex-wrap gap-x-6 gap-y-1 text-xs text-text-secondary">
            <span>تاریخ انتشار: {formatDate(detail.publication_datetime)}</span>
            <span>
              آخرین آپلود:{" "}
              {detail.last_upload !== "Not Uploaded" ? detail.last_upload : "آپلود نشده"}
              {detail.last_upload !== "Not Uploaded" && ` (${formatDate(detail.last_upload_time)})`}
            </span>
          </div>
          <div className="mt-8 max-w-sm">
            <RatingBreakdown avgRating={rating} ratingData={detail.rating_data} />
          </div>
        </div>

      </div>

      {detail.summary && (
        <p className="mt-8 text-sm leading-7 text-text-secondary">{detail.summary}</p>
      )}

      <div className="mt-6 mb-10 flex flex-wrap justify-end items-center gap-3 pl-3">
        <WatchlistButton manhwaSlug={slug} />
        <Link
          href="#episodes"
          className="rounded-card bg-accent px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-dark"
        >
          شروع مطالعه
        </Link>

      </div>
    </section>
  );
}