import React, { useState, useEffect, useRef } from 'react';
import UserMsg from '../components/UserMsg';
import AgentMsg from '../components/AgentMsg';
import ChatInput from '../components/ChatInput';
import { Container, Row, Col, Card, Spinner } from 'react-bootstrap';
import { getAssistantResponse, getAssistantVoiceResponse } from '../services/assistant';
import { getSessionId } from '../services/api';
import Recorder from 'recorder-js';
import AgentPersonaSelect from '../components/AgentPersonaSelect';

interface Message {
  sender: 'user' | 'assistant';
  text?: string;
  audioUrl?: string;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [persona, setPersona] = useState<string>('nicer');
  const recorderRef = useRef<Recorder | null>(null);

  useEffect(() => {
    const initialize = async () => {
      const newSessionId = await getSessionId();
      setSessionId(newSessionId);

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const recorder = new Recorder(audioContext, {
          onAnalysed: data => {},
        });
        recorder.init(stream);
        recorderRef.current = recorder;
      } catch (err) {
        console.error("Failed to get microphone stream:", err);
        alert("Microphone access denied. Please allow microphone access in your browser settings.");
      }
    };
    initialize();
  }, []);

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;
    const userMessage: Message = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    const assistantReply = await getAssistantResponse(input, persona);
    const assistantMessage: Message = { sender: 'assistant', text: assistantReply };
    setMessages(prev => [...prev, assistantMessage]);
    setLoading(false);
  };

  const handleVoice = async () => {
    if (!recorderRef.current) {
      alert("Recorder is not initialized. Please ensure microphone permissions are enabled.");
      return;
    }

    if (!recording) {
      try {
        await recorderRef.current.start();
        setRecording(true);
      } catch (err) {
        console.error("Could not start recording:", err);
        alert('Could not start recording.');
      }
    } else {
      try {
        setLoading(true);
        setRecording(false);
        const { blob } = await recorderRef.current.stop();
        
        // Display user's recorded audio immediately
        const userAudioUrl = URL.createObjectURL(blob);
        const userAudioMessage: Message = { sender: 'user', audioUrl: userAudioUrl };
        setMessages(prev => [...prev, userAudioMessage]);
        
        // Get the audio response from the backend
        const assistantAudioBlob = await getAssistantVoiceResponse(blob, persona);
        const assistantAudioUrl = URL.createObjectURL(assistantAudioBlob);
        
        // Display the assistant's audio response
        const assistantMessage: Message = { sender: 'assistant', audioUrl: assistantAudioUrl };
        setMessages(prev => [...prev, assistantMessage]);

      } catch (err) {
        console.error("Error during voice processing:", err);
        alert(`Could not process voice command. Error: ${err}`);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <Container fluid className="d-flex flex-column justify-content-center align-items-center p-0" style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#f8f9fa' }}>
      <Row className="w-100" style={{ position: 'absolute', top: 0, right: 0, zIndex: 20, justifyContent: 'flex-end' }}>
        <Col xs="auto" className="d-flex justify-content-end align-items-center p-3">
          <AgentPersonaSelect value={persona} onChange={e => setPersona(e.target.value)} />
        </Col>
      </Row>
      <Row className="flex-grow-1 w-100 justify-content-center align-items-center" style={{ minHeight: 0 }}>
        <Col xs={12} sm={10} md={8} lg={6} className="h-100 d-flex flex-column p-0">
          <Card className="flex-grow-1 d-flex flex-column shadow-sm" style={{ height: '100%', borderRadius: 16, overflow: 'hidden' }}>
            <Card.Body className="flex-grow-1 d-flex flex-column p-3" style={{ overflowY: 'auto', background: '#f4f6fb' }}>
              {messages.map((msg, idx) => {
                // Render audio messages for both user and assistant
                if (msg.audioUrl) {
                  const justifyContent = msg.sender === 'user' ? 'justify-content-end' : 'justify-content-start';
                  return (
                    <div key={idx} className={`d-flex ${justifyContent} mb-2`}>
                      <audio controls src={msg.audioUrl} style={{ maxWidth: 240, background: '#fff', borderRadius: 12, boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }} />
                    </div>
                  );
                }
                // Render text messages
                if (msg.sender === 'user') {
                  return (
                    <div key={idx} className="d-flex justify-content-end">
                      <UserMsg message={msg.text || ''} />
                    </div>
                  );
                }
                return (
                  <div key={idx} className="d-flex justify-content-start">
                    <AgentMsg message={msg.text || ''} />
                  </div>
                );
              })}
              {loading && (
                <div className="d-flex justify-content-start align-items-center" style={{ minHeight: 40 }}>
                  <div style={{ background: '#fff', borderRadius: 12, padding: '8px 16px', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                    <Spinner animation="border" size="sm" />
                  </div>
                </div>
              )}
            </Card.Body>
            <Card.Footer className="bg-white p-3 border-0" style={{ borderTop: '1px solid #eee' }}>
              <ChatInput
                value={input}
                onChange={e => setInput(e.target.value)}
                onSend={handleSend}
                onAttach={() => {}}
                onVoice={handleVoice}
                isRecording={recording}
              />
            </Card.Footer>
            {recording && (
              <div style={{ position: 'absolute', bottom: 80, left: '50%', transform: 'translateX(-50%)', zIndex: 10, background: '#fff', padding: '8px 24px', borderRadius: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
                <span role="img" aria-label="recording">🔴 Recording...</span>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ChatPage;
