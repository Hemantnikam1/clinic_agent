import { API_BASE_URL, getSessionId } from './api';

export const getAssistantResponse = async (userMessage: string): Promise<string> => {
  const session_id = getSessionId();
  const response = await fetch(`${API_BASE_URL}/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: userMessage, session_id }),
  });
  const data = await response.json();
  // Extract the assistant message from the nested response object
  return data.response?.llm_response ||data.response?.final_response|| '';
}; 