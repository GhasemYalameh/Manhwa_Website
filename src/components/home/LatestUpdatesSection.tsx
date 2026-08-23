import { MangaCard } from "@/components/manga/MangaCard";
import { getCoverUrl, type ManhwaApiItem } from "@/lib/api/manhwa";

interface LatestUpdatesSectionProps {
  items: ManhwaApiItem[];
}

export function LatestUpdatesSection({ items }: LatestUpdatesSectionProps) {
  return (
    <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-text-primary">آخرین به‌روزرسانی‌ها</h2>
      </div>
      <div className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-4">
        {items.map((item) => (
          <MangaCard
            key={item.slug}
            slug={item.slug}
            coverUrl={getCoverUrl(item.cover)}
            title={item.fa_title || item.en_title}
            rating={item.avg_rating ? Number(item.avg_rating) : undefined}
            lastUpload={item.last_upload}
            // TODO: بک‌اند فیلدهای is_new/is_hot رو هنوز نداره؛ فعلاً مقدار ثابت.
            // وقتی این فیلدها به ManhwaSerializer اضافه شدن، این دو خط از item خونده بشن.
            isNew={false}
            isHot={false}
          />
        ))}
      </div>
    </section>
  );
}