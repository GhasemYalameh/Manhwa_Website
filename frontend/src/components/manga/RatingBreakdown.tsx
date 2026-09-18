import { StarIcon } from "@/components/icons";
import type { ManhwaDetailApiItem } from "@/lib/api/manhwa";

interface RatingBreakdownProps {
  avgRating: number;
  ratingData: ManhwaDetailApiItem["rating_data"];
}

const STARS = [5, 4, 3, 2, 1] as const;

export function RatingBreakdown({ avgRating, ratingData }: RatingBreakdownProps) {
  const counts: Record<number, number> = {
    5: ratingData.fives_count,
    4: ratingData.fours_count,
    3: ratingData.threes_count,
    2: ratingData.twos_count,
    1: ratingData.ones_count,
  };
  const maxCount = Math.max(...Object.values(counts), 1);
  const starFillPercent = Math.max(0, Math.min(100, (avgRating / 5) * 100));

  return (
    <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
      {/* میانگین امتیاز */}
      <div className="flex shrink-0 flex-col items-center sm:items-start">
        <span className="text-5xl font-extrabold text-text-primary">{avgRating.toFixed(1)}</span>
        <div className="relative mt-1 flex" style={{ width: "5.5rem" }}>
          <div className="flex gap-0.5 text-divider">
            {STARS.map((s) => (
              <StarIcon key={s} className="h-4 w-4" />
            ))}
          </div>
          <div
            className="absolute inset-0 flex gap-0.5 overflow-hidden text-warning"
            style={{ width: `${starFillPercent}%` }}
          >
            {STARS.map((s) => (
              <StarIcon key={s} className="h-4 w-4 shrink-0" />
            ))}
          </div>
        </div>
        <span className="mt-1 text-sm text-text-secondary">
          {ratingData.raters_count.toLocaleString("fa-IR")} رأی
        </span>
      </div>

      {/* میله‌های توزیع */}
      <div className="flex flex-1 flex-col gap-1.5">
        {STARS.map((star) => {
          const count = counts[star];
          const percent = (count / maxCount) * 100;
          return (
            <div key={star} className="flex items-center gap-2 text-xs text-text-secondary">
              <span className="w-3 shrink-0 text-center">{star}</span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-divider">
                <div
                  className="h-full rounded-full bg-accent"
                  style={{ width: count > 0 ? `${percent}%` : "0%" }}
                />
              </div>
              <span className="w-8 shrink-0 text-left text-text-secondary">
                {count.toLocaleString("fa-IR")}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}