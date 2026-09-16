// فاصله‌ی زمانی نسبی و کوتاه («۳ دقیقه پیش»، «۲ روز پیش») — برای رویدادهای اخیر (کامنت، نوتیفیکیشن).
// برای بازه‌های طولانی‌تر (ماه/سال) به‌جاش از formatMembershipDuration در membership.ts استفاده کن.
export function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "همین الان";
  if (minutes < 60) return `${minutes.toLocaleString("fa-IR")} دقیقه پیش`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours.toLocaleString("fa-IR")} ساعت پیش`;
  const days = Math.floor(hours / 24);
  return `${days.toLocaleString("fa-IR")} روز پیش`;
}
