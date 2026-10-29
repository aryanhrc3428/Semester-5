import type { Metadata, Viewport } from "next";
import "./globals.css";
import { ToastProvider } from "@/components/ui";

export const metadata: Metadata = {
  title: "Hansraj Query Bridge",
  description: "Get verified answers from Hansraj College, or reach the right teacher, in one place.",
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#0e4a5a" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body><ToastProvider>{children}</ToastProvider></body>
    </html>
  );
}
