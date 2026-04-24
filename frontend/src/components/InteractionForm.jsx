import { useSelector, useDispatch } from 'react-redux'
import { setField, addFollowUpAction, removeFollowUpAction, addAttendee, removeAttendee, addMaterial, removeMaterial, resetForm } from '../store/interactionSlice'
import { useState } from 'react'

function InteractionForm() {
  const interaction = useSelector((state) => state.interaction)
  const dispatch = useDispatch()
  const [saving, setSaving] = useState(false)

  const handleChange = (field) => (e) => {
    dispatch(setField({ field, value: e.target.value }))
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const response = await fetch('http://localhost:8000/api/interactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hcp_id: Number(interaction.hcpId),
          date_time: interaction.dateTime,
          interaction_type: interaction.interactionType,
          topics_discussed: interaction.topicsDiscussed,
          hcp_sentiment: interaction.sentiment,
          follow_up_actions: interaction.followUpActions,
          attendees: interaction.attendees.filter(a => a.name),
          materials: interaction.materials.filter(m => m.materialName),
        }),
      })
      if (response.ok) {
        alert('Interaction saved successfully!')
      }
    } catch (error) {
      alert('Error saving interaction: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-xl font-semibold text-gray-800">Interaction Details</h2>

      {/* HCP Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">HCP Name</label>
        <input
          type="text"
          value={interaction.hcpName}
          onChange={handleChange('hcpName')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter HCP name"
        />
      </div>

      {/* HCP ID */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">HCP ID</label>
        <input
          type="number"
          value={interaction.hcpId}
          onChange={handleChange('hcpId')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter HCP ID"
        />
      </div>

      {/* Date/Time */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Date & Time</label>
        <input
          type="datetime-local"
          value={interaction.dateTime}
          onChange={handleChange('dateTime')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Interaction Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Interaction Type</label>
        <select
          value={interaction.interactionType}
          onChange={handleChange('interactionType')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
          onChange={handleChange('topicsDiscussed')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter topics discussed..."
        />
      </div>

      {/* Attendees */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Attendees</label>
        {interaction.attendees.map((attendee, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={attendee.name}
              onChange={(e) => {
                const updated = [...interaction.attendees]
                updated[index] = { ...updated[index], name: e.target.value }
                dispatch(setField({ field: 'attendees', value: updated }))
              }}
              placeholder="Name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <input
              type="text"
              value={attendee.role || ''}
              onChange={(e) => {
                const updated = [...interaction.attendees]
                updated[index] = { ...updated[index], role: e.target.value }
                dispatch(setField({ field: 'attendees', value: updated }))
              }}
              placeholder="Role"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <button onClick={() => dispatch(removeAttendee(index))} className="px-3 py-2 bg-red-500 text-white rounded-md">×</button>
          </div>
        ))}
        <button onClick={() => dispatch(addAttendee())} className="text-sm text-blue-600 hover:underline">+ Add Attendee</button>
      </div>

      {/* Materials Shared */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Materials Shared</label>
        {interaction.materials.map((material, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={material.materialName}
              onChange={(e) => {
                const updated = [...interaction.materials]
                updated[index] = { ...updated[index], materialName: e.target.value }
                dispatch(setField({ field: 'materials', value: updated }))
              }}
              placeholder="Material Name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <input
              type="number"
              value={material.quantity}
              onChange={(e) => {
                const updated = [...interaction.materials]
                updated[index] = { ...updated[index], quantity: Number(e.target.value) }
                dispatch(setField({ field: 'materials', value: updated }))
              }}
              placeholder="Qty"
              className="w-20 px-3 py-2 border border-gray-300 rounded-md"
            />
            <input
              type="text"
              value={material.materialType || ''}
              onChange={(e) => {
                const updated = [...interaction.materials]
                updated[index] = { ...updated[index], materialType: e.target.value }
                dispatch(setField({ field: 'materials', value: updated }))
              }}
              placeholder="Type"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <button onClick={() => dispatch(removeMaterial(index))} className="px-3 py-2 bg-red-500 text-white rounded-md">×</button>
          </div>
        ))}
        <button onClick={() => dispatch(addMaterial())} className="text-sm text-blue-600 hover:underline">+ Add Material</button>
      </div>

      {/* HCP Sentiment */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">HCP Sentiment</label>
        <div className="flex gap-4">
          {['positive', 'neutral', 'negative'].map((sentiment) => (
            <label key={sentiment} className="flex items-center gap-2">
              <input
                type="radio"
                name="sentiment"
                value={sentiment}
                checked={interaction.sentiment === sentiment}
                onChange={handleChange('sentiment')}
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
        {interaction.followUpActions.map((action, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={action}
              onChange={(e) => {
                const updated = [...interaction.followUpActions]
                updated[index] = e.target.value
                dispatch(setField({ field: 'followUpActions', value: updated }))
              }}
              placeholder="Action item"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <button onClick={() => dispatch(removeFollowUpAction(index))} className="px-3 py-2 bg-red-500 text-white rounded-md">×</button>
          </div>
        ))}
        <button onClick={() => dispatch(addFollowUpAction(''))} className="text-sm text-blue-600 hover:underline">+ Add Action</button>
      </div>

      {/* Buttons */}
      <div className="flex gap-4 pt-4">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Interaction'}
        </button>
        <button
          onClick={() => dispatch(resetForm())}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
        >
          Reset
        </button>
      </div>
    </div>
  )
}

export default InteractionForm
