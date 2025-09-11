'use client'

import { useState } from 'react'

type Role = 'user' | 'assistant'
type Msg = { role: Role; content: string }
type ChatResponse = { answer: string }

const backend = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'

function getErrorMessage(err: unknown): string {
	if (err instanceof Error) return err.message
	if (typeof err === 'string') return err
	try {
		return JSON.stringify(err)
	} catch {
		return 'Unknown error'
	}
}

// app/page.tsx – add this near the products list
async function getOrdersToday() {
	const base =
		process.env.BACKEND_URL ??
		process.env.NEXT_PUBLIC_BACKEND_URL ??
		'http://127.0.0.1:8000'
	const res = await fetch(`${base}/orders_today`, { cache: 'no-store' })
	if (!res.ok) return { count: 0, revenue: 0 }
	return res.json() as Promise<{ count: number; revenue: number }>
}

export default async function HomePage() {
	const [{ products }, kpi] = await Promise.all([
		getProducts(8),
		getOrdersToday(),
	])
	// render two small cards for Orders Today / Revenue Today if you want
}

export default function ChatBox() {
	const [msgs, setMsgs] = useState<Msg[]>([])
	const [input, setInput] = useState<string>('')
	const [loading, setLoading] = useState<boolean>(false)

	async function onSend(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault()
		const q = input.trim()
		if (!q) return

		setInput('')
		setMsgs((m) => [...m, { role: 'user', content: q }])
		setLoading(true)

		try {
			const res = await fetch(`${backend}/chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ question: q }),
			})
			if (!res.ok) throw new Error(`HTTP ${res.status}`)

			const data: ChatResponse = await res.json()
			const answer = data?.answer ?? 'No answer.'
			setMsgs((m) => [...m, { role: 'assistant', content: answer }])
		} catch (err: unknown) {
			setMsgs((m) => [
				...m,
				{ role: 'assistant', content: `Error: ${getErrorMessage(err)}` },
			])
		} finally {
			setLoading(false)
		}
	}

	return (
		<section className='max-w-2xl space-y-4'>
			<div className='border rounded-lg p-3 h-72 overflow-auto'>
				{msgs.length === 0 ? (
					<div className='opacity-60'>Ask about products or orders…</div>
				) : (
					msgs.map((m, i) => (
						<div key={i} className='mb-2'>
							<b>{m.role === 'user' ? 'You' : 'Assistant'}:</b>{' '}
							<span className='whitespace-pre-wrap'>{m.content}</span>
						</div>
					))
				)}
			</div>

			<form onSubmit={onSend} className='flex gap-2'>
				<input
					value={input}
					onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
						setInput(e.target.value)
					}
					className='flex-1 border rounded-lg px-3 py-2'
					placeholder='e.g., "What is my top-selling product?"'
					disabled={loading}
				/>
				<button
					type='submit'
					disabled={loading}
					className='border rounded-lg px-4 py-2 disabled:opacity-50'
				>
					{loading ? 'Thinking…' : 'Send'}
				</button>
			</form>
		</section>
	)
}
