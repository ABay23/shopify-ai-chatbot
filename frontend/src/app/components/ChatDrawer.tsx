'use client'

import { useEffect, useState } from 'react'
import ChatBox from './ChatBox' // your existing component

export default function ChatDrawer() {
	const [open, setOpen] = useState(false)

	// Keyboard: ⌘/Ctrl+K opens, Esc closes
	useEffect(() => {
		function onKey(e: KeyboardEvent) {
			if (e.key === 'Escape') setOpen(false)
			if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) {
				e.preventDefault()
				setOpen(true)
			}
		}
		window.addEventListener('keydown', onKey)
		return () => window.removeEventListener('keydown', onKey)
	}, [])

	return (
		<>
			{/* floating launcher button */}
			<button
				aria-label='Open chat'
				onClick={() => setOpen(true)}
				className='fixed bottom-6 right-6 h-14 w-14 rounded-full
                bg-gradient-to-br from-fuchsia-500 to-indigo-600
                shadow-lg border border-white/10 text-xl
                flex items-center justify-center z-40'
			>
				💬
			</button>

			{/* overlay + drawer */}
			<div
				className={`fixed inset-0 z-50 ${open ? '' : 'pointer-events-none'}`}
			>
				{/* backdrop */}
				<div
					className={`absolute inset-0 bg-gradient-to-b from-[#0b2a45]/40 via-[#0f3c6a]/40 to-[#061a2c]/40 transition-opacity duration-300
                    ${open ? 'opacity-100' : 'opacity-0'}`}
					onClick={() => setOpen(false)}
				/>
				{/* drawer panel */}
				<aside
					className={`absolute right-0 top-0 h-full w-full sm:w-[420px] md:w-[520px]
                    bg-zinc-900/40 backdrop-blur-md border-l border-white/10 shadow-2xl
                    transform transition-transform duration-300
                    ${open ? 'translate-x-0' : 'translate-x-full'}`}
					role='dialog'
					aria-modal='true'
				>
					<div
						className='flex items-center justify-between px-4 py-3
                        bg-gradient-to-r from-[#0b2a45] via-[#0f3c6a] to-[#061a2c]'
					>
						<div className='font-semibold'>Shopify AI Chat</div>
						<button onClick={() => setOpen(false)} aria-label='Close'>
							✕
						</button>
					</div>
					<div className='p-4'>
						<ChatBox />
					</div>
				</aside>
			</div>
		</>
	)
}
