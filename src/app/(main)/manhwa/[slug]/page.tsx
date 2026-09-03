import { notFound } from "next/navigation";
import { getManhwaBySlug } from "@/lib/api/manhwa";
import { getComments } from "@/lib/api/comment";
import { ManhwaHeader } from "@/components/manga/ManhwaHeader";
import { EpisodeList } from "@/components/manga/EpisodeList";
import { CommentList } from "@/components/manga/CommentList";
import { ApiError } from "@/lib/api/client";

interface ManhwaDetailPageProps {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ highlightComment?: string }>;
}

export default async function ManhwaDetailPage({ params, searchParams }: ManhwaDetailPageProps) {
  const { slug } = await params;
  const { highlightComment } = await searchParams;

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
      <CommentList
        manhwaSlug={slug}
        initialComments={commentsRes.results}
        initialCount={commentsRes.count}
        highlightCommentId={highlightComment ? Number(highlightComment) : undefined}
      />
    </main>
  );
}