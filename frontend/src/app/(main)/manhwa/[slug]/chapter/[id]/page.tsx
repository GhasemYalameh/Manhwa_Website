import { ChapterReader } from "@/components/manga/ChapterReader";

interface ChapterPageProps {
  params: Promise<{ slug: string; id: string }>;
}

export default async function ChapterPage({ params }: ChapterPageProps) {
  const { slug, id } = await params;
  return <ChapterReader slug={slug} chapterId={id} />;
}