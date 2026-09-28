import React, { useState } from 'react';
import { aiService } from '../services/api';
import {
  MessageSquare,
  Sparkles,
  Send,
  User,
  Bot,
  AlertCircle
} from 'lucide-react';

export const Assistant = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Hello! I am your AI Study Assistant powered by Google Gemini. Ask me any conceptual question, syllabus topic breakdown, code explanation, or exam prep query!",
    },
  ]);
  const [question, setQuestion] = useState('');
  const [context, setContext] = useState('');
  const [showContext, setShowContext] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSend = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userQ = question.trim();
    const currentContext = context.trim();
    
    // Add user message to state
    setMessages((prev) => [...prev, { role: 'user', content: userQ }]);
    setQuestion('');
    setLoading(true);
    setError('');

    try {
      const res = await aiService.ask({
        question: userQ,
        context: currentContext || undefined,
      });

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.data.answer },
      ]);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to get an answer from Gemini AI.');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            "⚠️ I encountered an issue connecting to the AI tutor service. Please check your network or try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    'Explain the difference between Process and Thread with an analogy.',
    'How does B-Tree indexing speed up SQL queries?',
    'What are the 4 conditions required for Deadlock to occur?',
    'Explain the OSI 7-layer model in simple terms.',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <MessageSquare className="w-6 h-6 text-emerald-400" />
            AI Academic Assistant
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Ask any conceptual questions, debugging queries, or exam review topics.
          </p>
        </div>
        <button
          onClick={() => setShowContext(!showContext)}
          className="text-xs px-3 py-1.5 bg-[#0c121e] border border-slate-700/80 hover:border-slate-600 rounded-lg text-slate-300 font-medium"
        >
          {showContext ? 'Hide Context' : '+ Add Syllabus Context'}
        </button>
      </div>

      {/* Optional Context Box */}
      {showContext && (
        <div className="mt-3 p-3 bg-[#0c121e] border border-slate-800 rounded-xl shrink-0">
          <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Optional Academic Context (e.g., Course Name, Exam Level, Syllabus Details)
          </label>
          <input
            type="text"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="e.g. Operating Systems Final Exam, Computer Science Year 3"
            className="w-full px-3 py-1.5 bg-[#070b12] border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
      )}

      {error && (
        <div className="mt-3 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-2 text-rose-400 text-xs shrink-0">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-4 pr-2">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3.5 ${
              m.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {m.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-emerald-600/25 border border-emerald-500/40 text-emerald-400 flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-2xl px-5 py-3.5 rounded-2xl text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-950/30'
                  : 'bg-[#0c121e] border border-slate-800 text-slate-200'
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
            </div>

            {m.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-cyan-600/25 border border-cyan-500/40 text-cyan-300 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-start gap-3.5">
            <div className="w-8 h-8 rounded-xl bg-emerald-600/25 border border-emerald-500/40 text-emerald-400 flex items-center justify-center shrink-0 animate-pulse">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="bg-[#0c121e] border border-slate-800 px-5 py-3 rounded-2xl flex items-center gap-2 text-slate-400 text-xs">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></div>
              <span>Gemini is generating pedagogical answer...</span>
            </div>
          </div>
        )}
      </div>

      {/* Suggested Quick Prompts */}
      {messages.length <= 2 && (
        <div className="py-2 flex flex-wrap gap-2 shrink-0">
          {sampleQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => setQuestion(q)}
              className="text-xs bg-[#0c121e] hover:bg-[#131b2e] border border-slate-800 hover:border-slate-700 text-slate-300 px-3 py-1.5 rounded-full transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input Box Form */}
      <div className="pt-3 border-t border-slate-800 shrink-0">
        <form onSubmit={handleSend} className="flex gap-2">
          <input
            type="text"
            required
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask your tutor anything (e.g., 'Explain deadlock prevention methods')..."
            className="flex-1 px-4 py-3 bg-[#0c121e] border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-5 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl shadow-md shadow-emerald-600/25 transition-all flex items-center justify-center gap-2 shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
