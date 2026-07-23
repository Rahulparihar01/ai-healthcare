import React, { useState, useRef, useEffect } from 'react';
import api from '../../api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  needsReview?: boolean;
}

const RAGChatInterface: React.FC<{ healthId: string }> = ({ healthId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('English');
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleVoiceInput = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support Speech Recognition.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = language === 'Spanish' ? 'es-ES' : language === 'Hindi' ? 'hi-IN' : 'en-US';
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(prev => prev + " " + transcript);
    };
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'Spanish' ? 'es-ES' : language === 'Hindi' ? 'hi-IN' : 'en-US';
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/copilot/chat', {
        query: userMsg,
        health_id: healthId,
        language: language
      });
      const answer = response.data.answer;
      speak(answer);
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: answer, sources: response.data.sources, needsReview: response.data.needs_review }
      ]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: 'Sorry, I encountered an error answering your question.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px] border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div className="bg-blue-600 p-4 text-white font-semibold flex items-center justify-between">
        <span>Copilot Assistant</span>
        <select 
          className="bg-blue-700 text-white border-none rounded text-sm p-1 focus:ring-0"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="English">English</option>
          <option value="Spanish">Español</option>
          <option value="Hindi">हिंदी</option>
        </select>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto bg-gray-50 flex flex-col gap-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-10">
            Ask me anything about this patient's medical history.
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-3 shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 border border-gray-100'}`}>
              {msg.needsReview && (
                <div className="mb-2 p-2 bg-yellow-50 text-yellow-800 text-xs font-semibold rounded border border-yellow-200 flex items-center gap-1">
                  ⚠️ Low confidence response. Please verify against source documents.
                </div>
              )}
              <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
              
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-gray-200">
                  <span className="text-xs font-semibold text-gray-500 mb-1 block">Sources:</span>
                  <ul className="text-xs text-gray-500 list-disc pl-4 space-y-1">
                    {msg.sources.map((s, i) => (
                      <li key={i}>{s.title} ({new Date(s.event_date).toLocaleDateString()})</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-100 text-gray-500 rounded-lg p-3 shadow-sm text-sm flex gap-2 items-center">
              <span className="animate-pulse">●</span>
              <span className="animate-pulse animation-delay-200">●</span>
              <span className="animate-pulse animation-delay-400">●</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 bg-white border-t border-gray-200 flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a medical question..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm"
        />
        <button
          onClick={handleVoiceInput}
          className={`px-3 py-2 border rounded-md transition-colors ${isListening ? 'bg-red-100 border-red-300 text-red-600' : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200'}`}
          title="Dictate"
        >
          🎤
        </button>
        <button 
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default RAGChatInterface;
