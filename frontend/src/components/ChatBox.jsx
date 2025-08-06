'use client';
import { useRef, useState, useEffect, Suspense } from 'react';

function ChatBox() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Ask me anything about your documents.' },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim()) return;
    setIsLoading(true);
    setError(null);
    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });
      if (!res.body) throw new Error('No response body');
      const reader = res.body.getReader();
      let aiMessage = '';
      setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        aiMessage += new TextDecoder().decode(value);
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: 'assistant', content: aiMessage };
          return updated;
        });
      }
    } catch (err) {
      setError('Something went wrong.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col h-[70vh] bg-base-100 rounded-xl shadow-lg border border-base-200 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat ${msg.role === 'user' ? 'chat-end' : 'chat-start'}`}
          >
            <div className={`chat-bubble ${msg.role === 'user' ? 'chat-bubble-primary' : 'chat-bubble-secondary'} whitespace-pre-line`}>{msg.content}</div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <form
        onSubmit={handleSend}
        className="p-4 bg-base-200 flex gap-2 items-center"
      >
        <input
          className="input input-bordered flex-1"
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          autoFocus
        />
        <button
          className="btn btn-primary"
          type="submit"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? (
            <span className="loading loading-spinner loading-xs"></span>
          ) : (
            'Send'
          )}
        </button>
      </form>
      {error && <div className="text-error text-center p-2">{error}</div>}
    </div>
  );
}

export default function ChatBoxSuspense() {
  return (
    <Suspense fallback={<div className="w-full max-w-xl mx-auto p-8 text-center">Loading chat...</div>}>
      <ChatBox />
    </Suspense>
  );
}
