const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// طبق مستندات API: نام حداکثر ۲۵ کاراکتر و اجباری
export function isValidFirstName(value: string): boolean {
    const trimmed = value.trim();
    return trimmed.length > 0 && trimmed.length <= 25;
}

// نام خانوادگی اختیاریه؛ اگه خالیه معتبره، وگرنه حداکثر ۲۵ کاراکتر
export function isValidLastName(value: string): boolean {
    return value.trim().length <= 25;
}

// ایمیل اختیاریه؛ اگه خالیه معتبره، وگرنه باید فرمت درست داشته باشه
export function isValidEmail(value: string): boolean {
    const trimmed = value.trim();
    if (trimmed.length === 0) return true;
    return EMAIL_REGEX.test(trimmed);
}