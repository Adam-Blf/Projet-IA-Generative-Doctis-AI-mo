/**
 * =============================================================================
 * Projet: Doctis AI
 * Auteurs: Adam Beloucif & Amina Medjdoub
 * Description: Layout principal de l'application Next.js
 * =============================================================================
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Doctis AI - Assistant de Pré-diagnostic Médical",
  description:
    "Doctis AI utilise l'intelligence artificielle pour analyser vos symptômes et vous orienter vers les soins appropriés. Projet réalisé par Adam Beloucif & Amina Medjdoub.",
  keywords: ["médical", "IA", "diagnostic", "santé", "symptômes"],
  authors: [
    { name: "Adam Beloucif" },
    { name: "Amina Medjdoub" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
