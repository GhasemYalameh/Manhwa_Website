"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getTickets,
  isTicketUserObject,
  type TicketApiItem,
} from "@/lib/api/tickets";
import { getCoverUrl } from "@/lib/api/manhwa";
import { CreateTicketModal } from "@/components/tickets/CreateTicketModal";
import { CommentIcon } from "@/components/icons";

interface TicketListProps {
  isAdmin: boolean;
}

const PAGE_SIZE = 10;

const STATUS_LABEL: Record<string, string> = {
  op: "باز",
  cl: "بسته‌شده",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("fa-IR");
}

export function TicketList({ isAdmin }: TicketListProps) {
  const [tickets, setTickets] = useState<TicketApiItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  const ordering = isAdmin ? "is_seen,-created_at" : "-created_at";

  function fetchTickets(targetPage: number) {
    setIsLoading(true);
    getTickets({ page: targetPage, ordering })
      .then((res) => {
        setTickets(res.results);
        setTotalCount(res.count);
        setPage(targetPage);
      })
      .catch(() => setTickets([]))
      .finally(() => setIsLoading(false));
  }

  useEffect(() => {
    fetchTickets(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <main className="min-h-screen bg-bg pb-12">
      <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-xl font-bold text-text-primary">
            {isAdmin ? "مدیریت تیکت‌ها" : "تیکت‌های پشتیبانی"}
          </h1>
          {!isAdmin && (
            <button
              type="button"
              onClick={() => setIsCreating(true)}
              className="rounded-card bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-dark"
            >
              تیکت جدید
            </button>
          )}
        </div>

        {isLoading ? (
          <p className="text-sm text-text-secondary">در حال بارگذاری...</p>
        ) : tickets.length === 0 ? (
          <p className="text-sm text-text-secondary">
            {isAdmin ? "تیکتی وجود ندارد." : "شما هنوز تیکتی ثبت نکرده‌اید."}
          </p>
        ) : (
          <ul className="flex flex-col divide-y divide-divider overflow-hidden rounded-card bg-surface">
            {tickets.map((ticket) => {
              const userObj = isTicketUserObject(ticket.user) ? ticket.user : null;
              const isSeen = isAdmin && ticket.is_seen;

              return (
                <li key={ticket.id}>
                  <Link
                    href={`/tickets/${ticket.id}`}
                    className={`flex items-center gap-4 border-r-4 px-4 py-5 transition-colors ${isSeen
                      ? "border-transparent bg-bg hover:bg-accent-light/40"
                      : "border-accent bg-surface hover:bg-accent-light"
                      }`}
                  >
                    {isAdmin && (
                      <>
                        {userObj?.avatar ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={getCoverUrl(userObj.avatar)}
                            alt=""
                            className={`h-10 w-10 shrink-0 rounded-full object-cover ${isSeen ? "grayscale" : ""
                              }`}
                          />
                        ) : (
                          <span
                            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${isSeen
                              ? "bg-divider text-text-secondary"
                              : "bg-accent-light text-accent"
                              }`}
                          >
                            {userObj?.first_name?.charAt(0) ?? "?"}
                          </span>
                        )}
                      </>
                    )}

                    <div className="min-w-0 flex-1">
                      <p
                        dir="auto"
                        className={`truncate text-sm ${isSeen ? "font-normal text-text-secondary" : "font-semibold text-text-primary"
                          }`}
                      >
                        {ticket.title}
                      </p>
                      <p className="mt-1 text-xs text-text-secondary">
                        {isAdmin && userObj && (
                          <span className="ml-2">
                            {userObj.first_name} {userObj.last_name} ·{" "}
                          </span>
                        )}
                        {formatDate(ticket.created_at)}
                      </p>
                    </div>

                    <span className="flex shrink-0 items-center gap-1 text-xs text-text-secondary">
                      <CommentIcon className="h-3.5 w-3.5" />
                      {ticket.messages_count.toLocaleString("fa-IR")}
                    </span>

                    <span
                      className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-semibold ${ticket.status === "cl"
                        ? "bg-success/15 text-success"
                        : "bg-warning/15 text-warning"
                        }`}
                    >
                      {STATUS_LABEL[ticket.status] ?? ticket.status}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}

        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-center gap-2">
            <button
              type="button"
              disabled={page === 1 || isLoading}
              onClick={() => fetchTickets(page - 1)}
              className="rounded-card border border-divider px-3 py-1.5 text-sm text-text-primary disabled:opacity-40"
            >
              قبلی
            </button>
            <span className="text-sm text-text-secondary">
              {page.toLocaleString("fa-IR")} از {totalPages.toLocaleString("fa-IR")}
            </span>
            <button
              type="button"
              disabled={page === totalPages || isLoading}
              onClick={() => fetchTickets(page + 1)}
              className="rounded-card border border-divider px-3 py-1.5 text-sm text-text-primary disabled:opacity-40"
            >
              بعدی
            </button>
          </div>
        )}
      </section>

      {isCreating && (
        <CreateTicketModal onClose={() => setIsCreating(false)} onCreated={() => fetchTickets(1)} />
      )}
    </main>
  );
}