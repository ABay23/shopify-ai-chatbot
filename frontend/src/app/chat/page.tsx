// app/chat/page.tsx

import ChatBox from '../components/ChatBox'

export default function ChatPage() {
	return (
		<main className='p-6 space-y-6'>
			<h1 className='text-2xl font-bold'>Chat</h1>
			<ChatBox />
		</main>
	)
}
