import { apiPost } from "./client";

const AUTH_PREFIX = "/account";

export interface VerifyOtpResponse {
  refresh_token: string;
  access_token: string;
  is_new_user: boolean;
}

export interface CompleteSignupPayload {
  first_name: string;
  last_name?: string;
  email?: string;
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

// تکمیل ثبت‌نام کاربر جدید (فقط بعد از ورود موفق با OTP و برای کاربرهایی که is_new_user=true بودن)
// توکن جدیدی برنمی‌گردونه؛ توکن‌های مرحله verify هم‌چنان معتبرن.
export function completeSignup(payload: CompleteSignupPayload): Promise<void> {
  const accessToken = getAccessToken();
  return apiPost<void>(`${AUTH_PREFIX}/otp/completion/`, payload, accessToken ?? undefined);
}

export interface PasswordAuthResponse {
  refresh_token: string;
  access_token: string;
}

export interface SignupPasswordPayload {
  phone_number: string;
  first_name: string;
  last_name?: string;
  email?: string;
  password: string;
  password2: string;
}

// ثبت‌نام مستقیم با رمز عبور؛ برخلاف فلوی OTP، توکن همینجا برمی‌گرده و نیازی به completion نیست
export function signupWithPassword(
  payload: SignupPasswordPayload
): Promise<PasswordAuthResponse> {
  return apiPost<PasswordAuthResponse>(`${AUTH_PREFIX}/signup/password/`, payload);
}

// ورود با شماره موبایل + رمز عبور (فقط برای کاربرهایی که با پسورد ثبت‌نام کرده‌ن)
export function loginWithPassword(
  phone_number: string,
  password: string
): Promise<PasswordAuthResponse> {
  return apiPost<PasswordAuthResponse>(`${AUTH_PREFIX}/login/password/`, {
    phone_number,
    password,
  });
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
