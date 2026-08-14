"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { NAV_LINKS } from "@/lib/constants/nav";
import { getAccessToken, clearTokens } from "@/lib/api/client";
import {
  SearchIcon,
  BellIcon,
  ChevronDownIcon,
  MenuIcon,
  XIcon,
  UserCircleIcon,
  HeartIcon,
  LogOutIcon,
} from "@/components/icons";

// TODO: وقتی endpoint پروفایل کاربر آماده شد، این mock با داده واقعی جایگزین بشه
const MOCK_USER = { name: "محسن", avatarUrl: null as string | null };

// TODO: وقتی endpoint نوتیفیکیشن‌ها آماده شد، این عدد از سرور خونده بشه
const MOCK_UNREAD_NOTIFICATIONS = 1;

function isActiveLink(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export function Header() {
  const pathname = usePathname();
  const router = useRouter();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const userMenuRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // وضعیت لاگین از localStorage خونده میشه (بعداً جای این با فراخوانی endpoint پروفایل عوض میشه)
  useEffect(() => {
    setIsLoggedIn(!!getAccessToken());
    function handleStorage() {
      setIsLoggedIn(!!getAccessToken());
    }
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  // بستن منوی کاربر با کلیک بیرون از اون
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // میانبر کیبورد "/" برای فوکوس روی سرچ (وقتی داخل یه فیلد دیگه تایپ نمی‌کنیم)
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement;
      const isTyping = target.tagName === "INPUT" || target.tagName === "TEXTAREA";
      if (e.key === "/" && !isTyping) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  // بستن منوی موبایل هروقت مسیر عوض شد
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  function handleLogout() {
    // TODO: قبل از پاک کردن توکن‌ها، /account/jwt/blacklist/ صدا زده بشه
    // (لاگ‌اوت سمت سرور هنوز پیاده نشده - آیتم بعدی auth؛ این فعلاً فقط سمت کلاینت پاک می‌کنه)
    clearTokens();
    setIsLoggedIn(false);
    setUserMenuOpen(false);
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-40 border-b border-divider bg-surface">
      <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between gap-4 px-4 lg:px-8">
        {/* لوگو + اسم سایت */}
        <Link href="/" className="flex shrink-0 items-center gap-2 ">
          {/* TODO: جای لوگو - وقتی لوگو نهایی شد، آیکون/تصویر اینجا اضافه میشه */}
          <span className="text-2xl font-bold text-accent">نارنج‌تون</span>
        </Link>

        {/* منوی دسکتاپ */}
        <nav className="hidden items-center gap-6 lg:flex">
          {NAV_LINKS.map((link) => {
            const active = isActiveLink(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`border-b-2 pb-1 text-sm pb-0 font-medium transition-colors ${active
                  ? "border-accent text-accent"
                  : "border-transparent text-text-secondary hover:text-text-primary"
                  }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* سرچ - دسکتاپ */}
        <div className="hidden max-w-xs flex-1 lg:block">
          <div className="relative">
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary">
              <SearchIcon />
            </span>
            <input
              ref={searchInputRef}
              type="text"
              placeholder="جستجو کنید..."
              className="w-full rounded-card border border-divider bg-bg py-2 pr-10 pl-10 text-right text-sm text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent"
            />
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 rounded border border-divider px-1.5 py-0.5 text-xs text-text-secondary">
              /
            </span>
          </div>
        </div>

        {/* آیکون‌ها و کاربر - دسکتاپ */}
        <div className="hidden items-center gap-3 lg:flex">
          <Link
            href="/notifications"
            aria-label="اعلان‌ها"
            className="relative rounded-full p-2 text-text-secondary transition-colors hover:bg-accent-light hover:text-accent"
          >
            <BellIcon />
            {MOCK_UNREAD_NOTIFICATIONS > 0 && (
              <span className="absolute left-1.5 top-1.5 h-2 w-2 rounded-full bg-error" />
            )}
          </Link>

          {isLoggedIn ? (
            <div ref={userMenuRef} className="relative">
              <button
                type="button"
                onClick={() => setUserMenuOpen((v) => !v)}
                className="flex items-center gap-2 rounded-full py-1 pl-1 pr-2 transition-colors hover:bg-accent-light"
              >
                <ChevronDownIcon className={`text-text-secondary transition-transform ${userMenuOpen ? "rotate-180" : ""}`} />
                <span className="text-sm text-text-primary">{MOCK_USER.name}</span>
                {MOCK_USER.avatarUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={MOCK_USER.avatarUrl} alt="" className="h-10 w-10 rounded-full object-cover" />
                ) : (
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent-light text-sm font-semibold text-accent">
                    {MOCK_USER.name.charAt(0)}
                  </span>
                )}
              </button>

              {userMenuOpen && (
                <div className="absolute start-0 top-full z-50 mt-2 w-52 rounded-card border border-divider bg-surface py-2 shadow-lg">
                  <Link
                    href="/profile"
                    onClick={() => setUserMenuOpen(false)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-text-primary  hover:text-accent"
                  >
                    <UserCircleIcon />
                    پروفایل من
                  </Link>
                  <Link
                    href="/favorites"
                    onClick={() => setUserMenuOpen(false)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-text-primary  hover:text-accent"
                  >
                    <HeartIcon />
                    علاقه‌مندی‌ها
                  </Link>
                  <div className="my-1 border-t border-divider" />
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 px-4 py-2 text-right text-sm text-error hover:bg-accent-light"
                  >
                    <LogOutIcon />
                    خروج
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              href="/login"
              className="rounded-card bg-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-accent-dark"
            >
              ورود
            </Link>
          )}
        </div>

        {/* دکمه همبرگری - موبایل */}
        <button
          type="button"
          onClick={() => setMobileMenuOpen((v) => !v)}
          aria-label="باز کردن منو"
          className="rounded-card p-2 text-text-primary lg:hidden"
        >
          {mobileMenuOpen ? <XIcon /> : <MenuIcon />}
        </button>
      </div>

      {/* منوی موبایل */}
      {mobileMenuOpen && (
        <div className="border-t border-divider bg-surface px-4 py-4 lg:hidden">
          <div className="relative mb-4">
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary">
              <SearchIcon />
            </span>
            <input
              type="text"
              placeholder="جستجو کنید..."
              className="w-full rounded-card border border-divider bg-bg py-2.5 pr-10 pl-4 text-right text-sm text-text-primary outline-none transition-colors placeholder:text-text-secondary/60 focus:border-accent"
            />
          </div>

          <nav className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => {
              const active = isActiveLink(pathname, link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-card px-3 py-2.5 text-sm font-medium transition-colors ${active ? "bg-accent-light text-accent" : "text-text-secondary hover:bg-bg hover:text-text-primary"
                    }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          <div className="my-3 border-t border-divider" />

          <Link
            href="/notifications"
            className="flex items-center gap-2 rounded-card px-3 py-2.5 text-sm text-text-secondary hover:bg-bg hover:text-text-primary"
          >
            <BellIcon />
            اعلان‌ها
            {MOCK_UNREAD_NOTIFICATIONS > 0 && <span className="h-2 w-2 rounded-full bg-error" />}
          </Link>

          {isLoggedIn ? (
            <>
              <Link
                href="/profile"
                className="flex items-center gap-2 rounded-card px-3 py-2.5 text-sm text-text-secondary hover:bg-bg hover:text-text-primary"
              >
                <UserCircleIcon />
                {MOCK_USER.name}
              </Link>
              <Link
                href="/favorites"
                className="flex items-center gap-2 rounded-card px-3 py-2.5 text-sm text-text-secondary hover:bg-bg hover:text-text-primary"
              >
                <HeartIcon />
                علاقه‌مندی‌ها
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="flex w-full items-center gap-2 rounded-card px-3 py-2.5 text-right text-sm text-error hover:bg-bg"
              >
                <LogOutIcon />
                خروج
              </button>
            </>
          ) : (
            <Link
              href="/login"
              className="mt-2 block rounded-card bg-accent px-4 py-2.5 text-center text-sm font-semibold text-white hover:bg-accent-dark"
            >
              ورود
            </Link>
          )}
        </div>
      )}
    </header>
  );
}
