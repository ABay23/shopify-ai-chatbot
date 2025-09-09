'use client'

import { useEffect, useState } from 'react'

type Product = { id: number; title: string; price?: string; imege?: string }

const backendUrl =
	process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function ProductGrid() {
	const [items, setItems] = useState<Product[]>([])
	const [loading, setLoading] = useState(true)

	useEffect(() => {})
}
