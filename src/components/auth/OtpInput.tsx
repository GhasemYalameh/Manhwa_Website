"use client";

import { useRef } from "react";

const OTP_LENGTH = 5;

interface OtpInputProps {
  value: string; // رشته اعداد، حداکثر طول OTP_LENGTH
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export function OtpInput({ value, onChange, error, disabled }: OtpInputProps) {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);
  const digits = value.split("");

  function setDigitAt(index: number, digit: string) {
    const next = value.split("");
    next[index] = digit;
    onChange(next.join("").slice(0, OTP_LENGTH));
  }

  function handleChange(index: number, raw: string) {
    const digit = raw.replace(/\D/g, "").slice(-1);
    setDigitAt(index, digit);
    if (digit && index < OTP_LENGTH - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  }

  function handleKeyDown(index: number, e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Backspace" && !digits[index] && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  }

  function handlePaste(e: React.ClipboardEvent<HTMLInputElement>) {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, OTP_LENGTH);
    if (!pasted) return;
    onChange(pasted);
    const focusIndex = Math.min(pasted.length, OTP_LENGTH - 1);
    inputsRef.current[focusIndex]?.focus();
  }

  return (
    <div>
      <div dir="ltr" className="flex justify-center gap-2" onPaste={handlePaste}>
        {Array.from({ length: OTP_LENGTH }).map((_, i) => (
          <input
            key={i}
            ref={(el) => {
              inputsRef.current[i] = el;
            }}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digits[i] ?? ""}
            onChange={(e) => handleChange(i, e.target.value)}
            onKeyDown={(e) => handleKeyDown(i, e)}
            disabled={disabled}
            className="h-14 w-12 rounded-card border border-divider bg-surface text-center text-xl font-semibold text-text-primary outline-none transition-colors focus:border-accent disabled:opacity-50"
            aria-invalid={!!error}
            aria-label={`رقم ${i + 1} کد تایید`}
          />
        ))}
      </div>
      {error && <p className="mt-3 text-center text-sm text-error">{error}</p>}
    </div>
  );
}
