"use client";

import { formatPhoneDisplay, stripToDigits } from "@/lib/validators/phone";

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
      {/* <label htmlFor="phone" className="mb-1.5 block text-sm text-text-secondary">
        شماره موبایل <span className="text-error">*</span>
      </label> */}
      <div className="relative">
        <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" />
          </svg>
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