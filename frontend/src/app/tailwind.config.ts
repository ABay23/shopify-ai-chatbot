import type { Config } from 'tailwindcss'
const config: Config = {
	theme: {
		extend: {
			colors: {
				brandblue: {
					900: '#0b2a45',
					700: '#0f3c6a',
					950: '#061a2c',
				},
			},
		},
	},
}
export default config
// tailwind.config.ts
// import type { Config } from 'tailwindcss'
// export default {
// 	content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
// 	theme: {
// 		extend: {
// 			colors: {
// 				brandblue: {
// 					900: '#0b2a45',
// 					700: '#0f3c6a',
// 					950: '#061a2c',
// 				},
// 			},
// 		},
// 	},
// 	plugins: [],
// } satisfies Config
