import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, BookOpen, Brain, Award, ArrowRight } from 'lucide-react';

export const Landing = () => {
  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col justify-between selection:bg-emerald-500 selection:text-white">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-[#0c121e]/70 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/logo.jpg"
              alt="AI StudyBuddy Logo"
              className="w-9 h-9 rounded-xl object-cover border border-emerald-500/40 shadow-md shadow-emerald-500/20"
            />
            <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              AI StudyBuddy
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-md shadow-emerald-600/30 transition-all hover:scale-[1.02]"
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative px-6 py-16 max-w-5xl mx-auto text-center">
        {/* Big Glowing Logo Display */}
        <div className="mb-6 inline-block relative">
          <div className="absolute -inset-1.5 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-3xl blur opacity-35 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-pulse"></div>
          <img
            src="/logo.jpg"
            alt="AI StudyBuddy"
            className="relative w-28 h-28 mx-auto rounded-2xl object-cover border-2 border-emerald-400/50 shadow-2xl shadow-emerald-500/30"
          />
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          AI-Augmented Backend Intelligence
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-100 mb-6 leading-tight">
          Supercharge Your College Studies with <br />
          <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
            Deterministic AI Pair Tutoring
          </span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          AI StudyBuddy combines FastAPI, PostgreSQL-ready persistent models, and Google Gemini 3.8 Flash to generate syllabus-based study plans, lecture summaries, adaptive quizzes, and diagnostic analytics.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/register"
            className="w-full sm:w-auto px-6 py-3.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium rounded-xl shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02] flex items-center justify-center gap-2"
          >
            Create Free Account
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto px-6 py-3.5 bg-slate-900 hover:bg-slate-800 text-slate-200 font-medium rounded-xl border border-slate-700 transition-all"
          >
            Log In to Workspace
          </Link>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="px-6 py-14 max-w-6xl mx-auto w-full">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#0c121e]/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm hover:border-emerald-500/40 transition-all">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4 border border-emerald-500/30">
              <Brain className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Automated Study Plans</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Personalized multi-day schedules structured specifically for your upcoming college exams and daily study capacity.
            </p>
          </div>

          <div className="bg-[#0c121e]/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm hover:border-cyan-500/40 transition-all">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center mb-4 border border-cyan-500/30">
              <Award className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">Deterministic Quizzes</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              AI creates high-level multiple choice questions, and our backend grades them with 100% mathematical precision.
            </p>
          </div>

          <div className="bg-[#0c121e]/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm hover:border-teal-500/40 transition-all">
            <div className="w-10 h-10 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center mb-4 border border-teal-500/30">
              <BookOpen className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-100 mb-2">AI Summaries & Q&A</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Condense massive lecture notes into high-impact key concepts or ask deep academic questions to an intelligent tutor.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 px-6 text-center text-xs text-slate-500">
        <p>AI StudyBuddy &bull; College Final Project: AI-Augmented Backend Development</p>
      </footer>
    </div>
  );
};
