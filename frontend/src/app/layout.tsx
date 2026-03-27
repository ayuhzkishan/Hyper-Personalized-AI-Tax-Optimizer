import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hyper-Personalized AI Tax Optimizer",
  description: "Next-gen tax planning with premium Personal CA features.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-50 min-h-screen font-sans">
        {children}
      </body>
    </html>
  );
}
