import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Geo-Spatial Analytics Dashboard',
  description: 'Big Data Pipeline Interface Engine Matrix',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
