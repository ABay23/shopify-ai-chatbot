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
// app/layout.tsx
// import type { Metadata } from 'next'
// import './globals.css'
// import { geistSans, geistMono } from './fonts' // if you created fonts.ts

// export const metadata: Metadata = {
// 	title: 'Shopify AI Chatbot',
// 	description: 'Next.js + FastAPI + Shopify Admin API + OpenAI',
// }

// export default function RootLayout({
// 	children,
// }: {
// 	children: React.ReactNode
// }) {
// 	return (
// 		<html lang='en'>
// 			<body
// 				className={`${geistSans.variable} ${geistMono.variable} antialiased`}
// 			>
// 				{/* ⬇️ THIS is the wrapper div */}
// 				<div className='min-h-screen text-zinc-100 bg-gradient-to-b from-brandblue-900 via-brandblue-700 to-brandblue-950'>
// 					{children}
// 				</div>
// 			</body>
// 		</html>
// 	)
// }
