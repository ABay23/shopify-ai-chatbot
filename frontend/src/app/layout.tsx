import type { Metadata } from 'next'
import './globals.css'
import { geistSans, geistMono } from './fonts' // ✅ now this exists

export const metadata: Metadata = {
	title: 'Shopify AI Chatbot',
	description: 'Next.js + FastAPI + Shopify Admin API + OpenAI',
}

export default function RootLayout({
	children,
}: {
	children: React.ReactNode
}) {
	return (
		<html lang='en'>
			<body
				className={`${geistSans.variable} ${geistMono.variable} antialiased`}
			>
				<div className='min-h-screen text-zinc-100 bg-gradient-to-b from-[#0b2a45] via-[#0f3c6a] to-[#061a2c]'>
					{children}
				</div>
			</body>
		</html>
	)
}
