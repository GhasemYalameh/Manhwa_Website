import { HeroBanner } from "@/components/home/HeroBanner";
import { LatestUpdatesSection } from "@/components/home/LatestUpdatesSection";
import { TopThisWeekSection } from "@/components/home/TopThisWeekSection";
import { GenreTabsSection } from "@/components/home/GenreTabsSection";
import { getManhwas } from "@/lib/api/manhwa";
import { getGenres } from "@/lib/api/genre";

export default async function HomePage() {
  const [latestUpdates, heroCandidates, topThisWeek, genres] = await Promise.all([
    getManhwas({ ordering: "-publication_datetime" }),
    getManhwas({ ordering: "-avg_rating" }),
    getManhwas({ ordering: "-views_count" }),
    getGenres(),
  ]);
  return (
    <main className="min-h-screen bg-bg">
      <HeroBanner items={heroCandidates.results.slice(0, 5)} />
      <LatestUpdatesSection items={latestUpdates.results} />
      <TopThisWeekSection items={topThisWeek.results.slice(0, 5)} />
      <GenreTabsSection genres={genres} />
      {/* TODO: تازه اضافه‌شده‌ها، ادامه‌ی مطالعه */}
    </main>
  );
}