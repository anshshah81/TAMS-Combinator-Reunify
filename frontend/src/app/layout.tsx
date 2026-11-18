import type { Metadata } from 'next';
import './globals.css';
import { SessionProvider } from '@/components/SessionProvider';
export const metadata: Metadata = { title: 'Reunify | Demo', description: 'Synthetic disaster reunification coordination prototype' };
export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body><SessionProvider>{children}</SessionProvider></body></html>;
}
