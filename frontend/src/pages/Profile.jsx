import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { profileService } from '../services/api';
import { User, CheckCircle, Clock, BookOpen, AlertCircle, Save } from 'lucide-react';

export const Profile = () => {
  const { user, profile, refreshProfile } = useAuth();
  
  const [educationLevel, setEducationLevel] = useState('College');
  const [dailyHours, setDailyHours] = useState(2.0);
  const [learningPref, setLearningPref] = useState('Visual');

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (profile) {
      setEducationLevel(profile.education_level || 'College');
      setDailyHours(profile.daily_study_hours || 2.0);
      setLearningPref(profile.learning_preference || 'Visual');
    }
  }, [profile]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccessMsg('');

    try {
      await profileService.updateProfile({
        education_level: educationLevel,
        daily_study_hours: parseFloat(dailyHours),
        learning_preference: learningPref,
      });
      await refreshProfile();
      setSuccessMsg('Profile preferences updated successfully!');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <User className="w-6 h-6 text-emerald-400" />
          Student Profile Settings
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Customize your academic background and learning style so Gemini tailors study plans to you.
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

      {/* Account Info Card */}
      <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
          Account Details
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-3.5 bg-[#070b12] border border-slate-800 rounded-xl">
            <span className="text-[11px] font-semibold uppercase text-slate-500">Student Name</span>
            <p className="text-sm font-semibold text-slate-200 mt-0.5">{user?.name}</p>
          </div>
          <div className="p-3.5 bg-[#070b12] border border-slate-800 rounded-xl">
            <span className="text-[11px] font-semibold uppercase text-slate-500">Email Address</span>
            <p className="text-sm font-semibold text-slate-200 mt-0.5">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* AI Personalization Form */}
      <div className="bg-[#0c121e] border border-slate-800 rounded-2xl p-6 shadow-sm">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
          AI Personalization Preferences
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Education Level
            </label>
            <select
              value={educationLevel}
              onChange={(e) => setEducationLevel(e.target.value)}
              className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
            >
              <option value="High School">High School</option>
              <option value="Undergraduate">Undergraduate / College</option>
              <option value="Graduate">Graduate / Master's</option>
              <option value="PhD / Research">PhD / Research</option>
              <option value="Self-Taught">Self-Taught / Professional</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Daily Study Capacity (Hours per Day): <span className="text-emerald-400 font-bold">{dailyHours} hrs</span>
            </label>
            <input
              type="range"
              min="0.5"
              max="14.0"
              step="0.5"
              value={dailyHours}
              onChange={(e) => setDailyHours(e.target.value)}
              className="w-full accent-emerald-500"
            />
            <div className="flex justify-between text-[11px] text-slate-500 mt-1">
              <span>30 mins</span>
              <span>7 hours</span>
              <span>14 hours</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Preferred Learning Style
            </label>
            <select
              value={learningPref}
              onChange={(e) => setLearningPref(e.target.value)}
              className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
            >
              <option value="Visual">Visual (Diagrams, analogies, flowcharts)</option>
              <option value="Hands-On">Hands-On (Practice problems, code, exercises)</option>
              <option value="Theory">Theoretical (Formal proofs, deep principles)</option>
              <option value="Concise">Concise & Summary-Focused (Bullet points, quick review)</option>
            </select>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/25 transition-all flex items-center gap-2"
            >
              {saving ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Saving Changes...
                </>
              ) : (
                <>
                  <Save className="w-3.5 h-3.5" />
                  Save Preferences
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
