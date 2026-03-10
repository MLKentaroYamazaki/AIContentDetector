"use client";
import { useSession, signIn } from "next-auth/react";
import { useEffect } from "react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === "loading") return;
    if (!session) signIn("google");
  }, [session, status]);

  if (status === "loading") return <div className="min-h-screen flex items-center justify-center text-gray-500">Loading...</div>;
  if (!session) return <div className="min-h-screen flex items-center justify-center text-gray-500">Redirecting...</div>;

  return <>{children}</>;
}
