import React, { useState, useEffect } from 'react';
import { subjectsService, topicsService } from '../services/api';
import {
  BookOpen,
  Plus,
  Trash2,
  Calendar,
  CheckCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  AlertCircle
} from 'lucide-react';

export const Subjects = () => {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // New Subject Form state
  const [showSubjectModal, setShowSubjectModal] = useState(false);
  const [newSubject, setNewSubject] = useState({
    name: '',
    description: '',
    difficulty: 'medium',
    exam_date: '',
  });

  // Expanded Subject for topics
  const [expandedSubjectId, setExpandedSubjectId] = useState(null);
  const [topicsMap, setTopicsMap] = useState({});
  const [newTopicName, setNewTopicName] = useState('');
  const [newTopicDifficulty, setNewTopicDifficulty] = useState('medium');

  const fetchSubjects = async () => {
    try {
      const res = await subjectsService.listSubjects();
      setSubjects(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch subjects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjects();
  }, []);

  const handleCreateSubject = async (e) => {
    e.preventDefault();
    try {
      await subjectsService.createSubject({
        ...newSubject,
        exam_date: newSubject.exam_date || null
      });
      setShowSubjectModal(false);
      setNewSubject({ name: '', description: '', difficulty: 'medium', exam_date: '' });
      await fetchSubjects();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || 'Failed to create subject');
    }
  };

  const handleDeleteSubject = async (id, name) => {
    if (!window.confirm(`Delete subject "${name}" and all its topics?`)) return;
    try {
      await subjectsService.deleteSubject(id);
      await fetchSubjects();
    } catch (err) {
      console.error(err);
      alert('Failed to delete subject');
    }
  };

  const toggleExpand = async (subjectId) => {
    if (expandedSubjectId === subjectId) {
      setExpandedSubjectId(null);
      return;
    }
    setExpandedSubjectId(subjectId);
    if (!topicsMap[subjectId]) {
      try {
        const res = await topicsService.listTopics(subjectId);
        setTopicsMap((prev) => ({ ...prev, [subjectId]: res.data }));
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleAddTopic = async (subjectId) => {
    if (!newTopicName.trim()) return;
    try {
      const res = await topicsService.createTopic(subjectId, {
        name: newTopicName,
        difficulty: newTopicDifficulty,
        status: 'not_started',
      });
      setTopicsMap((prev) => ({
        ...prev,
        [subjectId]: [...(prev[subjectId] || []), res.data],
      }));
      setNewTopicName('');
    } catch (err) {
      console.error(err);
      alert('Failed to add topic');
    }
  };

  const handleToggleTopicStatus = async (subjectId, topic) => {
    const nextStatus =
      topic.status === 'not_started'
        ? 'in_progress'
        : topic.status === 'in_progress'
        ? 'completed'
        : 'not_started';

    try {
      const res = await topicsService.updateTopic(topic.id, {
        status: nextStatus,
      });
      setTopicsMap((prev) => ({
        ...prev,
        [subjectId]: prev[subjectId].map((t) => (t.id === topic.id ? res.data : t)),
      }));
    } catch (err) {
      console.error(err);
      alert('Failed to update topic status');
    }
  };

  const handleDeleteTopic = async (subjectId, topicId) => {
    try {
      await topicsService.deleteTopic(topicId);
      setTopicsMap((prev) => ({
        ...prev,
        [subjectId]: prev[subjectId].filter((t) => t.id !== topicId),
      }));
    } catch (err) {
      console.error(err);
      alert('Failed to delete topic');
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-sm text-slate-400">Loading your subjects...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <BookOpen className="w-6 h-6 text-emerald-400" />
            Subjects & Syllabus Curriculum
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Organize your courses and break them down into granular topics for AI tracking.
          </p>
        </div>
        <button
          onClick={() => setShowSubjectModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl shadow-md shadow-emerald-600/25 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          Add Subject
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Subjects List */}
      <div className="space-y-4">
        {subjects.length === 0 ? (
          <div className="text-center py-16 bg-[#0c121e] border border-dashed border-slate-800 rounded-2xl">
            <BookOpen className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-slate-300">No subjects yet</h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1 mb-4">
              Add a college course (e.g. Operating Systems, Database Systems, Computer Networks) to begin tracking your syllabus.
            </p>
            <button
              onClick={() => setShowSubjectModal(true)}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg"
            >
              Add First Course
            </button>
          </div>
        ) : (
          subjects.map((subj) => {
            const isExpanded = expandedSubjectId === subj.id;
            const topics = topicsMap[subj.id] || [];

            return (
              <div
                key={subj.id}
                className="bg-[#0c121e] border border-slate-800 rounded-2xl overflow-hidden shadow-sm transition-all"
              >
                {/* Subject Header Row */}
                <div className="p-5 flex items-center justify-between gap-4">
                  <div
                    onClick={() => toggleExpand(subj.id)}
                    className="flex items-center gap-3.5 flex-1 cursor-pointer select-none"
                  >
                    <button className="text-slate-400 hover:text-white p-1">
                      {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </button>
                    <div>
                      <div className="flex items-center gap-2.5">
                        <h3 className="text-base font-bold text-white hover:text-emerald-400 transition-colors">
                          {subj.name}
                        </h3>
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                          subj.difficulty === 'hard'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : subj.difficulty === 'medium'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}>
                          {subj.difficulty}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{subj.description || 'No description provided'}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    {subj.exam_date && (
                      <span className="text-xs text-cyan-400/90 font-medium flex items-center gap-1.5 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
                        <Calendar className="w-3.5 h-3.5" />
                        {subj.exam_date}
                      </span>
                    )}
                    <button
                      onClick={() => handleDeleteSubject(subj.id, subj.name)}
                      className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                      title="Delete Subject"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Topics Accordion Section */}
                {isExpanded && (
                  <div className="border-t border-slate-800 bg-[#070b12] p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Syllabus Topics ({topics.length})
                      </h4>
                      <span className="text-[11px] text-slate-500">Click a topic's status to toggle progress</span>
                    </div>

                    {/* Topic List */}
                    <div className="space-y-2">
                      {topics.length === 0 ? (
                        <p className="text-xs text-slate-500 py-2">No topics added to this subject yet.</p>
                      ) : (
                        topics.map((t) => (
                          <div
                            key={t.id}
                            className="flex items-center justify-between p-3 bg-[#0c121e] border border-slate-800/80 rounded-xl"
                          >
                            <div className="flex items-center gap-3">
                              <button
                                onClick={() => handleToggleTopicStatus(subj.id, t)}
                                className={`text-xs px-2.5 py-1 rounded-lg font-medium flex items-center gap-1.5 transition-colors ${
                                  t.status === 'completed'
                                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                    : t.status === 'in_progress'
                                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                                }`}
                              >
                                {t.status === 'completed' ? (
                                  <>
                                    <CheckCircle className="w-3.5 h-3.5" />
                                    Completed
                                  </>
                                ) : t.status === 'in_progress' ? (
                                  <>
                                    <Clock className="w-3.5 h-3.5" />
                                    In Progress
                                  </>
                                ) : (
                                  'Not Started'
                                )}
                              </button>
                              <span className="text-sm font-medium text-slate-200">{t.name}</span>
                            </div>

                            <div className="flex items-center gap-3">
                              <span className="text-[10px] text-slate-400 font-semibold uppercase bg-slate-800 px-2 py-0.5 rounded">
                                {t.difficulty}
                              </span>
                              <button
                                onClick={() => handleDeleteTopic(subj.id, t.id)}
                                className="text-slate-500 hover:text-rose-400 p-1"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>

                    {/* Add Topic Input Bar */}
                    <div className="pt-3 border-t border-slate-800/60 flex flex-col sm:flex-row gap-2">
                      <input
                        type="text"
                        placeholder="Add a new topic (e.g. Memory Management, Normalization)"
                        value={newTopicName}
                        onChange={(e) => setNewTopicName(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddTopic(subj.id)}
                        className="flex-1 px-3.5 py-2 bg-[#0c121e] border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                      />
                      <select
                        value={newTopicDifficulty}
                        onChange={(e) => setNewTopicDifficulty(e.target.value)}
                        className="px-3 py-2 bg-[#0c121e] border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                      >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                      </select>
                      <button
                        onClick={() => handleAddTopic(subj.id)}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 shadow-sm"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        Add Topic
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Add Subject Modal */}
      {showSubjectModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0c121e] border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4">Add New Subject</h3>
            <form onSubmit={handleCreateSubject} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Subject Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Operating Systems"
                  value={newSubject.name}
                  onChange={(e) => setNewSubject({ ...newSubject, name: e.target.value })}
                  className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Description (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Processes, Memory, Storage, Concurrency"
                  value={newSubject.description}
                  onChange={(e) => setNewSubject({ ...newSubject, description: e.target.value })}
                  className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700 rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Difficulty
                  </label>
                  <select
                    value={newSubject.difficulty}
                    onChange={(e) => setNewSubject({ ...newSubject, difficulty: e.target.value })}
                    className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Exam Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={newSubject.exam_date}
                    onChange={(e) => setNewSubject({ ...newSubject, exam_date: e.target.value })}
                    className="w-full px-4 py-2.5 bg-[#070b12] border border-slate-700 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowSubjectModal(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow-md"
                >
                  Save Subject
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
