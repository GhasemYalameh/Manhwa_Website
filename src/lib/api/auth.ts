import { apiPost } from "./client";

const AUTH_PREFIX = "/account";

export interface VerifyOtpResponse {
  refresh_token: string;
  access_token: string;
  is_new_user: boolean;
}

export function generateOtp(phone_number: string): Promise<void> {
  return apiPost<void>(`${AUTH_PREFIX}/otp/`, { phone_number });
}

export function verifyOtp(
  phone_number: string,
  otp: string
): Promise<VerifyOtpResponse> {
  return apiPost<VerifyOtpResponse>(`${AUTH_PREFIX}/otp/verify/`, { phone_number, otp });
}

// --- مدیریت ساده توکن‌ها در localStorage ---
// در صورت نیاز به سناریوهای پیچیده‌تر (SSR، httpOnly cookie) باید این بخش عوض شود.

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export function storeTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}
