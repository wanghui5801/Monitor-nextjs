import { ThemeProvider } from 'next-themes'
import type { AppProps } from "next/app";
import "../styles/globals.css";
import { AuthProvider } from '../hooks/useAuth';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <Component {...pageProps} />
      </ThemeProvider>
    </AuthProvider>
  );
}
