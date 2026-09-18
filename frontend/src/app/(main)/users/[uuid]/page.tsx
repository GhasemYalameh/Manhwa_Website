import { notFound } from "next/navigation";
import { getPublicProfile } from "@/lib/api/publicProfile";
import { ApiError } from "@/lib/api/client";
import { PublicProfileHeader } from "@/components/publicProfile/PublicProfileHeader";
import { ProfileStatsGrid } from "@/components/publicProfile/ProfileStatsGrid";
import { PublicCommentsList } from "@/components/publicProfile/PublicCommentsList";
import { PublicInterestedManhwas } from "@/components/publicProfile/PublicInterestedManhwas";

interface PublicProfilePageProps {
  params: Promise<{ uuid: string }>;
}

export default async function PublicProfilePage({ params }: PublicProfilePageProps) {
  const { uuid } = await params;

  let profile;
  try {
    profile = await getPublicProfile(uuid);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      notFound();
    }
    throw err;
  }

  return (
    <main className="min-h-screen bg-bg pb-12">
      <PublicProfileHeader profile={profile} />
      <ProfileStatsGrid profile={profile} />
      <PublicCommentsList comments={profile.last_comments} />
      <PublicInterestedManhwas items={profile.interested_manhwas} />
    </main>
  );
}
