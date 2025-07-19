import React from 'react';
import { Card } from 'react-bootstrap';

interface AgentMsgProps {
  message: string;
}

const AgentMsg: React.FC<AgentMsgProps> = ({ message }) => (
  <Card className="mb-2 me-auto rounded-pill shadow-sm bg-light text-dark" style={{ maxWidth: '75%', borderRadius: '2rem' }}>
    <Card.Body className="py-2 px-3">
      <Card.Text className="mb-0">{message}</Card.Text>
    </Card.Body>
  </Card>
);

export default AgentMsg; 