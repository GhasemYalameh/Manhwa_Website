const PHONE_REGEX = /^09\d{9}$/;

export function isValidPhone(phone: string): boolean {
  return PHONE_REGEX.test(phone);
}

// "09123456789" -> "0912 345 6789" برای نمایش خواناتر
export function formatPhoneDisplay(digitsOnly: string): string {
  const d = digitsOnly.slice(0, 11);
  const parts = [d.slice(0, 4), d.slice(4, 7), d.slice(7, 11)].filter(Boolean);
  return parts.join(" ");
}

// حذف هر چیزی جز رقم، برای گرفتن مقدار خام از ورودی فرمت‌شده
export function stripToDigits(value: string): string {
  return value.replace(/\D/g, "").slice(0, 11);
}
