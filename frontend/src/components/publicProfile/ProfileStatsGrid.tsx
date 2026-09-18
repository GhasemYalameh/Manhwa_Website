import { CheckCircleIcon, BookOpenIcon, ClockIcon, CommentIcon, StarIcon } from "@/components/icons";
import type { PublicProfileApiItem } from "@/lib/api/publicProfile";

interface ProfileStatsGridProps {
  profile: PublicProfileApiItem;
}

export function ProfileStatsGrid({ profile }: ProfileStatsGridProps) {
  const stats = [
    { icon: <CheckCircleIcon className="h-8 w-8 text-accent" />, label: "تمام‌شده", value: profile.finished_manhwa_count },
    { icon: <BookOpenIcon className="h-8 w-8 text-accent" />, label: "در حال خواندن", value: profile.now_following_manhwa_count },
    { icon: <ClockIcon className="h-8 w-8 text-accent" />, label: "بعداً می‌خوانم", value: profile.will_reading_manhwa_count },
    { icon: <CommentIcon className="h-8 w-8 text-accent" />, label: "کامنت‌ها", value: profile.total_comments },
    { icon: <StarIcon className="h-8 w-8 text-accent" />, label: "امتیازها", value: profile.total_manhwa_rated },
  ];

  return (
    <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <div className="grid grid-cols-[repeat(auto-fill,minmax(180px,1fr))] gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="flex items-center gap-3 rounded-card bg-surface p-4">
            {stat.icon}
            <div className="flex flex-col">
              <span className="text-xs text-text-secondary">{stat.label}</span>
              <span className="text-xl font-bold text-text-primary">
                {stat.value.toLocaleString("fa-IR")}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
