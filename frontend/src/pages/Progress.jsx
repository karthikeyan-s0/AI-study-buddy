import React, { useState, useEffect } from 'react';
import { subjectsService, topicsService, progressService, aiService } from '../services/api';
import {
  TrendingUp,
  Brain,
  Clock,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  Plus,
  AlertCircle
} from 'lucide-react';

export const Progress = () => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [topics, setTopics] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState('');
  const [studyMinutes, setStudyMinutes] = useState(30);
  const [completionPercentage, setCompletionPercentage] = useState(100);

  const [progressList, setProgressList] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [aiReport, setAiReport] = useState(null);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [subjRes, progRes] = await Promise.all([
        subjectsService.listSubjects(),
        progressService.listProgress(),
      ]);
      setSubjects(subjRes.data);
      setProgressList(progRes.data);

      if (subjRes.data.length > 0) {
        const firstSubjId = subjRes.data[0].id;
        setSelectedSubjectId(firstSubjId);
        loadTopicsForSubject(firstSubjId);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to load progress records');
    }
  };

  const loadTopicsForSubject = async (subjectId) => {
    try {
      const res = await topicsService.listTopics(subjectId);
      setTopics(res.data);
      if (res.data.length > 0) {
        setSelectedTopicId(res.data[0].id);
      } else {
        setSelectedTopicId('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubjectChange = (subjectId) => {
    setSelectedSubjectId(subjectId);
    loadTopicsForSubject(subjectId);
    setAiReport(null);
  };

  const handleLogProgress = async (e) => {
    e.preventDefault();
    if (!selectedSubjectId) return;

    setError('');
    setSuccessMsg('');

    try {
      await progressService.updateProgress({
        subject_id: parseInt(selectedSubjectId, 10),
        topic_id: selectedTopicId ? parseInt(selectedTopicId, 10) : null,
        completion_percentage: parseFloat(completionPercentage),
        study_minutes: parseInt(studyMinutes, 10),
      });

      setSuccessMsg('Progress successfully recorded!');
      setTimeout(() => setSuccessMsg(''), 3000);

      // Refresh list
      const progRes = await progressService.listProgress();
      setProgressList(progRes.data);
    } catch (err) {
      console.error(err);
      setError('Failed to record progress');
    }
  };

  const handleRunAiAnalysis = async () => {
    if (!selectedSubjectId) {
      alert('Please select a subject to analyze');
      return;
    }

    setAnalyzing(true);
    setError('');

    try {
      const res = await aiService.analyzePerformance(parseInt(selectedSubjectId, 10));
      setAiReport(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to generate AI performance analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <TrendingUp className="w-6 h-6 text-emerald-400" />
          Progress & Learning Analytics
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Log revision sessions, track minutes spent on each topic, and request AI diagnostic reports.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-3 text-emerald-400 text-sm">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Columns: Log Session & AI Diagnostic */}
        <div className="lg:col-span-2 space-y-6">
          {/* Log Study Session Form */}
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Plus className="w-4 h-4 text-emerald-400" />
              Log Study Session
            </h2>

            <form onSubmit={handleLogProgress} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Subject
                  </label>
                  <select
                    value={selectedSubjectId}
                    onChange={(e) => handleSubjectChange(e.target.value)}
                    className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  >
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Topic
                  </label>
                  <select
                    value={selectedTopicId}
                    onChange={(e) => setSelectedTopicId(e.target.value)}
                    className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  >
                    <option value="">General Subject Progress</option>
                    {topics.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name} ({t.status})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Study Time (Minutes)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="600"
                    value={studyMinutes}
                    onChange={(e) => setStudyMinutes(e.target.value)}
                    className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Completion Percentage ({completionPercentage}%)
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    value={completionPercentage}
                    onChange={(e) => setCompletionPercentage(e.target.value)}
                    className="w-full mt-2 accent-emerald-500"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={subjects.length === 0}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/25 transition-all flex items-center gap-2"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Save Progress
                </button>
              </div>
            </form>
          </div>

          {/* AI Diagnostic Button and Report */}
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Brain className="w-5 h-5 text-cyan-400" />
                  AI Performance Analysis
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Gemini analyzes quiz scores and topic time to diagnose weaknesses.
                </p>
              </div>
              <button
                onClick={handleRunAiAnalysis}
                disabled={analyzing || subjects.length === 0}
                className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-cyan-600/25 transition-all flex items-center gap-2 shrink-0"
              >
                {analyzing ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Diagnosing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    Analyze Current Subject
                  </>
                )}
              </button>
            </div>

            {aiReport ? (
              <div className="mt-6 space-y-4">
                <div className="p-4 bg-[#070b12] border border-slate-800 rounded-xl">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-1.5">
                    Diagnostic Summary
                  </h4>
                  <p className="text-sm text-slate-300 leading-relaxed">{aiReport.overall_summary}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Strengths */}
                  <div className="p-4 bg-[#070b12] border border-slate-800 rounded-xl">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Strengths & Mastered Concepts
                    </h4>
                    <ul className="space-y-1.5">
                      {aiReport.strengths?.map((s, i) => (
                        <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                          <span className="text-emerald-400">•</span>
                          <span>{s}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Weaknesses */}
                  <div className="p-4 bg-[#070b12] border border-slate-800 rounded-xl">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-400 mb-2 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Identified Weak Topics
                    </h4>
                    <ul className="space-y-1.5">
                      {aiReport.weak_topics?.map((w, i) => (
                        <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                          <span className="text-rose-400">•</span>
                          <span>{w}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Recommendations */}
                {aiReport.recommendations && aiReport.recommendations.length > 0 && (
                  <div className="p-4 bg-[#070b12] border border-slate-800 rounded-xl">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-teal-400 mb-2">
                      Tailored Study Strategies
                    </h4>
                    <ul className="space-y-1.5">
                      {aiReport.recommendations.map((rec, i) => (
                        <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-teal-400">→</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">
                Click "Analyze Current Subject" to trigger an automated diagnosis of your study data.
              </p>
            )}
          </div>
        </div>

        {/* Right Column: Recent Progress Log */}
        <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Clock className="w-4 h-4 text-emerald-400" />
            Revision Records ({progressList.length})
          </h3>

          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
            {progressList.length === 0 ? (
              <p className="text-xs text-slate-500">No study logs yet recorded.</p>
            ) : (
              progressList.map((p) => (
                <div key={p.id} className="p-3 bg-[#070b12] border border-slate-800/80 rounded-xl space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-200">
                      Subject #{p.subject_id} {p.topic_id ? `• Topic #${p.topic_id}` : ''}
                    </span>
                    <span className="text-xs font-bold text-emerald-400">
                      {p.completion_percentage.toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{p.study_minutes} mins accumulated</span>
                    <span>{new Date(p.last_studied).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
