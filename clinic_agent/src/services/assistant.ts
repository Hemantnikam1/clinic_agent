import { API_BASE_URL, getSessionId } from './api';

export const getAssistantResponse = async (userMessage: string, agentPersona: string): Promise<string> => {
  const session_id = getSessionId();
  const response = await fetch(`${API_BASE_URL}/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: userMessage, session_id, agent_persona: agentPersona }),
  });
  const data = await response.json();
  // Extract the assistant message from the nested response object
  return data.response?.llm_response || data.response?.final_response || '';
};

/**
 * Sends an audio blob to the backend and receives an audio blob response.
 * @param audioBlob The user's recorded audio.
 * @param agentPersona The selected agent persona.
 * @returns A promise that resolves to an audio Blob from the server.
 */
export const getAssistantVoiceResponse = async (audioBlob: Blob, agentPersona: string): Promise<Blob> => {
  const session_id = getSessionId() || '';
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.webm');
  formData.append('session_id', session_id);
  formData.append('agent_persona', agentPersona);

  const response = await fetch(`${API_BASE_URL}/voice`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    // Handle potential errors from the server, like model loading failures
    const errorText = await response.text();
    console.error("Error from voice endpoint:", errorText);
    throw new Error(`Server responded with status: ${response.status}`);
  }

  // The response from the /voice endpoint is the audio file itself
  const responseAudioBlob = await response.blob();
  return responseAudioBlob;
};
