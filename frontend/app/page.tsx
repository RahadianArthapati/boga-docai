'use client';

import { useState, useEffect } from 'react';
import Header from './components/Header';
import Message, { MessageProps } from './components/Message';
import QuickReplies from './components/QuickReplies';
import InputArea from './components/InputArea';
import { apiService } from './services/api';

// Define message type
interface MessageWithId extends Omit<MessageProps, 'timestamp'> {
  id: string;
  timestamp: Date;
}

// Default quick replies
const DEFAULT_QUICK_REPLIES = [
  'How does this work?',
  'Tell me about your features',
  'Can you help with my project?',
  'I need technical support'
];

export default function Home() {
  const [messages, setMessages] = useState<MessageWithId[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fileResults, setFileResults] = useState<Record<string, any>>({});
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [backendStatus, setBackendStatus] = useState<{success: boolean, error?: string}>({ success: true });

  // Check backend status on mount
  useEffect(() => {
    const checkBackend = async () => {
      const status = await apiService.checkBackendStatus();
      setBackendStatus(status);
      
      if (!status.success) {
        addAIMessage(`⚠️ ${status.error || 'Cannot connect to the backend server. Please ensure it is running.'}`);
      }
    };
    
    checkBackend();
  }, []);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          content: "Hi there! I'm your friendly AI assistant. How can I help you today?",
          role: 'assistant',
          timestamp: new Date()
        }
      ]);
    }
  }, [messages]);

  // Toggle dark/light theme
  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
    // In a real implementation, this would apply theme classes to the body
  };

  // Clear chat history
  const clearChat = () => {
    setMessages([
      {
        id: 'welcome',
        content: "Hi there! I'm your friendly AI assistant. How can I help you today?",
        role: 'assistant',
        timestamp: new Date()
      }
    ]);
    setFileResults({});
  };

  // Handle sending message
  const handleSendMessage = async (message: string, file?: File | null) => {
    if (!message.trim() && !file) return;

    // Check backend status before sending
    if (!backendStatus.success) {
      const status = await apiService.checkBackendStatus();
      setBackendStatus(status);
      
      if (!status.success) {
        addAIMessage(`⚠️ ${status.error || 'Cannot connect to the backend server. Please ensure it is running.'}`);
        return;
      }
    }

    // Add user message to chat
    const userMessageId = `user-${Date.now()}`;
    const userMessage: MessageWithId = {
      id: userMessageId,
      content: message,
      role: 'user',
      timestamp: new Date(),
      ...(file && { attachment: { name: file.name, type: file.type } })
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Process file if present
    if (file) {
      setIsProcessing(true);
      
      try {
        // Upload file to backend
        const result = await apiService.uploadFile(file);
        
        if (result.success) {
          const fileId = result.file_id;
          setFileResults(prev => ({ ...prev, [fileId]: result }));
          
          // Add AI response messages
          addAIMessage(`I've processed your document: **${file.name}**`);
          
          // Show extracted data
          const extractedText = result.extracted_text;
          if (extractedText && extractedText.length > 300) {
            const shortText = extractedText.substring(0, 300) + '...';
            addAIMessage(`Here's a preview of the extracted text:\n\n${shortText}`);
          }
          
          // Show structured data
          const jsonData = result.json_result;
          if (jsonData) {
            addAIMessage(`I've extracted the following structured data from your document:\n\`\`\`json\n${JSON.stringify(jsonData, null, 2).substring(0, 500)}\n\`\`\``);
          }
          
          addAIMessage("Is there anything specific you'd like to know about this document?");
        } else {
          const error = result.error || 'Unknown error occurred';
          
          if (error.includes('Network Error')) {
            setBackendStatus({ success: false, error });
            addAIMessage(`⚠️ ${error}`);
            addAIMessage("The backend server appears to be offline. Please make sure it's running at the correct URL and try again.");
          } else {
            addAIMessage(`Sorry, I couldn't process your document: ${error}`);
          }
          
          if (error.toLowerCase().includes('poppler')) {
            addAIMessage(`It looks like Poppler is not installed. This is required for PDF processing.
            
Please install it:
- macOS: \`brew install poppler\`
- Ubuntu/Debian: \`sudo apt-get install poppler-utils\`
- Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/`);
          }
        }
      } catch (error) {
        addAIMessage(`Sorry, an error occurred while processing your document: ${error instanceof Error ? error.message : 'Unknown error'}`);
      } finally {
        setIsProcessing(false);
      }
    } else if (message.trim()) {
      // Process text message
      setIsProcessing(true);
      
      try {
        // Simulate thinking
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simple responses for demo
        const responses = [
          "I'm analyzing your question...",
          "That's an interesting point about the document.",
          "Let me check the extracted data to answer that.",
          "Would you like to upload another document to compare?",
          "Is there anything specific you'd like me to explain about the document structure?"
        ];
        
        // Add random AI response (in a real app, this would call the backend API)
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addAIMessage(randomResponse);
      } catch (error) {
        addAIMessage(`Sorry, an error occurred while processing your message: ${error instanceof Error ? error.message : 'Unknown error'}`);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  // Helper for adding AI messages
  const addAIMessage = (content: string) => {
    const aiMessageId = `ai-${Date.now()}`;
    setMessages(prev => [
      ...prev,
      {
        id: aiMessageId,
        content,
        role: 'assistant',
        timestamp: new Date()
      }
    ]);
  };

  // Handle quick reply click
  const handleQuickReplyClick = (reply: string) => {
    handleSendMessage(reply, null);
  };

  // Check if we should show quick replies (after AI message)
  const showQuickReplies = messages.length > 0 && messages[messages.length - 1].role === 'assistant';

  return (
    <main className={`flex flex-col p-4 h-screen ${isDarkMode ? 'bg-gray-900 text-white' : ''}`}>
      <div className="max-w-4xl w-full mx-auto flex flex-col h-full">
        <Header clearChat={clearChat} toggleTheme={toggleTheme} />
        
        {!backendStatus.success && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
            <p className="font-bold">Backend Connection Error</p>
            <p>{backendStatus.error || 'Cannot connect to backend server'}</p>
            <p className="text-sm mt-1">
              Make sure the backend is running at {process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}
            </p>
          </div>
        )}
        
        <div className="flex-1 overflow-y-auto mb-4 pr-2">
          {messages.map(message => (
            <Message
              key={message.id}
              content={message.content}
              role={message.role}
              timestamp={message.timestamp}
              attachment={message.attachment}
            />
          ))}
          
          {showQuickReplies && (
            <QuickReplies
              replies={DEFAULT_QUICK_REPLIES}
              onReplyClick={handleQuickReplyClick}
            />
          )}
        </div>
        
        <InputArea
          onSendMessage={handleSendMessage}
          isProcessing={isProcessing}
        />
      </div>
    </main>
  );
} 