// app/page.tsx (Server Component)
import Image from 'next/image'
import ChatBox from './components/ChatBox'

export const dynamic = 'force-dynamic'

type Product = {
	id: number
	title: string
	price?: string // change to number if backend returns numeric
	image?: string
}

type ProductsResponse = { products: Product[] }

const BASE =
	process.env.BACKEND_URL ??
	process.env.NEXT_PUBLIC_BACKEND_URL ??
	'http://127.0.0.1:8000'

const fmt = new Intl.NumberFormat('en-US', {
	style: 'currency',
	currency: 'USD',
})

async function getProducts(limit = 12): Promise<ProductsResponse> {
	const res = await fetch(`${BASE}/products_simple?limit=${limit}`, {
		cache: 'no-store',
	})
	if (!res.ok) {
		const txt = await res.text().catch(() => '')
		throw new Error(
			`Failed to fetch products: ${res.status} ${res.statusText} ${txt.slice(
				0,
				200
			)}`
		)
	}
	return (await res.json()) as ProductsResponse
}

export default async function HomePage() {
	const { products } = await getProducts(12)

	return (
		<main className='p-6 space-y-6'>
			<h1 className='text-2xl font-bold'>Shopify AI Chatbot</h1>

			{products.length === 0 ? (
				<div className='opacity-70'>No products yet.</div>
			) : (
				<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
					{products.map((p) => (
						<li key={p.id} className='border rounded-lg p-3'>
							{p.image ? (
								<Image
									src={p.image}
									alt={p.title}
									width={96}
									height={96}
									className='w-24 h-24 object-cover mb-2 rounded'
								/>
							) : (
								<div className='w-24 h-24 mb-2 rounded bg-white/10 flex items-center justify-center text-xs opacity-60'>
									no image
								</div>
							)}
							<div className='font-medium'>{p.title}</div>
							{p.price ? (
								<div className='text-sm opacity-75'>
									{fmt.format(Number(p.price))}
								</div>
							) : (
								<div className='text-sm opacity-50'>—</div>
							)}
						</li>
					))}
				</ul>
			)}
			<ChatBox />
		</main>
	)
}
