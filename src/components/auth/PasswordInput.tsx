"use client";

import { useState } from "react";
import { PasswordIcon } from "../icons";

interface PasswordInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  placeholder?: string;
  autoComplete?: string;
  required?: boolean;
}

export function PasswordInput({
  id,
  label,
  value,
  onChange,
  error,
  disabled,
  placeholder,
  autoComplete,
  required = true,
}: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div>
      <div className="relative">
        <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary">
          <PasswordIcon />
        </span>
        <input
          id={id}
          type={visible ? "text" : "password"}
          dir="ltr"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          autoComplete={autoComplete}
          placeholder={placeholder}
          className="w-full rounded-card border border-divider bg-surface py-3 pl-16 pr-11 text-right text-base text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 placeholder:text-right focus:border-accent disabled:opacity-50"
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          disabled={disabled}
          tabIndex={-1}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-text-secondary hover:text-accent disabled:opacity-50"
        >
          {visible ? "مخفی" : "نمایش"}
        </button>
      </div>
      {error && (
        <p id={`${id}-error`} className="mt-1.5 text-sm text-error">
          {error}
        </p>
      )}
    </div>
  );
}