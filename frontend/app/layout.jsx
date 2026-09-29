import "./globals.css";

export const metadata = {
  title: "IT Support Assistant",
  description: "IT troubleshooting, software and licensing help",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
