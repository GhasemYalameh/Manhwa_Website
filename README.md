# manga-auth

فلوی ورود با شماره موبایل و تایید OTP، بر اساس مستندات auth API (بک‌اند جنگو).

## اجرای محلی

```bash
cp .env.local.example .env.local
# NEXT_PUBLIC_API_BASE_URL را روی آدرس واقعی بک‌اند تنظیم کنید
npm install
npm run dev
```

سپس آدرس `http://localhost:3000` باز می‌شود و به `/login` هدایت می‌شوید.

## اجرا با Docker

```bash
docker build -t manga-auth .
docker run -p 3000:3000 --env NEXT_PUBLIC_API_BASE_URL=http://backend:8000/v1 manga-auth
```

برای اتصال به سرویس بک‌اند جنگو در همان `docker-compose.yml`، این سرویس را به شبکه مشترک اضافه کنید و `NEXT_PUBLIC_API_BASE_URL` را به نام سرویس بک‌اند در همان شبکه اشاره دهید.

## افزودن صفحات بعدی

- تابع API جدید در `src/lib/api/auth.ts` اضافه کنید (طبق الگوی `generateOtp`/`verifyOtp`).
- صفحه جدید را به‌صورت route زیر `src/app/` بسازید؛ اگر جزو فلوی احراز هویت است داخل `src/app/(auth)/` تا از همان لایوت (کارت وسط صفحه + سوییچ تم) استفاده کند.
- `/completion` و `/dashboard` فعلاً placeholder هستند و باید با صفحات واقعی جایگزین شوند.
