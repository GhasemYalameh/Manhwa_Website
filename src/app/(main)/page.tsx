import { LatestUpdatesSection } from "@/components/home/LatestUpdatesSection";
import { getManhwas } from "@/lib/api/manhwa";

export default async function HomePage() {
  const latestUpdates = await getManhwas({ ordering: "-publication_datetime" });

  return (
    <main className="min-h-screen bg-bg">
      {/* TODO: بنر شاخص (Hero) — بخش بعدی */}
      <LatestUpdatesSection items={latestUpdates.results} />
      {/* TODO: پرطرفدارترین این هفته، ژانرها، تازه اضافه‌شده‌ها، ادامه‌ی مطالعه */}
    </main>
  );
}