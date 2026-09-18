"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/api/client";
import { getMe } from "@/lib/api/auth";
import { TicketList } from "@/components/tickets/TicketList";

export default function TicketsPage() {
  const router = useRouter();
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

  return <TicketList isAdmin={isAdmin} />;
}