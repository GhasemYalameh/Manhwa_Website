"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { PhoneInput } from "@/components/auth/PhoneInput";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { signupWithPassword, storeTokens } from "@/lib/api/auth";
import { isValidPhone } from "@/lib/validators/phone";
import { isValidEmail, isValidFirstName, isValidLastName } from "@/lib/validators/profile";
import { isValidPassword, passwordsMatch } from "@/lib/validators/password";
import { ApiError } from "@/lib/api/client";

function extractMessage(body: unknown): string | undefined {
  if (body && typeof body === "object") {
    const rec = body as Record<string, unknown>;
    const val = rec.detail ?? rec.message ?? rec.error;
    if (typeof val === "string") return val;
  }
  return undefined;
}

export default function SignupPage() {
  const router = useRouter();

  const [phone, setPhone] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);

  const canSubmit =
    isValidPhone(phone) &&
    isValidFirstName(firstName) &&
    isValidLastName(lastName) &&
    isValidEmail(email) &&
    isValidPassword(password) &&
    passwordsMatch(password, password2) &&
    !loading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setError(undefined);
    setLoading(true);

    try {
      const res = await signupWithPassword({
        phone_number: phone,
        first_name: firstName.trim(),
        last_name: lastName.trim() || undefined,
        email: email.trim() || undefined,
        password,
        password2,
      });
      storeTokens(res.access_token, res.refresh_token);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          extractMessage(err.body) ?? "ثبت‌نام ناموفق بود. اطلاعات وارد شده را بررسی کنید."
        );
      } else {
        setError("خطا در برقراری ارتباط با سرور. دوباره تلاش کنید.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="mb-8 text-2xl font-medium text-text-primary text-center">ثبت‌نام با رمز عبور</h1>
      {/* <p className="mb-6 text-sm text-text-secondary">
        برای ساخت حساب کاربری جدید، اطلاعات زیر را وارد کنید.
      </p> */}

      <form onSubmit={handleSubmit} className="space-y-5">
        <PhoneInput value={phone} onChange={setPhone} disabled={loading} />

        <div>
          {/* <label htmlFor="firstName" className="mb-1.5 block text-sm text-text-secondary">
            نام <span className="text-error">*</span>
          </label> */}
          <input
            id="firstName"
            type="text"
            maxLength={25}
            value={firstName}
            dir="ltr"
            onChange={(e) => setFirstName(e.target.value)}
            disabled={loading}
            className="w-full rounded-card border border-divider bg-surface px-4 py-3 text-right text-base text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent disabled:opacity-50"
            placeholder="نام"
          />
        </div>

        <div>
          {/* <label htmlFor="lastName" className="mb-1.5 block text-sm text-text-secondary">
            نام‌خانوادگی
          </label> */}
          <input
            id="lastName"
            type="text"
            maxLength={25}
            value={lastName}
            dir="ltr"
            onChange={(e) => setLastName(e.target.value)}
            disabled={loading}
            className="w-full rounded-card border border-divider bg-surface px-4 py-3 text-right text-base text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent disabled:opacity-50"
            placeholder="نام خانوادگی"
          />
        </div>

        <div>
          {/* <label htmlFor="email" className="mb-1.5 block text-sm text-text-secondary">
            ایمیل
          </label> */}
          <input
            id="email"
            type="email"
            dir="ltr"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
            className="w-full rounded-card border border-divider bg-surface px-4 py-3 text-right text-base text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 placeholder:text-right focus:border-accent disabled:opacity-50"
            placeholder="(اختیاری) ایمیل"
          />
        </div>

        <PasswordInput
          id="password"
          label="رمز عبور"
          value={password}
          onChange={setPassword}
          disabled={loading}
          autoComplete="new-password"
          placeholder="رمز عبور"
        />

        <PasswordInput
          id="password2"
          label="تکرار رمز عبور"
          value={password2}
          onChange={setPassword2}
          disabled={loading}
          placeholder="تکرار رمز عبور"
          autoComplete="new-password"
          error={
            password2.length > 0 && !passwordsMatch(password, password2)
              ? "رمز عبور و تکرار آن یکسان نیستند."
              : undefined
          }
        />

        {error && <p className="text-sm text-error">{error}</p>}

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full rounded-card bg-accent py-3 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "در حال ثبت..." : "ثبت‌نام"}
        </button>

        <p className="text-center text-sm text-text-secondary">
          حساب کاربری دارید؟{" "}
          <Link href="/login?tab=password" className="text-accent hover:text-accent-dark">
            ورود
          </Link>
        </p>
      </form>
    </>
  );
}
