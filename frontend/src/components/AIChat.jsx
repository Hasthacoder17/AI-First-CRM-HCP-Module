import { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { setInteractionData } from '../store/interactionSlice'

function AIChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const dispatch = useDispatch()
  const interaction = useSelector((state) => state.interaction)

  const extractInteractionData = (text) => {
    const data = {}
    const hcpIdMatch = text.match(/hcp[_\s]*id["\s]*:?\s*(\d+)/i)
    if (hcpIdMatch) data.hcp_id = Number(hcpIdMatch[1])

    const dateMatch = text.match(/date[_\s]*time["\s]*:?\s*["']([^"']+)["']/i)
    if (dateMatch) data.date_time = dateMatch[1]

    const typeMatch = text.match(/interaction[_\s]*type["\s]*:?\s*["']?(in_person|virtual|phone)["']?/i)
    if (typeMatch) data.interaction_type = typeMatch[1]

    const topicsMatch = text.match(/topics[_\s]*discussed["\s]*:?\s*["']([^"']+)["']/i)
    if (topicsMatch) data.topics_discussed = topicsMatch[1]

    const sentimentMatch = text.match(/hcp[_\s]*sentiment["\s]*:?\s*["']?(positive|neutral|negative)["']?/i)
    if (sentimentMatch) data.hcp_sentiment = sentimentMatch[1]

    return Object.keys(data).length > 0 ? data : null
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      })

      const result = await response.json()
      const aiContent = result.response || 'No response'

      setMessages((prev) => [...prev, { role: 'assistant', content: aiContent }])

      const extractedData = extractInteractionData(aiContent)
      if (extractedData) {
        dispatch(setInteractionData(extractedData))
      }
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Error: ' + error.message }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="text-lg font-semibold text-gray-800">AI Assistant</h2>
        <p className="text-xs text-gray-500">Describe your interaction and I'll log it for you</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p>No messages yet</p>
            <p className="text-sm">Ask me to log an interaction with an HCP</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-4 py-2 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-br-sm'
                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 px-4 py-2 rounded-lg rounded-bl-sm">
              <p className="text-sm text-gray-500">Thinking...</p>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Describe your interaction..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Form data synced: {interaction.hcpName || 'No HCP'} | {interaction.interactionType}
        </p>
      </div>
    </div>
  )
}

export default AIChat
