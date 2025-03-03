import { useState, useRef, ChangeEvent, KeyboardEvent } from 'react';
import { MdAttachFile, MdSend, MdKeyboardVoice } from 'react-icons/md';

interface InputAreaProps {
  onSendMessage: (message: string, file?: File | null) => void;
  isProcessing: boolean;
}

export default function InputArea({ onSendMessage, isProcessing }: InputAreaProps) {
  const [message, setMessage] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSend = () => {
    if (message.trim() || file) {
      onSendMessage(message, file);
      setMessage('');
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-area">
      <button
        className="p-2 rounded-full hover:bg-gray-100 transition-colors"
        onClick={() => fileInputRef.current?.click()}
        disabled={isProcessing}
        aria-label="Attach file"
      >
        <MdAttachFile className="text-gray-500" />
      </button>
      
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.png,.jpg,.jpeg"
        disabled={isProcessing}
      />
      
      {file && (
        <div className="text-xs px-2 py-1 bg-gray-100 rounded-full">
          {file.name.length > 20 ? `${file.name.substring(0, 17)}...` : file.name}
        </div>
      )}
      
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        className="flex-1 outline-none text-gray-700"
        placeholder="Type your message..."
        disabled={isProcessing}
      />
      
      <button
        className="p-2 rounded-full hover:bg-gray-100 transition-colors"
        aria-label="Voice input"
        disabled={isProcessing}
      >
        <MdKeyboardVoice className="text-gray-500" />
      </button>
      
      <button
        className="p-2 rounded-full bg-primary text-white hover:bg-opacity-90 transition-colors"
        onClick={handleSend}
        disabled={isProcessing || (!message.trim() && !file)}
        aria-label="Send message"
      >
        <MdSend />
      </button>
    </div>
  );
} 