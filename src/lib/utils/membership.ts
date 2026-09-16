// مدت‌زمان عضویت رو به شکل نسبی («۳ ماه») برمی‌گردونه.
// از timeAgo (که برای رویدادهای اخیر مثل کامنت/نوتیفیکیشنه) جداست چون اون فقط تا "روز پیش" میره
// و برای بازه‌های طولانی (ماه/سال) مناسب نیست.
export function formatMembershipDuration(iso: string): string {
  const joined = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - joined.getTime();
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (days < 1) return "امروز";
  if (days < 30) return `${days.toLocaleString("fa-IR")} روز`;

  const months = Math.floor(days / 30);
  if (months < 12) return `${months.toLocaleString("fa-IR")} ماه`;

  const years = Math.floor(months / 12);
  const remMonths = months % 12;
  if (remMonths === 0) return `${years.toLocaleString("fa-IR")} سال`;
  return `${years.toLocaleString("fa-IR")} سال و ${remMonths.toLocaleString("fa-IR")} ماه`;
}
