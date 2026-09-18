"use client";

import { useEffect, useRef, useState } from "react";
import { useToast } from "@/components/ui/Toast";
import { ApiError } from "@/lib/api/client";
import { requestPasswordChangeOtp, verifyPasswordChangeOtp, storeTokens } from "@/lib/api/auth";
import { isValidPassword, passwordsMatch } from "@/lib/validators/password";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { OtpInput } from "@/components/auth/OtpInput";
import { LockIcon } from "@/components/icons";

// طبق مستندات، TTL پیش‌فرض OTP — فقط وقتی درخواست موفق (۲۰۱) بود و بک‌اند خودش ttl واقعی برنگردونده استفاده میشه
const DEFAULT_OTP_TTL = 120;

type Step = "password" | "otp";

function hasTtl(body: unknown): body is { ttl: number } {
  return typeof body === "object" && body !== null && typeof (body as Record<string, unknown>).ttl === "number";
}

function hasRemaining(body: unknown): body is { remaining: number } {
  return (
    typeof body === "object" && body !== null && typeof (body as Record<string, unknown>).remaining === "number"
  );
}

function StepIndicator({ step }: { step: Step }) {
  return (
    <div className="mb-6 flex items-center gap-3">
      <div className="flex items-center gap-2">
        <span
          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${step === "password" ? "bg-accent text-white" : "bg-accent-light text-accent"
            }`}
        >
          ۱
        </span>
        <span className={`text-xs font-medium ${step === "password" ? "text-text-primary" : "text-text-secondary"}`}>
          رمز عبور جدید
        </span>
      </div>
      <div className="h-px flex-1 bg-divider" />
      <div className="flex items-center gap-2">
        <span
          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${step === "otp" ? "bg-accent text-white" : "bg-divider text-text-secondary"
            }`}
        >
          ۲
        </span>
        <span className={`text-xs font-medium ${step === "otp" ? "text-text-primary" : "text-text-secondary"}`}>
          تایید کد
        </span>
      </div>
    </div>
  );
}

export function AccountSecuritySection() {
  const { showToast } = useToast();

  const [step, setStep] = useState<Step>("password");

  const [newPassword, setNewPassword] = useState("");
  const [newPassword2, setNewPassword2] = useState("");
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [password2Error, setPassword2Error] = useState<string | null>(null);

  const [otp, setOtp] = useState("");
  const [otpError, setOtpError] = useState<string | null>(null);
  const [remainingAttempts, setRemainingAttempts] = useState<number | null>(null);

  const [secondsLeft, setSecondsLeft] = useState(0);
  const [isOtpExpired, setIsOtpExpired] = useState(false);

  const [blockedSecondsLeft, setBlockedSecondsLeft] = useState<number | null>(null);

  const [isRequesting, setIsRequesting] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  function clearCountdown() {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = null;
  }

  function startOtpCountdown(seconds: number) {
    clearCountdown();
    setIsOtpExpired(false);
    setSecondsLeft(seconds);
    intervalRef.current = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearCountdown();
          setIsOtpExpired(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }

  function startBlockedCountdown(seconds: number) {
    clearCountdown();
    setBlockedSecondsLeft(seconds);
    intervalRef.current = setInterval(() => {
      setBlockedSecondsLeft((prev) => {
        if (prev === null || prev <= 1) {
          clearCountdown();
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  }

  function validatePasswordFields(): boolean {
    let valid = true;
    if (!isValidPassword(newPassword)) {
      setPasswordError("رمز عبور باید حداقل ۸ کاراکتر باشد.");
      valid = false;
    } else {
      setPasswordError(null);
    }
    if (!passwordsMatch(newPassword, newPassword2)) {
      setPassword2Error("تکرار رمز عبور با رمز عبور یکسان نیست.");
      valid = false;
    } else {
      setPassword2Error(null);
    }
    return valid;
  }

  async function handleRequestOtp() {
    if (isRequesting || !validatePasswordFields()) return;
    setIsRequesting(true);
    try {
      await requestPasswordChangeOtp();
      setOtp("");
      setOtpError(null);
      setRemainingAttempts(null);
      setStep("otp");
      startOtpCountdown(DEFAULT_OTP_TTL);
    } catch (err) {
      if (err instanceof ApiError && err.status === 406 && hasTtl(err.body)) {
        // کد قبلی هنوز معتبره — مستقیم برو مرحله‌ی تایید، با ttl واقعی باقی‌مانده
        setOtp("");
        setOtpError(null);
        setRemainingAttempts(null);
        setStep("otp");
        startOtpCountdown(err.body.ttl);
      } else if (err instanceof ApiError && err.status === 403 && hasTtl(err.body)) {
        startBlockedCountdown(err.body.ttl);
      } else {
        showToast("ارسال کد تایید با خطا مواجه شد.", "error");
      }
    } finally {
      setIsRequesting(false);
    }
  }

  function handleEditPassword() {
    clearCountdown();
    setStep("password");
    setOtp("");
    setOtpError(null);
    setRemainingAttempts(null);
    setSecondsLeft(0);
    setIsOtpExpired(false);
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    if (isVerifying || isOtpExpired || otp.length < 5) return;
    setIsVerifying(true);
    setOtpError(null);
    try {
      const res = await verifyPasswordChangeOtp({
        otp,
        new_password: newPassword,
        new_password2: newPassword2,
      });
      storeTokens(res.access_token, res.refresh_token);
      showToast("رمز عبور با موفقیت تغییر کرد.", "success");
      clearCountdown();
      setStep("password");
      setNewPassword("");
      setNewPassword2("");
      setOtp("");
      setOtpError(null);
      setRemainingAttempts(null);
      setSecondsLeft(0);
      setIsOtpExpired(false);
      setBlockedSecondsLeft(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 400 && hasRemaining(err.body)) {
        setOtpError("کد وارد شده اشتباه است.");
        setRemainingAttempts(err.body.remaining);
        setOtp("");
      } else if (err instanceof ApiError && err.status === 403 && hasTtl(err.body)) {
        clearCountdown();
        setStep("password");
        startBlockedCountdown(err.body.ttl);
      } else if (err instanceof ApiError && err.status === 400) {
        setOtpError("اطلاعات وارد شده معتبر نیست. لطفاً دوباره تلاش کنید.");
      } else {
        showToast("تغییر رمز عبور با خطا مواجه شد.", "error");
      }
    } finally {
      setIsVerifying(false);
    }
  }

  const isBlocked = blockedSecondsLeft !== null;

  return (
    <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <h2 className="mb-4 text-lg font-bold text-text-primary">امنیت حساب</h2>

      <div className="max-w-md rounded-card bg-surface p-5">
        <div className="mb-5 flex items-center gap-2 text-text-primary">
          <LockIcon className="h-5 w-5 text-accent" />
          <h3 className="text-sm font-semibold">تغییر رمز عبور</h3>
        </div>

        {isBlocked ? (
          <div className="rounded-card bg-error/10 p-4 text-sm text-error">
            <p>به‌دلیل تلاش‌های ناموفق متعدد، امکان تلاش مجدد موقتاً مسدود شده است.</p>
            <p className="mt-1 text-xs">
              {blockedSecondsLeft!.toLocaleString("fa-IR")} ثانیه‌ی دیگر می‌توانید دوباره تلاش کنید.
            </p>
          </div>
        ) : (
          <>
            <StepIndicator step={step} />

            {step === "password" && (
              <div className="flex flex-col gap-4">
                <PasswordInput
                  id="new-password"
                  label="رمز عبور جدید"
                  value={newPassword}
                  onChange={setNewPassword}
                  error={passwordError ?? undefined}
                  placeholder="رمز عبور جدید"
                  autoComplete="new-password"
                />
                <PasswordInput
                  id="new-password2"
                  label="تکرار رمز عبور جدید"
                  value={newPassword2}
                  onChange={setNewPassword2}
                  error={password2Error ?? undefined}
                  placeholder="تکرار رمز عبور جدید"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={handleRequestOtp}
                  disabled={isRequesting}
                  className="self-start rounded-card bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:opacity-50"
                >
                  {isRequesting ? "در حال ارسال..." : "دریافت کد یکبار مصرف"}
                </button>
              </div>
            )}

            {step === "otp" && (
              <form onSubmit={handleVerify} className="flex flex-col gap-4">
                <p className="text-center text-xs text-text-secondary">
                  {isOtpExpired
                    ? "کد تایید منقضی شده است."
                    : `کد تایید ارسال شد — اعتبار: ${secondsLeft.toLocaleString("fa-IR")} ثانیه`}
                </p>

                <OtpInput value={otp} onChange={setOtp} error={otpError ?? undefined} disabled={isOtpExpired} />

                {remainingAttempts !== null && !isOtpExpired && (
                  <p className="text-center text-xs text-text-secondary">
                    {remainingAttempts.toLocaleString("fa-IR")} تلاش باقی‌مانده
                  </p>
                )}

                {isOtpExpired ? (
                  <button
                    type="button"
                    onClick={handleEditPassword}
                    className="rounded-card border border-divider px-4 py-2.5 text-sm text-text-primary transition-colors hover:border-accent hover:text-accent"
                  >
                    ویرایش رمز عبور
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={isVerifying || otp.length < 5}
                    className="rounded-card bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:opacity-50"
                  >
                    {isVerifying ? "در حال ثبت..." : "ثبت رمز جدید"}
                  </button>
                )}
              </form>
            )}
          </>
        )}
      </div>
    </section>
  );
}