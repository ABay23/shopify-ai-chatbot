// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
	images: {
		domains: ['cdn.shopify.com'], // allow Shopify CDN for <Image />
	},
}

export default nextConfig
