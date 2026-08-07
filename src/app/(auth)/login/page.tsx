"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { PhoneInput } from "@/components/auth/PhoneInput";
import { generateOtp } from "@/lib/api/auth";
import { isValidPhone } from "@/lib/validators/phone";
import { ApiError } from "@/lib/api/client";

export default function LoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState("");
  const [error, setError] = useState<string>();
  const [blacklisted, setBlacklisted] = useState(false);
  const [loading, setLoading] = useState(false);

  const canSubmit = isValidPhone(phone) && !loading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setError(undefined);
    setBlacklisted(false);
    setLoading(true);

    try {
      await generateOtp(phone);
      router.push(`/verify?phone=${phone}`);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 403) {
          setBlacklisted(true);
        } else if (err.status === 406) {
          // کد قبلا ارسال شده و هنوز منقضی نشده؛ کاربر را مستقیم به صفحه تایید می‌بریم
          router.push(`/verify?phone=${phone}`);
          return;
        } else {
          setError("شماره موبایل معتبر نیست.");
        }
      } else {
        setError("خطا در برقراری ارتباط با سرور. دوباره تلاش کنید.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="mb-1.5 text-xl font-medium text-text-primary">ورود / ثبت‌نام</h1>
      <p className="mb-6 text-sm text-text-secondary">
        شماره موبایل خود را وارد کنید تا کد تایید برایتان پیامک شود.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <PhoneInput value={phone} onChange={setPhone} error={error} disabled={loading} />

        {blacklisted && (
          <p className="rounded-card bg-accent-light px-4 py-3 text-sm text-error">
            به دلیل تلاش‌های ناموفق زیاد، دسترسی شما موقتاً محدود شده است. کمی بعد دوباره تلاش
            کنید.
          </p>
        )}

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full rounded-card bg-accent py-3 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "در حال ارسال..." : "دریافت کد تایید"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-text-secondary">
        یا{" "}
        <Link href="/login-password" className="text-accent hover:text-accent-dark">
          ورود با رمز عبور
        </Link>{" "}
        /{" "}
        <Link href="/signup" className="text-accent hover:text-accent-dark">
          ثبت‌نام
        </Link>
      </p>
    </>
  );
}