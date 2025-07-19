// Dummy API function to simulate a call to an external service
export const sendMessageToApi = async (message: string): Promise<string> => {
  // Simulate network delay
  await new Promise(res => setTimeout(res, 500));
  // Return dummy response
  return `API response to: ${message}`;
}; 