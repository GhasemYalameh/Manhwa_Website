// حداقل طول رمز عبور؛ اگر بک‌اند قانون سخت‌گیرانه‌تری داشت اینجا اضافه می‌شود
export function isValidPassword(value: string): boolean {
  return value.length >= 8;
}

export function passwordsMatch(password: string, password2: string): boolean {
  return password.length > 0 && password === password2;
}
