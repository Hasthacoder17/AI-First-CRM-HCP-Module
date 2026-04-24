import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hcpId: '',
  hcpName: '',
  dateTime: new Date().toISOString().slice(0, 16),
  interactionType: 'in_person',
  topicsDiscussed: '',
  sentiment: 'neutral',
  followUpActions: [],
  attendees: [],
  materials: [],
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    setField(state, action) {
      const { field, value } = action.payload;
      state[field] = value;
    },
    setInteractionData(state, action) {
      const data = action.payload;
      if (data.hcp_id !== undefined) state.hcpId = data.hcp_id;
      if (data.hcpName !== undefined) state.hcpName = data.hcpName;
      if (data.date_time !== undefined) state.dateTime = data.date_time;
      if (data.interaction_type !== undefined) state.interactionType = data.interaction_type;
      if (data.topics_discussed !== undefined) state.topicsDiscussed = data.topics_discussed;
      if (data.hcp_sentiment !== undefined) state.sentiment = data.hcp_sentiment;
      if (data.follow_up_actions !== undefined) state.followUpActions = data.follow_up_actions;
      if (data.attendees !== undefined) state.attendees = data.attendees;
      if (data.materials !== undefined) state.materials = data.materials;
    },
    addFollowUpAction(state, action) {
      state.followUpActions.push(action.payload);
    },
    removeFollowUpAction(state, action) {
      state.followUpActions.splice(action.payload, 1);
    },
    addAttendee(state, action) {
      state.attendees.push(action.payload || { name: '', role: '' });
    },
    removeAttendee(state, action) {
      state.attendees.splice(action.payload, 1);
    },
    addMaterial(state, action) {
      state.materials.push(action.payload || { materialName: '', quantity: 1, materialType: '' });
    },
    removeMaterial(state, action) {
      state.materials.splice(action.payload, 1);
    },
    resetForm(state) {
      Object.assign(state, initialState);
    },
  },
});

export const {
  setField,
  setInteractionData,
  addFollowUpAction,
  removeFollowUpAction,
  addAttendee,
  removeAttendee,
  addMaterial,
  removeMaterial,
  resetForm,
} = interactionSlice.actions;

export default interactionSlice.reducer;
