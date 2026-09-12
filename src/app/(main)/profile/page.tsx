"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/api/client";
import { getMe, type UserProfile } from "@/lib/api/auth";
import { ProfileHeader } from "@/components/profile/ProfileHeader";
import { ProfileTabs } from "@/components/profile/ProfileTabs";
import { WatchlistSection } from "@/components/profile/WatchlistSection";
import { SubscriptionSection } from "@/components/profile/SubscriptionSection";
import { MyCommentsSection } from "@/components/profile/MyCommentsSection";

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "unauthorized">("loading");

  useEffect(() => {
    if (!getAccessToken()) {
      router.push("/login");
      return;
    }
    getMe()
      .then((res) => {
        setProfile(res);
        setStatus("ready");
      })
      .catch(() => setStatus("unauthorized"));
  }, [router]);

  if (status === "loading") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-bg">
        <p className="text-sm text-text-secondary">در حال بارگذاری...</p>
      </main>
    );
  }

  if (status === "unauthorized" || !profile) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-bg">
        <p className="text-sm text-text-secondary">برای مشاهده‌ی این صفحه باید وارد حساب کاربری شوید.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-bg pb-12">
      <ProfileHeader profile={profile} onUpdated={setProfile} />
      <ProfileTabs
        tabs={[
          { id: "watchlist", label: "لیست مطالعه", content: <WatchlistSection /> },
          { id: "subscription", label: "اشتراک", content: <SubscriptionSection /> },
          { id: "comments", label: "کامنت‌های من", content: <MyCommentsSection /> },
        ]}
      />
    </main>
  );
}