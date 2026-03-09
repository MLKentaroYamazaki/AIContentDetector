import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Content Detector",
  description: "テキストが人間によって書かれたものか、AIによって生成されたものかを判定します",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <head>
        <link href="/tailwind.css" rel="stylesheet" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
