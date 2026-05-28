import type { ReactNode } from "react";
import { Navigate } from "react-router";
import { useAuth } from "../../context/AuthContext";
import { SystemRol } from "../../types/auth";

interface RoleGuardProps {
  allowedRoles: SystemRol[];
  children: ReactNode;
  redirectTo?: string;
}

/**
 * Wrapper that redirects unauthorized users to a given path.
 * Use in the router to protect entire routes.
 */
export function RoleGuard({ allowedRoles, children, redirectTo = "/dashboard" }: RoleGuardProps) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!user || !allowedRoles.includes(user.rol)) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}
