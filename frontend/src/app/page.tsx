// app/page.tsx (Server Component)

import Image from 'next/image'

type Product = {
	id: number
	title: string
	price?: string //* validate return from backend API first
	image?: string
}

type ProductsResponse = {
	products: Product[]
}

async function getProducts(limit = 9): Promise<ProductsResponse> {
	const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'
	const res = await fetch(`${base}/products_simple?limit=${limit}`, {
		cache: 'no-store',
	})
	if (!res.ok) {
		throw new Error(`Failed to fetch products: ${res.status} ${res.statusText}`)
	}
	// TS-only assertion (no runtime validation):
	return (await res.json()) as ProductsResponse
}

export default async function HomePage() {
	const { products } = await getProducts(12)

	return (
		<main className='p-6'>
			<h1 className='text-2xl font-bold mb-4'>Shopify AI Chatbot</h1>
			<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
				{products.map((p) => (
					<li key={p.id} className='border rounded-lg p-3'>
						{p.image && (
							<Image
								src={p.image}
								alt={p.title}
								width={96}
								height={96}
								className='w-24 h-24 object-cover mb-2 rounded'
							/>
						)}
						<div className='font-medium'>{p.title}</div>
						{p.price && <div className='text-sm opacity-75'>${p.price}</div>}
					</li>
				))}
			</ul>
		</main>
	)
}
