"use client";

import { formatPhoneDisplay, stripToDigits } from "@/lib/validators/phone";
import { PhoneIcon } from "../icons";

interface PhoneInputProps {
  value: string; // فقط رقم، بدون فرمت
  onChange: (digitsOnly: string) => void;
  error?: string;
  disabled?: boolean;
  autoFocus?: boolean;
}

export function PhoneInput({ value, onChange, error, disabled, autoFocus }: PhoneInputProps) {
  return (
    <div>
      <div className="relative">
        <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary">
          <PhoneIcon />
        </span>
        <input
          id="phone"
          type="tel"
          inputMode="numeric"
          placeholder="شماره موبایل"
          value={formatPhoneDisplay(value)}
          onChange={(e) => onChange(stripToDigits(e.target.value))}
          disabled={disabled}
          autoFocus={autoFocus}
          className="w-full rounded-card border border-divider bg-surface py-3 pr-11 pl-4 text-right text-lg text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 placeholder:text-right focus:border-accent disabled:opacity-50"
          aria-invalid={!!error}
          aria-describedby={error ? "phone-error" : undefined}
        />
      </div>
      {error && (
        <p id="phone-error" className="mt-1.5 text-sm text-error">
          {error}
        </p>
      )}
    </div>
  );
}