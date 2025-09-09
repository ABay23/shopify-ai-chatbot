'use client'

import { useEffect, useState } from 'react'

export default function Home() {
	const [message, setMessage] = useState('')

	useEffect(() => {
		fetch('http://localhost:8000/ping')
			.then((res) => res.json())
			.then((data) => setMessage(data.message))
	}, [])

	return (
		<main className='p-6'>
			<h1 className='text-2xl font-bold'>Shopify AI Chatbot</h1>
			<p>Backend says: {message}</p>
		</main>
	)
}
