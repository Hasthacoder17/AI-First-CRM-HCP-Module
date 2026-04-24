import { useSelector, useDispatch } from 'react-redux'
import { resetForm } from '../store/interactionSlice'
import { useState } from 'react'

function InteractionForm() {
  const interaction = useSelector((state) => state.interaction)
  const dispatch = useDispatch()
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    const text = `HCP: ${interaction.hcpName || 'N/A'}
Date: ${interaction.dateTime || 'N/A'}
Type: ${interaction.interactionType}
Sentiment: ${interaction.sentiment}
Topics: ${interaction.topicsDiscussed || 'N/A'}
Attendees: ${interaction.attendees.map(a => a.name).join(', ') || 'None'}
Materials: ${interaction.materials.map(m => m.materialName).join(', ') || 'None'}
Follow-ups: ${interaction.followUpActions.join('; ') || 'None'}`
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">Interaction Details</h2>
        <span className="text-xs text-gray-400">AI-Controlled</span>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-700">
        This form is controlled by the AI Assistant. Describe your interaction in the chat panel to populate this form.
      </div>

      {/* HCP Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">HCP Name</label>
        <input
          type="text"
          value={interaction.hcpName}
          readOnly
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
        />
      </div>

      {/* HCP ID */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">HCP ID</label>
        <input
          type="number"
          value={interaction.hcpId}
          readOnly
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
        />
      </div>

      {/* Date/Time */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Date & Time</label>
        <input
          type="datetime-local"
          value={interaction.dateTime}
          readOnly
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
        />
      </div>

      {/* Interaction Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Interaction Type</label>
        <select
          value={interaction.interactionType}
          disabled
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
        >
          <option value="in_person">In Person</option>
          <option value="virtual">Virtual</option>
          <option value="phone">Phone</option>
        </select>
      </div>

      {/* Topics Discussed */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Topics Discussed</label>
        <textarea
          value={interaction.topicsDiscussed}
          readOnly
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
          placeholder="AI will populate this field..."
        />
      </div>

      {/* Attendees */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Attendees</label>
        {interaction.attendees.length === 0 ? (
          <p className="text-sm text-gray-400">No attendees added yet</p>
        ) : (
          <div className="space-y-2">
            {interaction.attendees.map((attendee, index) => (
              <div key={index} className="flex gap-2 text-sm text-gray-700">
                <span className="font-medium">{attendee.name}</span>
                {attendee.role && <span className="text-gray-400">({attendee.role})</span>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Materials Shared */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Materials Shared</label>
        {interaction.materials.length === 0 ? (
          <p className="text-sm text-gray-400">No materials logged yet</p>
        ) : (
          <div className="space-y-2">
            {interaction.materials.map((material, index) => (
              <div key={index} className="flex gap-2 text-sm text-gray-700">
                <span>{material.materialName}</span>
                <span className="text-gray-400">x{material.quantity}</span>
                {material.materialType && <span className="text-gray-400">({material.materialType})</span>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* HCP Sentiment */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">HCP Sentiment</label>
        <div className="flex gap-4">
          {['positive', 'neutral', 'negative'].map((sentiment) => (
            <label key={sentiment} className={`flex items-center gap-2 ${interaction.sentiment === sentiment ? 'font-semibold' : ''}`}>
              <input
                type="radio"
                name="sentiment"
                value={sentiment}
                checked={interaction.sentiment === sentiment}
                disabled
                className="text-blue-600"
              />
              <span className="capitalize">{sentiment}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Follow-up Actions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Follow-up Actions</label>
        {interaction.followUpActions.length === 0 ? (
          <p className="text-sm text-gray-400">No follow-up actions yet</p>
        ) : (
          <ul className="list-disc list-inside space-y-1">
            {interaction.followUpActions.map((action, index) => (
              <li key={index} className="text-sm text-gray-700">{action}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Buttons */}
      <div className="flex gap-4 pt-4">
        <button
          onClick={handleCopy}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          {copied ? 'Copied!' : 'Copy Details'}
        </button>
        <button
          onClick={() => dispatch(resetForm())}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
        >
          Reset Form
        </button>
      </div>
    </div>
  )
}

export default InteractionForm
