"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const current = document.documentElement.getAttribute("data-theme");
    if (current === "dark" || current === "light") setTheme(current);
  }, []);

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label="تغییر پوسته روشن/تیره"
      className="fixed left-4 top-4 rounded-full border border-divider bg-surface px-3 py-1.5 text-sm text-text-secondary transition-colors hover:border-accent hover:text-accent"
    >
      {theme === "dark" ? "روشن" : "تیره"}
    </button>
  );
}
