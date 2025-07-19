import React from 'react';
import { Card } from 'react-bootstrap';

interface UserMsgProps {
  message: string;
}

const UserMsg: React.FC<UserMsgProps> = ({ message }) => (
  <Card className="mb-2 ms-auto rounded-pill shadow-sm bg-primary text-white" style={{ maxWidth: '75%', borderRadius: '2rem' }}>
    <Card.Body className="py-2 px-3">
      <Card.Text className="mb-0">{message}</Card.Text>
    </Card.Body>
  </Card>
);

export default UserMsg; 