import React, { useState, useEffect } from 'react';
import { subjectsService, quizService } from '../services/api';
import {
  HelpCircle,
  Sparkles,
  Award,
  CheckCircle,
  XCircle,
  RotateCcw,
  AlertCircle
} from 'lucide-react';

export const Quiz = () => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [numQuestions, setNumQuestions] = useState(5);

  const [generating, setGenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const res = await subjectsService.listSubjects();
        setSubjects(res.data);
        if (res.data.length > 0) {
          setSelectedSubjectId(res.data[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchSubjects();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedSubjectId || !topic.trim()) {
      alert('Please select a subject and enter a topic name');
      return;
    }

    setGenerating(true);
    setError('');
    setResult(null);
    setAnswers({});

    try {
      const res = await quizService.generateQuiz({
        subject_id: parseInt(selectedSubjectId, 10),
        topic: topic.trim(),
        difficulty,
        number_of_questions: parseInt(numQuestions, 10),
      });
      setCurrentQuiz(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to generate quiz with Gemini AI.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectOption = (qIndex, optionKey) => {
    setAnswers((prev) => ({
      ...prev,
      [String(qIndex)]: optionKey,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!currentQuiz) return;

    const total = currentQuiz.questions_json?.length || 0;
    const answeredCount = Object.keys(answers).length;
    if (answeredCount < total) {
      if (!window.confirm(`You've only answered ${answeredCount} of ${total} questions. Submit anyway?`)) {
        return;
      }
    }

    setSubmitting(true);
    setError('');

    try {
      const res = await quizService.submitQuiz(currentQuiz.id, answers);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to grade quiz.');
    } finally {
      setSubmitting(false);
    }
  };

  const resetQuiz = () => {
    setCurrentQuiz(null);
    setAnswers({});
    setResult(null);
  };

  const questions = currentQuiz?.questions_json || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <HelpCircle className="w-6 h-6 text-emerald-400" />
          AI Quiz Generator & Evaluator
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Generate custom diagnostic quizzes and get evaluated with 100% deterministic backend scoring.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Generator Form */}
      {!currentQuiz && !result && (
        <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
          <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            Configure Quiz Parameters
          </h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Target Course / Subject
                </label>
                <select
                  value={selectedSubjectId}
                  onChange={(e) => setSelectedSubjectId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.difficulty})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Topic or Concept to Test
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. TCP Handshake, Semaphores, ACID properties"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Difficulty Level
                </label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  <option value="easy">Easy (Fundamentals & Definitions)</option>
                  <option value="medium">Medium (Application & Problem Solving)</option>
                  <option value="hard">Hard (Advanced Edge Cases & Complex Analysis)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Number of Questions
                </label>
                <select
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  <option value={3}>3 Questions (Quick check)</option>
                  <option value={5}>5 Questions (Standard)</option>
                  <option value={10}>10 Questions (Comprehensive drill)</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={generating || subjects.length === 0}
                className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-2"
              >
                {generating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Generating Questions with Gemini...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate AI Quiz
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Active Quiz Player */}
      {currentQuiz && !result && (
        <div className="space-y-6">
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                  Topic Assessment
                </span>
                <h2 className="text-xl font-bold text-white mt-0.5">{currentQuiz.topic}</h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-[#070b12] text-slate-300 px-3 py-1 rounded-lg border border-slate-700 uppercase font-semibold">
                  {currentQuiz.difficulty}
                </span>
                <button
                  onClick={resetQuiz}
                  className="text-xs px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>

            {/* Questions List */}
            <div className="mt-6 space-y-6">
              {questions.map((q, qIdx) => {
                const currentAnswer = answers[String(qIdx)];
                const options = q.options || {};

                return (
                  <div
                    key={qIdx}
                    className="p-5 bg-[#070b12] border border-slate-800/90 rounded-xl space-y-4"
                  >
                    <div className="flex items-start gap-3">
                      <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                        {qIdx + 1}
                      </span>
                      <p className="text-sm font-semibold text-slate-100 leading-relaxed">
                        {q.question}
                      </p>
                    </div>

                    {/* 4 Options Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pl-9">
                      {['A', 'B', 'C', 'D'].map((key) => {
                        const isSelected = currentAnswer === key;
                        const optionText = options[key] || '';

                        return (
                          <button
                            key={key}
                            type="button"
                            onClick={() => handleSelectOption(qIdx, key)}
                            className={`p-3 rounded-xl text-xs text-left transition-all flex items-start gap-2.5 border ${
                              isSelected
                                ? 'bg-emerald-600/20 border-emerald-500 text-white font-medium shadow-sm shadow-emerald-950/20'
                                : 'bg-[#0c121e] border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/40'
                            }`}
                          >
                            <span
                              className={`w-5 h-5 rounded-md text-[10px] font-bold flex items-center justify-center shrink-0 ${
                                isSelected
                                  ? 'bg-emerald-600 text-white'
                                  : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              {key}
                            </span>
                            <span className="leading-relaxed">{optionText}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 pt-5 border-t border-slate-800 flex items-center justify-between">
              <span className="text-xs text-slate-400">
                {Object.keys(answers).length} of {questions.length} answered
              </span>
              <button
                onClick={handleSubmitQuiz}
                disabled={submitting}
                className="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/25 transition-all flex items-center gap-2"
              >
                {submitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Grading Answers...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Submit & Grade Quiz
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results & Score Screen */}
      {result && (
        <div className="space-y-6">
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-xl">
            {/* Header Score Overview */}
            <div className="text-center py-6 border-b border-slate-800">
              <div className="inline-flex p-3 rounded-full bg-emerald-500/10 text-emerald-400 mb-3 border border-emerald-500/20">
                <Award className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-black text-white">Quiz Evaluation Completed</h2>
              <div className="mt-3 flex items-center justify-center gap-3">
                <span className="text-3xl font-black text-emerald-400">
                  {result.score} / {result.total_questions}
                </span>
                <span
                  className={`text-lg font-bold px-3 py-1 rounded-full ${
                    result.percentage >= 70
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {result.percentage.toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Graded deterministically by AI StudyBuddy server engine
              </p>
            </div>

            {/* Question by Question Feedback */}
            <div className="mt-6 space-y-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Detailed Answer Breakdown & Explanations
              </h3>
              {result.feedback &&
                result.feedback.map((item, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border ${
                      item.is_correct
                        ? 'bg-emerald-950/20 border-emerald-500/30'
                        : 'bg-rose-950/20 border-rose-500/30'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {item.is_correct ? (
                        <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                      )}
                      <div className="space-y-1.5 flex-1">
                        <p className="text-sm font-semibold text-slate-100">
                          {idx + 1}. {item.question}
                        </p>
                        <div className="flex flex-wrap items-center gap-3 text-xs">
                          <span
                            className={
                              item.is_correct ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'
                            }
                          >
                            Your Answer: {item.selected_answer || 'None'}
                          </span>
                          {!item.is_correct && (
                            <span className="text-emerald-400 font-bold">
                              Correct Answer: {item.correct_answer}
                            </span>
                          )}
                        </div>
                        <div className="mt-2 pt-2 border-t border-slate-800 text-xs text-slate-400 leading-relaxed">
                          <span className="text-slate-300 font-semibold">Explanation: </span>
                          {item.explanation}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>

            <div className="mt-6 pt-5 border-t border-slate-800 flex justify-end gap-3">
              <button
                onClick={resetQuiz}
                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-md transition-all flex items-center gap-2"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Take Another Quiz
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
