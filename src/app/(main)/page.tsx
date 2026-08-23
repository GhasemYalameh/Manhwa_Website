import { HeroBanner } from "@/components/home/HeroBanner";
import { LatestUpdatesSection } from "@/components/home/LatestUpdatesSection";
import { getManhwas } from "@/lib/api/manhwa";

export default async function HomePage() {
  const [latestUpdates, heroCandidates] = await Promise.all([
    getManhwas({ ordering: "-publication_datetime" }),
    getManhwas({ ordering: "-avg_rating" }),
  ]);
  return (
    <main className="min-h-screen bg-bg">
      <HeroBanner items={heroCandidates.results.slice(0, 5)} />
      <LatestUpdatesSection items={latestUpdates.results} />
      {/* TODO: پرطرفدارترین این هفته، ژانرها، تازه اضافه‌شده‌ها، ادامه‌ی مطالعه */}
    </main>
  );
}