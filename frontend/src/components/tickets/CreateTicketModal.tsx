"use client";

import { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { useToast } from "@/components/ui/Toast";
import { createTicket } from "@/lib/api/tickets";

interface CreateTicketModalProps {
  onClose: () => void;
  onCreated: () => void;
}

const MAX_TEXT_LENGTH = 500;

export function CreateTicketModal({ onClose, onCreated }: CreateTicketModalProps) {
  const { showToast } = useToast();
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await createTicket(trimmed, title.trim() || undefined);
      showToast("تیکت شما ثبت شد.", "success");
      onCreated();
      onClose();
    } catch {
      showToast("ثبت تیکت با خطا مواجه شد.", "error");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title="تیکت جدید" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary">عنوان (اختیاری)</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            dir="auto"
            className="rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary">
            پیام ({text.length.toLocaleString("fa-IR")}/{MAX_TEXT_LENGTH.toLocaleString("fa-IR")})
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value.slice(0, MAX_TEXT_LENGTH))}
            rows={5}
            dir="auto"
            className="w-full resize-none rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
          />
        </div>

        <button
          type="submit"
          disabled={!text.trim() || isSubmitting}
          className="rounded-card bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:opacity-50"
        >
          {isSubmitting ? "در حال ارسال..." : "ارسال تیکت"}
        </button>
      </form>
    </Modal>
  );
}
