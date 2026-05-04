import { useState, useRef, useEffect } from 'react';
import { chatStream } from '../api';
 
const STARTERS = [
  'What is my leave balance?',
  'Apply for sick leave tomorrow',
  'Show my pending requests',
  'How many casual leaves do I have?',
];
 
export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I\'m your leave assistant. Ask me anything about your leaves, balance, or to apply for one.' }
  ]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef(null);
 
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
 
  const send = async (text) => {
    const userMsg = text || input.trim();
    if (!userMsg || streaming) return;
    setInput('');
 
    const newMessages = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setStreaming(true);
 
    // Add empty assistant message for streaming
    setMessages((m) => [...m, { role: 'assistant', content: '' }]);
 
    try {
      await chatStream(
        newMessages.map(({ role, content }) => ({ role, content })),
        (chunk) => {
          setMessages((m) => {
            const updated = [...m];
            updated[updated.length - 1] = {
              role: 'assistant',
              content: updated[updated.length - 1].content + chunk,
            };
            return updated;
          });
        }
      );
    } catch (e) {
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
        };
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  };
 
  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };
 
  return (
    <div className="chat-page">
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role === 'user' ? 'bubble-user' : 'bubble-ai'}`}>
            {m.role === 'assistant' && <span className="bubble-icon">🤖</span>}
            <div className="bubble-text">
              {m.content}
              {streaming && i === messages.length - 1 && m.role === 'assistant' && (
                <span className="cursor-blink">▌</span>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
 
      {messages.length <= 1 && (
        <div className="starters">
          {STARTERS.map((s) => (
            <button key={s} className="starter-btn" onClick={() => send(s)}>{s}</button>
          ))}
        </div>
      )}
 
      <div className="chat-input-row">
        <textarea
          className="chat-input"
          rows={1}
          placeholder="Ask about your leaves…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={streaming}
        />
        <button
          className="btn btn-primary chat-send"
          onClick={() => send()}
          disabled={streaming || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}