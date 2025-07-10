import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatBox.css';

function ChatBox({ user }) {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const chatWindowRef = useRef(null);

  const scrollToBottom = () => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!prompt.trim() || isLoading) return;

    const userMessage = { from: 'user', text: prompt };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setPrompt('');
    setIsLoading(true);

    try {
      const response = await axios.post('https://agentic-health-assistant-fupm.onrender.com/api/agent', {
        prompt,
        user,
        chat_history: updatedMessages.map(msg => ({
          role: msg.from === 'user' ? 'user' : 'assistant',
          content: msg.text,
        })),
      });

      const assistantMessage = {
        from: 'assistant',
        text: response.data?.response || 'No response from assistant.',
      };
      setMessages([...updatedMessages, assistantMessage]);
    } catch (err) {
      setMessages([
        ...updatedMessages,
        { from: 'assistant', text: 'Error contacting assistant.' },
      ]);
      console.error('Assistant error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbox">
      <div className="chat-window" ref={chatWindowRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.from}`}>
            <b>{msg.from === 'user' ? 'You' : 'Assistant'}:</b> {msg.text}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <b>Assistant:</b> <em>Typing...</em>
          </div>
        )}
      </div>

      <div className="chat-input">
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything..."
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !prompt.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatBox;
