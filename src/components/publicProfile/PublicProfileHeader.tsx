import { getCoverUrl } from "@/lib/api/manhwa";
import { formatMembershipDuration } from "@/lib/utils/membership";
import type { PublicProfileApiItem } from "@/lib/api/publicProfile";

interface PublicProfileHeaderProps {
  profile: PublicProfileApiItem;
}

export function PublicProfileHeader({ profile }: PublicProfileHeaderProps) {
  return (
    <section className="mx-auto max-w-[1400px] px-4 pt-8 lg:px-8">
      <div className="flex flex-col items-center gap-4 rounded-card bg-surface p-6 sm:flex-row sm:items-center">
        {profile.avatar ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={getCoverUrl(profile.avatar)}
            alt=""
            className="h-20 w-20 shrink-0 rounded-full object-cover"
          />
        ) : (
          <span className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-accent-light text-2xl font-semibold text-accent">
            {profile.first_name.charAt(0) || "?"}
          </span>
        )}

        <div className="flex flex-1 flex-col items-center gap-1 sm:items-start">
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-text-primary">{profile.first_name}</h1>
            {profile.is_subscriber && (
              <span className="rounded-full bg-accent-light px-2.5 py-0.5 text-[11px] font-semibold text-accent">
                مشترک
              </span>
            )}
          </div>
          <p className="text-sm text-text-secondary">
            عضو شده از {formatMembershipDuration(profile.date_joined)} پیش
          </p>
          {profile.bio && (
            <p dir="auto" className="mt-2 max-w-xl text-sm text-text-primary">
              {profile.bio}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
