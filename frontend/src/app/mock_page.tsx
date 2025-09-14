//* app/page.tsx

type Product = { id: number; title: string }
const BASE = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://127.0.0.1:8000'

export default async function HomePage() {
	const res = await fetch(`${BASE}/products_simple?limit=6`, {
		cache: 'no-store',
	})
	const { products } = await res.json()
	return (
		<main className='p-6'>
			<h1 className='text-2xl font-bold'>Shopify AI Chatbot</h1>
			<ul className='mt-4 space-y-2'>
				{products.map((p: Product) => (
					<li key={p.id}>{p.title}</li>
				))}
			</ul>
		</main>
	)
}
