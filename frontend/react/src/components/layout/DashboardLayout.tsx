import { Outlet, Navigate } from "react-router";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useAuth } from "../../context/AuthContext";
import { Loader2 } from "lucide-react";

export function DashboardLayout() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin h-10 w-10 text-blue-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 print:block print:h-auto">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden print:overflow-visible">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 relative print:overflow-visible print:p-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
