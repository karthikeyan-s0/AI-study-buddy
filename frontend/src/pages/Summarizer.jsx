import React, { useState } from 'react';
import { aiService } from '../services/api';
import {
  FileText,
  Sparkles,
  Copy,
  Check,
  BookMarked,
  Key,
  AlertCircle
} from 'lucide-react';

export const Summarizer = () => {
  const [content, setContent] = useState('');
  const [focus, setFocus] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleSummarize = async (e) => {
    e.preventDefault();
    if (!content.trim()) {
      alert('Please paste lecture notes or study text first');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await aiService.summarize({
        content,
        focus: focus.trim() || undefined,
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to summarize content with Gemini AI.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    const textToCopy = `EXECUTIVE SUMMARY:\n${result.summary}\n\nKEY TAKEAWAYS:\n${result.key_points?.map((p) => `- ${p}`).join('\n')}\n\nIMPORTANT TERMS:\n${result.important_terms?.map((t) => `- ${t}`).join('\n')}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <FileText className="w-6 h-6 text-emerald-400" />
          AI Lecture Summarizer
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Paste dense reading material, lecture slides, or textbooks to extract key principles and terms.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Input Form */}
      <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
        <form onSubmit={handleSummarize} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Source Study Text / Lecture Notes
            </label>
            <textarea
              required
              rows={8}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your raw lecture notes, article excerpts, or syllabus topic text here..."
              className="w-full px-4 py-3 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500 leading-relaxed font-mono"
            ></textarea>
            <span className="text-[11px] text-slate-500 block text-right mt-1">
              {content.length} characters
            </span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Optional Focus Area (e.g. "Focus on Exam Definitions" or "Focus on Algorithms")
            </label>
            <input
              type="text"
              value={focus}
              onChange={(e) => setFocus(e.target.value)}
              placeholder="e.g. Exam definitions and trade-offs"
              className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Analyzing and Condensing with Gemini...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate AI Summary
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Results View */}
      {result && (
        <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <BookMarked className="w-5 h-5 text-emerald-400" />
              Summary Overview
            </h2>
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 bg-[#070b12] hover:bg-[#131b2e] text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors border border-slate-700"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  Copied to Clipboard!
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  Copy Markdown
                </>
              )}
            </button>
          </div>

          {/* Executive Summary */}
          <div className="bg-[#070b12] border border-slate-800 rounded-xl p-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-2">
              Executive Summary
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed">{result.summary}</p>
          </div>

          {/* Key Points */}
          {result.key_points && result.key_points.length > 0 && (
            <div className="bg-[#070b12] border border-slate-800 rounded-xl p-5">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Key Concept Takeaways
              </h3>
              <ul className="space-y-2">
                {result.key_points.map((pt, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2.5 leading-relaxed">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0"></span>
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Important Terms */}
          {result.important_terms && result.important_terms.length > 0 && (
            <div className="bg-[#070b12] border border-slate-800 rounded-xl p-5">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-teal-400 mb-3 flex items-center gap-2">
                <Key className="w-4 h-4" />
                Important Academic Terminology
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.important_terms.map((item, i) => (
                  <div key={i} className="bg-[#0c121e] border border-slate-800 p-3 rounded-lg">
                    <span className="text-xs font-bold text-teal-400 block mb-1">
                      {typeof item === 'string' ? item : item.term}
                    </span>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      {typeof item === 'string' ? '' : item.definition}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
