import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'QuickDeal - Compare, Negotiate & Save on Quick Commerce',
  description: 'Compare prices across Blinkit, Zepto, Instamart, BigBasket & JioMart. Negotiate with sellers for the best deals on groceries in India.',
  keywords: 'price comparison, quick commerce, blinkit, zepto, instamart, bigbasket, jiomart, grocery deals, negotiate prices',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

