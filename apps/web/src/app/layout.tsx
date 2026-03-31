import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CARE Assessment Kit — Terrene Foundation",
  description:
    "AI-guided governance assessment. Discover what AI governance your organization needs.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
