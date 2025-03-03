import { format } from 'date-fns';
import { ReactNode } from 'react';

export interface MessageProps {
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  attachment?: {
    name: string;
    type: string;
  };
}

export default function Message({ content, role, timestamp, attachment }: MessageProps) {
  const messageClass = role === 'user' ? 'user-message' : 'ai-message';
  const formattedTime = format(timestamp, 'h:mm a');
  const sender = role === 'user' ? 'You' : 'AI';

  return (
    <div className={`chat-message ${messageClass}`}>
      <div className="flex justify-between mb-2">
        <span className="font-bold">{sender}</span>
        <span className="text-xs opacity-80">{formattedTime}</span>
      </div>
      <div className="whitespace-pre-wrap">{content}</div>
      
      {attachment && (
        <div className="mt-2 p-2 bg-black/10 rounded-md">
          <div className="flex items-center">
            <span className="mr-2">📎</span>
            <span>{attachment.name}</span>
          </div>
        </div>
      )}
    </div>
  );
} 