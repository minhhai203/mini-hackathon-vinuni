import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vinpearl AI Resort & Package Fit Assistant",
  description: "Next.js UI for a Vinpearl AI travel recommendation assistant prototype.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
