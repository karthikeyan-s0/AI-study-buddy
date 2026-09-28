import React, { useState, useEffect } from 'react';
import { subjectsService, studyPlanService } from '../services/api';
import {
  Calendar,
  Sparkles,
  Clock,
  CheckCircle,
  BookOpen,
  ArrowRight,
  ListOrdered,
  AlertCircle
} from 'lucide-react';

export const StudyPlanner = () => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [focusAreas, setFocusAreas] = useState('');
  
  const [generating, setGenerating] = useState(false);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [savedPlans, setSavedPlans] = useState([]);
  const [error, setError] = useState('');

  // Default dates: today to +7 days
  useEffect(() => {
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);
    setStartDate(today.toISOString().split('T')[0]);
    setEndDate(nextWeek.toISOString().split('T')[0]);

    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [subjRes, plansRes] = await Promise.all([
        subjectsService.listSubjects(),
        studyPlanService.listPlans(),
      ]);
      setSubjects(subjRes.data);
      if (subjRes.data.length > 0) {
        setSelectedSubjectId(subjRes.data[0].id);
      }
      setSavedPlans(plansRes.data);
      if (plansRes.data.length > 0) {
        setCurrentPlan(plansRes.data[0]);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to load study planner prerequisites');
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedSubjectId) {
      alert('Please select a subject first');
      return;
    }

    setGenerating(true);
    setError('');

    try {
      const res = await studyPlanService.generatePlan({
        subject_id: parseInt(selectedSubjectId, 10),
        start_date: startDate,
        end_date: endDate,
        focus_areas: focusAreas ? focusAreas.split(',').map((s) => s.trim()) : [],
      });
      setCurrentPlan(res.data);
      setSavedPlans((prev) => [res.data, ...prev]);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to generate study plan with Gemini AI.');
    } finally {
      setGenerating(false);
    }
  };

  const planContent = currentPlan?.plan_json;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <Calendar className="w-6 h-6 text-emerald-400" />
          AI Study Planner
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Generate realistic, personalized day-by-day study schedules powered by Gemini 3.8 Flash.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Generation Form Card */}
      <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Target Subject
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
                Start Date
              </label>
              <input
                type="date"
                required
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                End Date (Exam / Milestone)
              </label>
              <input
                type="date"
                required
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Focus Areas or Priorities (Optional, comma-separated)
            </label>
            <input
              type="text"
              placeholder="e.g. Memory Hierarchy, Paging Algorithms, Deadlock Detection"
              value={focusAreas}
              onChange={(e) => setFocusAreas(e.target.value)}
              className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
            />
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
                  Generating Schedule with Gemini...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate AI Study Plan
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Plan Display Area */}
      {currentPlan && planContent ? (
        <div className="space-y-6">
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                  {currentPlan.start_date} → {currentPlan.end_date}
                </span>
                <h2 className="text-xl font-bold text-white mt-1">{currentPlan.title}</h2>
                <p className="text-sm text-slate-400 mt-1">{planContent.summary || 'Structured preparation roadmap.'}</p>
              </div>

              {/* Saved Plans Dropdown */}
              {savedPlans.length > 1 && (
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs text-slate-400 font-medium">History:</span>
                  <select
                    value={currentPlan.id}
                    onChange={(e) => {
                      const found = savedPlans.find((p) => p.id === parseInt(e.target.value, 10));
                      if (found) setCurrentPlan(found);
                    }}
                    className="px-3 py-1.5 bg-[#070b12] border border-slate-700 rounded-lg text-xs text-slate-200"
                  >
                    {savedPlans.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.title} ({p.start_date})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Days Roadmap */}
            <div className="mt-6 space-y-4">
              {planContent.days && planContent.days.map((dayItem, idx) => (
                <div
                  key={idx}
                  className="bg-[#070b12] border border-slate-800/90 rounded-xl p-5 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-300 font-bold text-xs flex items-center justify-center border border-emerald-500/30">
                        D{dayItem.day}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-slate-200">
                          Day {dayItem.day} &bull; <span className="text-slate-400 font-normal">{dayItem.date}</span>
                        </h4>
                      </div>
                    </div>
                  </div>

                  {/* Day's Topics */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                    {dayItem.topics && dayItem.topics.map((t, tIdx) => (
                      <div
                        key={tIdx}
                        className="bg-[#0c121e] border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-200">{t.topic}</span>
                            <span className="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {t.duration_minutes}m
                            </span>
                          </div>

                          {t.activities && t.activities.length > 0 && (
                            <ul className="mt-2.5 space-y-1">
                              {t.activities.map((act, aIdx) => (
                                <li key={aIdx} className="text-xs text-slate-400 flex items-start gap-1.5">
                                  <span className="text-emerald-400 mt-0.5">•</span>
                                  <span>{act}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-[#0c121e] border border-dashed border-slate-800 rounded-2xl">
          <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-300">No study plan selected</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            Choose your subject above and generate your customized syllabus schedule.
          </p>
        </div>
      )}
    </div>
  );
};
