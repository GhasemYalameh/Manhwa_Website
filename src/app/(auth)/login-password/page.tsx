"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { PhoneInput } from "@/components/auth/PhoneInput";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { loginWithPassword, storeTokens } from "@/lib/api/auth";
import { isValidPhone } from "@/lib/validators/phone";
import { ApiError } from "@/lib/api/client";

function extractMessage(body: unknown): string | undefined {
  if (body && typeof body === "object") {
    const rec = body as Record<string, unknown>;
    const val = rec.detail ?? rec.message ?? rec.error;
    if (typeof val === "string") return val;
  }
  return undefined;
}

export default function LoginPasswordPage() {
  const router = useRouter();

  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  const canSubmit = isValidPhone(phone) && password.length > 0 && !loading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setError(undefined);
    setLoading(true);

    try {
      const res = await loginWithPassword(phone, password);
      storeTokens(res.access_token, res.refresh_token);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(extractMessage(err.body) ?? "شماره موبایل یا رمز عبور اشتباه است.");
      } else {
        setError("خطا در برقراری ارتباط با سرور. دوباره تلاش کنید.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="mb-1.5 text-xl font-medium text-text-primary">ورود با رمز عبور</h1>
      <p className="mb-6 text-sm text-text-secondary">
        شماره موبایل و رمز عبور خود را وارد کنید.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <PhoneInput value={phone} onChange={setPhone} disabled={loading} />

        <PasswordInput
          id="password"
          label="رمز عبور"
          value={password}
          onChange={setPassword}
          disabled={loading}
          autoComplete="current-password"
        />

        {error && <p className="text-sm text-error">{error}</p>}

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full rounded-card bg-accent py-3 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "در حال ورود..." : "ورود"}
        </button>

        <p className="text-center text-sm text-text-secondary">
          حساب ندارید؟{" "}
          <Link href="/signup" className="text-accent hover:text-accent-dark">
            ثبت‌نام با رمز عبور
          </Link>
        </p>
        <p className="text-center text-sm text-text-secondary">
          یا{" "}
          <Link href="/login" className="text-accent hover:text-accent-dark">
            ورود با کد پیامکی
          </Link>
        </p>
      </form>
    </>
  );
}
