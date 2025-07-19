import React from 'react';
import { InputGroup, FormControl, Button } from 'react-bootstrap';
import { BsPaperclip, BsMic } from 'react-icons/bs';

interface ChatInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSend: () => void;
  onAttach: () => void;
  onVoice: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ value, onChange, onSend, onAttach, onVoice }) => (
  <InputGroup className="rounded shadow-sm" style={{ background: '#fff' }}>
    <Button variant="outline-secondary" onClick={onAttach} className="d-flex align-items-center">
      <BsPaperclip size={20} />
    </Button>
    <FormControl
      placeholder="Type a message..."
      value={value}
      onChange={onChange}
      onKeyDown={e => { if (e.key === 'Enter') onSend(); }}
      className="border-0"
      style={{ background: '#f4f6fb' }}
    />
    <Button variant="outline-secondary" onClick={onVoice} className="d-flex align-items-center">
      <BsMic size={20} />
    </Button>
    <Button variant="primary" onClick={onSend} className="px-4">
      Send
    </Button>
  </InputGroup>
);

export default ChatInput; 