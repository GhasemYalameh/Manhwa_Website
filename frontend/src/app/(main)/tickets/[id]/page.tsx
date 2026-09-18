"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/api/client";
import { getMe } from "@/lib/api/auth";
import { TicketThread } from "@/components/tickets/TicketThread";

export default function TicketDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const [isChecking, setIsChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (!getAccessToken()) {
      router.push("/login");
      return;
    }
    getMe()
      .then((profile) => setIsAdmin(profile.is_admin))
      .catch(() => {})
      .finally(() => setIsChecking(false));
  }, [router]);

  if (isChecking) return null;

  return <TicketThread ticketId={Number(params.id)} isAdmin={isAdmin} />;
}