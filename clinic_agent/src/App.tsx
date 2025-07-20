import './App.css';
import ChatPage from './pages/ChatPage';
// Make sure to install uuid: npm install uuid
import { v4 as uuidv4 } from 'uuid';
import React, { createContext, useEffect, useState } from 'react';

// Create a context for session_id
export const SessionIdContext = createContext<string | undefined>(undefined);

function useSessionId() {
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);

  useEffect(() => {
    let id = sessionStorage.getItem('session_id');
    if (!id) {
      id = uuidv4();
      sessionStorage.setItem('session_id', id);
    }
    setSessionId(id || undefined);

    // Clear session_id when tab is closed
    const handleUnload = () => {
      sessionStorage.removeItem('session_id');
    };
    window.addEventListener('beforeunload', handleUnload);
    return () => {
      window.removeEventListener('beforeunload', handleUnload);
    };
  }, []);

  return sessionId;
}

function App() {
  const sessionId = useSessionId();
  return (
    <SessionIdContext.Provider value={sessionId}>
      <ChatPage />
    </SessionIdContext.Provider>
  );
}

export default App;
