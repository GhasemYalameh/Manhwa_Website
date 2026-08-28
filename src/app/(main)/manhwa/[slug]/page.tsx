import { notFound } from "next/navigation";
import { getManhwaBySlug } from "@/lib/api/manhwa";
import { getComments } from "@/lib/api/comment";
import { ManhwaHeader } from "@/components/manga/ManhwaHeader";
import { EpisodeList } from "@/components/manga/EpisodeList";
import { CommentList } from "@/components/manga/CommentList";
import { ApiError } from "@/lib/api/client";

interface ManhwaDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function ManhwaDetailPage({ params }: ManhwaDetailPageProps) {
  const { slug } = await params;

  let detailResult;
  try {
    detailResult = await Promise.all([
      getManhwaBySlug(slug),
      getComments(slug),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      notFound();
    }
    throw err;
  }

  const [detail, commentsRes] = detailResult;

  return (
    <main className="min-h-screen bg-bg pb-12">
      <ManhwaHeader slug={slug} detail={detail} />
      <EpisodeList manhwaSlug={slug} />
      <CommentList comments={commentsRes.results} totalCount={commentsRes.count} />
    </main>
  );
}