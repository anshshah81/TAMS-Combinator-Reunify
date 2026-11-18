import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Reunify | Demo', description: 'Synthetic disaster reunification coordination prototype' };
export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
