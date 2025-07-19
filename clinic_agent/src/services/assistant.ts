import { sendMessageToApi } from './api';

export const getAssistantResponse = async (userMessage: string): Promise<string> => {
  // Use the API function to get a response
  const response = await sendMessageToApi(userMessage);
  return response;
}; 