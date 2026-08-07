"use client";

import { formatPhoneDisplay, stripToDigits } from "@/lib/validators/phone";

interface PhoneInputProps {
  value: string; // فقط رقم، بدون فرمت
  onChange: (digitsOnly: string) => void;
  error?: string;
  disabled?: boolean;
}

export function PhoneInput({ value, onChange, error, disabled }: PhoneInputProps) {
  return (
    <div>
      <label htmlFor="phone" className="mb-1.5 block text-sm text-text-secondary">
        شماره موبایل
      </label>
      <input
        id="phone"
        type="tel"
        inputMode="numeric"
        placeholder="0912 345 6789"
        value={formatPhoneDisplay(value)}
        onChange={(e) => onChange(stripToDigits(e.target.value))}
        disabled={disabled}
        className="w-full rounded-card border border-divider bg-surface px-4 py-3 text-right text-lg text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent disabled:opacity-50"
        aria-invalid={!!error}
        aria-describedby={error ? "phone-error" : undefined}
      />
      {error && (
        <p id="phone-error" className="mt-1.5 text-sm text-error">
          {error}
        </p>
      )}
    </div>
  );
}
