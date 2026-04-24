import InteractionForm from './components/InteractionForm'
import AIChat from './components/AIChat'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">AI-First CRM HCP Module</h1>
        <p className="text-sm text-gray-500">Log Interaction Screen</p>
      </header>
      <main className="grid grid-cols-2 min-h-[calc(100vh-80px)]">
        <div className="border-r border-gray-200 bg-white overflow-y-auto">
          <InteractionForm />
        </div>
        <div className="bg-gray-50 overflow-y-auto">
          <AIChat />
        </div>
      </main>
    </div>
  )
}

export default App
