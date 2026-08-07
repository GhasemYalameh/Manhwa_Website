import { ThemeToggle } from "@/components/ThemeToggle";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4">
      <ThemeToggle />
      <div className="w-full max-w-[400px] rounded-card border border-divider bg-surface p-8">
        {children}
      </div>
    </div>
  );
}
