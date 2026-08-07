"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { completeSignup, getAccessToken } from "@/lib/api/auth";
import { isValidEmail, isValidFirstName, isValidLastName } from "@/lib/validators/profile";
import { ApiError } from "@/lib/api/client";

function extractMessage(body: unknown): string | undefined {
  if (body && typeof body === "object") {
    const rec = body as Record<string, unknown>;
    const val = rec.detail ?? rec.message ?? rec.error;
    if (typeof val === "string") return val;
  }
  return undefined;
}

export default function CompletionPage() {
  const router = useRouter();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  const canSubmit =
    isValidFirstName(firstName) &&
    isValidLastName(lastName) &&
    isValidEmail(email) &&
    !loading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    // اگر توکن نباشه یعنی کاربر مستقیم به این صفحه اومده، نه از فلوی verify
    if (!getAccessToken()) {
      router.push("/login");
      return;
    }

    setError(undefined);
    setLoading(true);

    try {
      await completeSignup({
        first_name: firstName.trim(),
        last_name: lastName.trim() || undefined,
        email: email.trim() || undefined,
      });
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        // توکن منقضی یا نامعتبره؛ کاربر باید دوباره وارد بشه
        router.push("/login");
        return;
      }
      if (err instanceof ApiError) {
        setError(extractMessage(err.body) ?? "اطلاعات وارد شده معتبر نیست.");
      } else {
        setError("خطا در برقراری ارتباط با سرور. دوباره تلاش کنید.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="mb-1.5 text-xl font-medium text-text-primary">تکمیل ثبت‌نام</h1>
      <p className="mb-6 text-sm text-text-secondary">
        برای تکمیل حساب کاربری، لطفاً اطلاعات زیر را وارد کنید.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="firstName" className="mb-1.5 block text-sm text-text-secondary">
            نام <span className="text-error">*</span>
          </label>
          <input
            id="firstName"
            type="text"
            maxLength={25}
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            disabled={loading}
            className="w-full rounded-card border border-divider bg-surface px-4 py-3 text-right text-base text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent disabled:opacity-50"
            placeholder="مثلاً علی"
          />
        </div>

        <div>
          <label htmlFor="lastName" className="mb-1.5 block text-sm text-text-secondary">
            نام‌خانوادگی
          </label>
          <input
            id="lastName"
            type="text"
            maxLength={25}
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            disabled={loading}
            className="w-full rounded-card border border-divider bg-surface px-4 py-3 text-right text-base text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent disabled:opacity-50"
            placeholder="اختیاری"
          />
        </div>

        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm text-text-secondary">
            ایمیل
          </label>
          <input
            id="email"
            type="email"
            dir="ltr"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
            className="w-full rounded-card border border-divider bg-surface px-4 py-3 text-left text-base text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent disabled:opacity-50"
            placeholder="example@mail.com"
          />
        </div>

        {error && <p className="text-sm text-error">{error}</p>}

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full rounded-card bg-accent py-3 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "در حال ثبت..." : "تکمیل ثبت‌نام"}
        </button>
      </form>
    </>
  );
}