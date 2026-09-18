import { MangaCard } from "@/components/manga/MangaCard";
import { getCoverUrl, type ManhwaApiItem } from "@/lib/api/manhwa";

interface LatestUpdatesSectionProps {
  items: ManhwaApiItem[];
  title?: string;
}

export function LatestUpdatesSection({ items, title = "آخرین به‌روزرسانی‌ها" }: LatestUpdatesSectionProps) {
  return (
    <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-text-primary">{title}</h2>
      </div>
      <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-4">
        {items.map((item) => (
          <MangaCard
            key={item.slug}
            slug={item.slug}
            coverUrl={getCoverUrl(item.cover)}
            title={item.fa_title || item.en_title}
            rating={item.avg_rating ? Number(item.avg_rating) : undefined}
            lastUpload={item.last_upload}
            viewsCount={item.views_count}
            commentsCount={item.comments_count}
            isHot={item.is_hot}
            publicationStatus={item.publication_status}
          />
        ))}
      </div>
    </section>
  );
}