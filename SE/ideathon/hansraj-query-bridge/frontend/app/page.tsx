"use client";
import { useEffect } from "react";
import { getSession } from "@/lib/api";

export default function Home() {
  useEffect(() => {
    const s = getSession();
    window.location.replace(s ? `/${s.user.role.toLowerCase()}/dashboard` : "/login");
  }, []);
  return null;
}
