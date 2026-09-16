import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TryGaruda | AI Voice Calling Platform",
  description: "Deploy and manage your conversational AI voice agents.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="dashboard-container">
          <aside className="sidebar glass">
            <h2>TryGaruda</h2>
            <nav style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <a href="#" className="nav-link active">Agents</a>
              <a href="#" className="nav-link">Call Logs</a>
              <a href="#" className="nav-link">Phone Numbers</a>
              <a href="#" className="nav-link">Settings</a>
            </nav>
          </aside>
          
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
