import { Header } from "@/components/layout/Header";
// ...

export default function DashboardPage() {
  return (
    <>
      <Header />
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-bg px-4">
        <p className="text-text-primary">به داشبورد خوش آمدید.</p>
      </div>
    </>
    // <div className="flex min-h-screen items-center justify-center bg-bg px-4">
    //   <p className="text-text-primary">به داشبورد خوش آمدید.</p>
    // </div>
  );
}
