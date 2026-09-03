import { apiPost, apiGet, getRefreshToken } from "./client";

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
// { auth: true } یعنی apiPost خودش توکن رو از storage می‌خونه و اگه ۴۰۱ بگیره، رفرش+retry می‌کنه.
export function completeSignup(payload: CompleteSignupPayload): Promise<void> {
  return apiPost<void>(`${AUTH_PREFIX}/otp/completion/`, payload, { auth: true });
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

// مدیریت توکن‌ها الان در client.ts هست (چون apiPost خودش بهشون نیاز داره)؛
// اینجا فقط دوباره export می‌کنیم که importهای بقیه‌ی فایل‌ها تغییر نکنه.
export { getAccessToken, storeTokens, getRefreshToken, clearTokens } from "./client";

export interface UserProfile {
  first_name: string;
  last_name: string;
  avatar: string | null; // relative URL
  phone_number: string;
  is_subscriber: boolean;
}

export function getMe(): Promise<UserProfile> {
  return apiGet<UserProfile>(`${AUTH_PREFIX}/me/`, { auth: true });
}

// خروج سمت سرور — رفرش توکن فعلی رو بلاک‌لیست می‌کنه (best-effort)
export function logout(): Promise<void> {
  const refresh = getRefreshToken();
  if (!refresh) return Promise.resolve();
  return apiPost<void>(`${AUTH_PREFIX}/jwt/blacklist/`, { refresh });
}