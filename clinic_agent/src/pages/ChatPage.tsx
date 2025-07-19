import React, { useState } from 'react';
import UserMsg from '../components/UserMsg';
import AgentMsg from '../components/AgentMsg';
import ChatInput from '../components/ChatInput';
import { Container, Row, Col, Card } from 'react-bootstrap';

// Dummy service to simulate assistant response
const dummyAssistantReply = (userMsg: string) => {
  return `Assistant received: ${userMsg}`;
};

interface Message {
  sender: 'user' | 'assistant';
  text: string;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    const userMessage: Message = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    // Simulate assistant reply
    setTimeout(() => {
      const assistantMessage: Message = { sender: 'assistant', text: dummyAssistantReply(input) };
      setMessages(prev => [...prev, assistantMessage]);
    }, 500);
  };

  return (
    <Container fluid className="d-flex flex-column justify-content-center align-items-center p-0" style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#f8f9fa' }}>
      <Row className="flex-grow-1 w-100 justify-content-center align-items-center" style={{ minHeight: 0 }}>
        <Col xs={12} sm={10} md={8} lg={6} className="h-100 d-flex flex-column p-0">
          <Card className="flex-grow-1 d-flex flex-column shadow-sm" style={{ height: '100%', borderRadius: 16, overflow: 'hidden' }}>
            <Card.Body className="flex-grow-1 d-flex flex-column p-3" style={{ overflowY: 'auto', background: '#f4f6fb' }}>
              {messages.map((msg, idx) =>
                msg.sender === 'user' ? (
                  <div key={idx} className="d-flex justify-content-end">
                    <UserMsg message={msg.text} />
                  </div>
                ) : (
                  <div key={idx} className="d-flex justify-content-start">
                    <AgentMsg message={msg.text} />
                  </div>
                )
              )}
            </Card.Body>
            <Card.Footer className="bg-white p-3 border-0" style={{ borderTop: '1px solid #eee' }}>
              <ChatInput
                value={input}
                onChange={e => setInput(e.target.value)}
                onSend={handleSend}
                onAttach={() => {}}
                onVoice={() => {}}
              />
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ChatPage; 