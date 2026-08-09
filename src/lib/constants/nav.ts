export interface NavLink {
  href: string;
  label: string;
}

// ترتیب طبق چیدمان راست‌به‌چپ منو (خانه اول، چون منطقی‌ترین نقطه‌ی شروعه)
// این routeها هنوز ساخته نشدن (ماژول browse شروع نشده)، فعلاً فقط لینک‌های آماده‌ن
export const NAV_LINKS: NavLink[] = [
  { href: "/", label: "خانه" },
  { href: "/weekly", label: "پخش هفتگی" },
  { href: "/manhwa", label: "مانهواها" },
  { href: "/genres", label: "ژانرها" },
  { href: "/movies", label: "سینمایی‌ها" },
  { href: "/blog", label: "بلاگ" },
];
