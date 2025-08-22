'use client';
import { useRef, useState, useEffect, Suspense } from 'react';

function ChatBox() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your AI Knowledge Assistant. Ask me anything about your documents, or any general questions you might have.' },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);
  const hasAutoScrolledOnceRef = useRef(false);

  useEffect(() => {
    // Avoid scrolling on first render so the page starts at the top
    if (!hasAutoScrolledOnceRef.current) {
      hasAutoScrolledOnceRef.current = true;
      return;
    }
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
      setError('Something went wrong. Please try again.');
      setMessages((prev) => prev.slice(0, -1)); // Remove the empty assistant message
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col h-[600px] bg-card border border-border rounded-2xl shadow-lg overflow-hidden backdrop-blur-sm">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-border bg-muted/30">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-muted-foreground">AI Assistant</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>{messages.length > 1 ? `${messages.length - 1} messages` : 'Start conversation'}</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            )}
            <div
              className={`max-w-[70%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground ml-auto'
                  : 'bg-muted text-foreground'
              }`}
            >
              {msg.content && (
                <div className="whitespace-pre-line break-words">
                  {msg.content}
                </div>
              )}
              {msg.role === 'assistant' && !msg.content && isLoading && (
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-muted-foreground text-xs">Thinking...</span>
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-secondary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-6 py-2">
          <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg">
            <svg className="w-4 h-4 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-red-700 dark:text-red-400">{error}</span>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-border bg-muted/30">
        <form onSubmit={handleSend} className="flex gap-3">
          <div className="flex-1 relative">
            <input
              className="w-full px-4 py-3 bg-background border border-border rounded-xl focus-ring resize-none text-sm placeholder:text-muted-foreground disabled:opacity-50 disabled:cursor-not-allowed pr-12"
              type="text"
              placeholder="Ask me anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              // Avoid auto focusing on initial load to prevent scrolling to bottom
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="text-xs text-muted-foreground">
                {input.length > 0 && `${input.length}`}
              </div>
            </div>
          </div>
          <button
            className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium focus-ring disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:bg-primary/90 flex items-center gap-2"
            type="submit"
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></div>
                <span className="hidden sm:inline">Sending</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </form>
        
        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mt-3">
          {messages.length === 1 && (
            <>
              <button
                onClick={() => setInput('Give me a summary of the document')}
                className="px-3 py-1.5 bg-accent text-accent-foreground text-xs rounded-lg hover:bg-accent/80 transition-colors"
              >
                Give me a summary of the document
              </button>
              <button
                onClick={() => setInput('What is the topic of the document about?')}
                className="px-3 py-1.5 bg-accent text-accent-foreground text-xs rounded-lg hover:bg-accent/80 transition-colors"
              >
                What is the topic of the document about?
              </button>
              {/* <button
                onClick={() => setInput('Explain quantum computing in simple terms')}
                className="px-3 py-1.5 bg-accent text-accent-foreground text-xs rounded-lg hover:bg-accent/80 transition-colors"
              >
                Explain quantum computing
              </button> */}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ChatBoxSuspense() {
  return (
    <Suspense fallback={
      <div className="w-full max-w-4xl mx-auto h-[600px] bg-card border border-border rounded-2xl shadow-lg flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
          <span>Loading chat...</span>
        </div>
      </div>
    }>
      <ChatBox />
    </Suspense>
  );
}
