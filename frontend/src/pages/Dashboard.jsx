import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../services/api';
import {
  TrendingUp,
  BookOpen,
  Calendar,
  Award,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
  Brain,
  HelpCircle
} from 'lucide-react';

export const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await dashboardService.getDashboard();
        setData(res.data);
      } catch (err) {
        console.error('Failed to load dashboard', err);
        setError('Failed to fetch dashboard data. Please make sure the backend is running.');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-sm text-slate-400">Loading student learning overview...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 text-sm">
        {error || 'Unable to display dashboard.'}
      </div>
    );
  }

  const { student, overall_progress, subjects, upcoming_exams, recent_quiz_attempts, weak_topics, strong_topics, recommendations } = data;

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-emerald-950/60 via-teal-950/40 to-[#0c121e] border border-emerald-500/25 rounded-3xl p-8 shadow-xl shadow-emerald-950/20">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 rounded-full border border-emerald-500/30">
                {student.education_level || 'College'} Student
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-cyan-500/20 text-cyan-300 rounded-full border border-cyan-500/30">
                Goal: {student.daily_study_hours} hrs/day
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              Hello, {student.name}! 👋
            </h1>
            <p className="text-slate-300 mt-1 text-sm max-w-xl">
              Here is your AI-analyzed academic standing. You've completed {overall_progress.toFixed(0)}% of your tracked syllabus.
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap gap-2.5">
            <Link
              to="/quiz"
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow-md shadow-emerald-600/25 transition-all flex items-center gap-2"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              New AI Quiz
            </Link>
            <Link
              to="/study-planner"
              className="px-4 py-2 bg-[#131b2e] hover:bg-[#1a253f] text-slate-200 text-xs font-semibold rounded-xl border border-slate-700/80 transition-all flex items-center gap-2"
            >
              <Calendar className="w-3.5 h-3.5" />
              Plan Study
            </Link>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-emerald-500/30 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Overall Progress</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-xl">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-black text-white">{overall_progress.toFixed(1)}%</span>
            <div className="w-full bg-slate-800/80 rounded-full h-2 mt-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(overall_progress, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-cyan-500/30 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Subjects</span>
            <div className="p-2 bg-cyan-500/10 text-cyan-400 rounded-xl">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-black text-white">{subjects.length}</span>
            <p className="text-xs text-slate-400 mt-1">Active courses tracked</p>
          </div>
        </div>

        <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-amber-500/30 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Upcoming Exams</span>
            <div className="p-2 bg-amber-500/10 text-amber-400 rounded-xl">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-black text-white">{upcoming_exams.length}</span>
            <p className="text-xs text-slate-400 mt-1">Scheduled deadlines</p>
          </div>
        </div>

        <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-emerald-500/30 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Quiz Attempts</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-xl">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-black text-white">{recent_quiz_attempts.length}</span>
            <p className="text-xs text-slate-400 mt-1">Tests completed</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Subjects & AI Diagnostics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Subject Progress List */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-emerald-400" />
                Subjects & Syllabus Progress
              </h2>
              <Link to="/subjects" className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1">
                Manage Subjects <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {subjects.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-slate-800 rounded-xl">
                <BookOpen className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                <p className="text-sm text-slate-400">No subjects added yet.</p>
                <Link
                  to="/subjects"
                  className="mt-3 inline-block px-4 py-2 text-xs bg-emerald-600 text-white rounded-lg font-medium"
                >
                  Add Your First Subject
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {subjects.map((subj) => (
                  <div key={subj.id} className="p-4 bg-[#070b12] border border-slate-800/90 rounded-xl hover:border-slate-700 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <span className="font-semibold text-slate-200 text-sm">{subj.name}</span>
                        <span className="ml-2 px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded bg-slate-800 text-slate-400">
                          {subj.difficulty}
                        </span>
                      </div>
                      <span className="text-xs font-bold text-emerald-400">{subj.progress_percentage.toFixed(0)}%</span>
                    </div>

                    <div className="w-full bg-slate-800/80 rounded-full h-2 mb-2 overflow-hidden">
                      <div
                        className="bg-emerald-500 h-2 rounded-full"
                        style={{ width: `${subj.progress_percentage}%` }}
                      ></div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>{subj.completed_topics} of {subj.topics_count} topics finished</span>
                      {subj.exam_date && (
                        <span className="text-cyan-400/90 font-medium">Exam: {subj.exam_date}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Quiz Attempts */}
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Award className="w-5 h-5 text-cyan-400" />
                Recent Quiz Performance
              </h2>
              <Link to="/quiz" className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1">
                View Quizzes <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {recent_quiz_attempts.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-6">No quiz attempts yet. Generate a quiz to test your mastery!</p>
            ) : (
              <div className="space-y-3">
                {recent_quiz_attempts.map((att) => (
                  <div key={att.id} className="p-3.5 bg-[#070b12] border border-slate-800/90 rounded-xl flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-semibold text-slate-200">{att.topic}</h4>
                      <p className="text-xs text-slate-400">Score: {att.score} / {att.total_questions}</p>
                    </div>
                    <div className="text-right">
                      <span
                        className={`text-sm font-bold ${
                          att.percentage >= 70 ? 'text-emerald-400' : 'text-amber-400'
                        }`}
                      >
                        {att.percentage.toFixed(0)}%
                      </span>
                      <p className="text-[10px] text-slate-500 mt-0.5">
                        {new Date(att.attempted_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: AI Analysis & Upcoming Exams */}
        <div className="space-y-6">
          {/* AI Insights & Recommendations */}
          <div className="bg-gradient-to-b from-emerald-950/30 to-[#0c121e] border border-emerald-500/25 rounded-2xl p-6 shadow-md shadow-emerald-950/20">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-1.5 bg-emerald-500/20 text-emerald-400 rounded-lg">
                <Brain className="w-4 h-4" />
              </div>
              <h3 className="font-bold text-white text-base">AI Study Recommendations</h3>
            </div>

            <div className="space-y-3">
              {recommendations && recommendations.length > 0 ? (
                recommendations.map((rec, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-300 leading-relaxed bg-[#070b12]/80 p-3 rounded-xl border border-slate-800/80">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{rec}</span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-400">Complete topics or quizzes to unlock personalized AI recommendations.</p>
              )}
            </div>

            {/* Strengths and Weaknesses */}
            <div className="mt-6 pt-5 border-t border-slate-800 space-y-4">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-rose-400 flex items-center gap-1.5 mb-2">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Focus Topics (Needs Attention)
                </span>
                {weak_topics && weak_topics.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {weak_topics.map((t, i) => (
                      <span key={i} className="text-xs bg-rose-500/10 text-rose-300 border border-rose-500/20 px-2 py-1 rounded-lg">
                        {t}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">No weak topics flagged.</p>
                )}
              </div>

              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5 mb-2">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Strong Topics (Mastered)
                </span>
                {strong_topics && strong_topics.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {strong_topics.map((t, i) => (
                      <span key={i} className="text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2 py-1 rounded-lg">
                        {t}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">Take quizzes to record your mastered concepts.</p>
                )}
              </div>
            </div>
          </div>

          {/* Upcoming Exams Card */}
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6">
            <h3 className="font-bold text-white text-base mb-4 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-400" />
              Upcoming Exam Dates
            </h3>
            {upcoming_exams.length === 0 ? (
              <p className="text-xs text-slate-500">No upcoming exam dates set on your subjects.</p>
            ) : (
              <div className="space-y-2.5">
                {upcoming_exams.map((ex, i) => (
                  <div key={i} className="p-3 bg-[#070b12] border border-slate-800 rounded-xl flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-slate-200">{ex.name}</p>
                      <p className="text-[11px] text-slate-400">{ex.days_until} days remaining</p>
                    </div>
                    <span className="text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
                      {ex.exam_date}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
