export const API_BASE_URL = 'http://127.0.0.1:8001'; 

// Helper to get the session_id from sessionStorage
export function getSessionId(): string | null {
  return sessionStorage.getItem('session_id');
}

// Example usage in API call:
// Instead of passing session_id from component, always use getSessionId()
// For example, in your sendMessage or similar function:
//
// export async function sendMessage(message: string) {
//   const session_id = getSessionId();
//   // ...
//   await fetch('/api', { method: 'POST', body: JSON.stringify({ message, session_id }) })
// } 