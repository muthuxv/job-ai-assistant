import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Sparkles, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import NeonButton from '../components/NeonButton';
import StatusBadge from '../components/StatusBadge';
import {
  getApplication,
  updateApplication,
  generateAllTones,
  getInterviewPrep,
  deleteApplication,
} from '../services/api';

// ─── Composant CopyButton ───────────────────────────────────────
const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
      style={{
        background: copied ? 'rgba(74,222,128,0.15)' : 'rgba(255,255,255,0.06)',
        border: `1px solid ${copied ? 'rgba(74,222,128,0.4)' : 'rgba(255,255,255,0.1)'}`,
        color: copied ? '#4ade80' : 'rgba(148,163,184,0.8)',
      }}
    >
      {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
      {copied ? 'Copié !' : 'Copier'}
    </button>
  );
};

// ─── Composant CollapsibleSection ──────────────────────────────
const CollapsibleSection = ({ title, icon, children, defaultOpen = false, accentColor = '#a855f7' }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div
      className="rounded-2xl overflow-hidden mb-4"
      style={{ border: `1px solid rgba(255,255,255,0.08)`, background: 'rgba(255,255,255,0.03)' }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-5 transition-all"
        style={{ background: open ? `rgba(168,85,247,0.05)` : 'transparent' }}
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">{icon}</span>
          <span className="font-bold text-white text-lg">{title}</span>
        </div>
        {open
          ? <ChevronUp className="w-5 h-5" style={{ color: accentColor }} />
          : <ChevronDown className="w-5 h-5" style={{ color: 'rgba(148,163,184,0.5)' }} />
        }
      </button>
      {open && (
        <div className="px-5 pb-5">
          <div className="neon-divider mb-4" />
          {children}
        </div>
      )}
    </div>
  );
};

// ─── Page Principale ────────────────────────────────────────────
const ApplicationDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingLetters, setGeneratingLetters] = useState(false);
  const [generatingPrep, setGeneratingPrep] = useState(false);
  const [interviewPrep, setInterviewPrep] = useState(null);
  const [activeLetterTone, setActiveLetterTone] = useState('formal');
  const [coverLetters, setCoverLetters] = useState({});
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => { loadApplication(); }, [id]);

  const loadApplication = async () => {
    try {
      const data = await getApplication(parseInt(id));
      setApplication(data);

      // Charge les cover letters existantes
      if (data.cover_letters?.length > 0) {
        const letters = {};
        data.cover_letters.forEach(cl => { letters[cl.tone] = cl.content; });
        setCoverLetters(letters);
        setActiveLetterTone(Object.keys(letters)[0]);
      }
    } catch (err) {
      console.error('Erreur chargement:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateLetters = async () => {
    setGeneratingLetters(true);
    try {
      const result = await generateAllTones(parseInt(id));
      setCoverLetters(result.cover_letters);
      setActiveLetterTone('formal');
      await loadApplication();
    } catch (err) {
      alert('Erreur : ' + (err.response?.data?.detail || err.message));
    } finally {
      setGeneratingLetters(false);
    }
  };

  const handleGeneratePrep = async () => {
    setGeneratingPrep(true);
    try {
      const result = await getInterviewPrep(parseInt(id));
      setInterviewPrep(result.preparation);
    } catch (err) {
      alert('Erreur : ' + (err.response?.data?.detail || err.message));
    } finally {
      setGeneratingPrep(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      await updateApplication(parseInt(id), {
        status: newStatus,
        applied_date: newStatus === 'applied' ? new Date().toISOString() : undefined,
      });
      await loadApplication();
    } catch (err) {
      console.error('Erreur update:', err);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Supprimer cette candidature ?')) {
      await deleteApplication(parseInt(id));
      navigate('/');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return '#4ade80';
    if (score >= 50) return '#a855f7';
    return '#f59e0b';
  };

  const toneConfig = {
    formal:  { label: 'Formel',  icon: '👔', color: '#a855f7' },
    startup: { label: 'Startup', icon: '🚀', color: '#06b6d4' },
    tech:    { label: 'Tech',    icon: '💻', color: '#ec4899' },
  };

  const statusFlow = [
    { value: 'draft',     label: 'Brouillon', icon: '📝' },
    { value: 'applied',   label: 'Envoyée',   icon: '📤' },
    { value: 'interview', label: 'Entretien', icon: '🎤' },
    { value: 'offer',     label: 'Offre',     icon: '🎉' },
    { value: 'rejected',  label: 'Refusée',   icon: '❌' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div
          className="w-14 h-14 rounded-full border-4 border-t-transparent animate-spin"
          style={{ borderColor: 'rgba(168,85,247,0.3)', borderTopColor: '#a855f7' }}
        />
      </div>
    );
  }

  if (!application) {
    return (
      <div className="text-center py-20">
        <p style={{ color: 'rgba(148,163,184,0.6)' }}>Candidature introuvable</p>
        <NeonButton onClick={() => navigate('/')} className="mt-4">Retour</NeonButton>
      </div>
    );
  }

  const { job, status, match_score } = application;

  return (
    <div className="max-w-4xl mx-auto">

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div className="flex items-start gap-4">
          <button
            onClick={() => navigate('/')}
            className="w-10 h-10 rounded-xl glass-card flex items-center justify-center mt-1 transition-all"
          >
            <ArrowLeft className="w-5 h-5" style={{ color: '#a855f7' }} />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">{job.title}</h1>
            <p style={{ color: 'rgba(148,163,184,0.7)' }}>{job.company}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={status} />
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1.5 rounded-lg transition-all"
              style={{
                background: 'rgba(6,182,212,0.1)',
                border: '1px solid rgba(6,182,212,0.3)',
                color: '#06b6d4',
              }}
            >
              🔗 Voir l'offre
            </a>
          )}
        </div>
      </div>

      {/* Match Score */}
      {match_score !== null && match_score !== undefined && (
        <GlassCard hover={false} className="mb-6">
          <div className="flex items-center gap-6">
            <div className="text-center flex-shrink-0">
              <div className="text-5xl font-black mb-1" style={{ color: getScoreColor(match_score) }}>
                {match_score}%
              </div>
              <p className="text-xs" style={{ color: 'rgba(148,163,184,0.6)' }}>Compatibilité</p>
            </div>
            <div className="flex-1">
              <div className="score-bar-track mb-2" style={{ height: '10px' }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${match_score}%`,
                    background: `linear-gradient(90deg, #a855f7, ${getScoreColor(match_score)})`,
                    boxShadow: `0 0 12px ${getScoreColor(match_score)}80`,
                    transition: 'width 1.5s ease',
                  }}
                />
              </div>
              <p className="text-sm font-semibold" style={{ color: getScoreColor(match_score) }}>
                {match_score >= 75 ? '🎉 Excellent profil pour ce poste !' :
                 match_score >= 60 ? '👍 Bon match, candidature encouragée' :
                 match_score >= 45 ? '⚡ Match moyen, soignez votre lettre' :
                 '💪 Défi ambitieux, mais pourquoi pas !'}
              </p>
            </div>
          </div>
        </GlassCard>
      )}

      {/* Status Flow */}
      <GlassCard hover={false} className="mb-6">
        <p className="text-sm font-semibold mb-4" style={{ color: 'rgba(148,163,184,0.6)' }}>
          📍 STATUT DE LA CANDIDATURE
        </p>
        <div className="flex items-center gap-2 flex-wrap">
          {statusFlow.map((s) => (
            <button
              key={s.value}
              onClick={() => handleStatusUpdate(s.value)}
              disabled={updatingStatus || s.value === status}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all"
              style={{
                background: s.value === status
                  ? 'rgba(168,85,247,0.2)'
                  : 'rgba(255,255,255,0.04)',
                border: `1px solid ${s.value === status
                  ? 'rgba(168,85,247,0.5)'
                  : 'rgba(255,255,255,0.08)'}`,
                color: s.value === status ? '#a855f7' : 'rgba(148,163,184,0.7)',
                boxShadow: s.value === status ? '0 0 12px rgba(168,85,247,0.3)' : 'none',
                cursor: s.value === status ? 'default' : 'pointer',
              }}
            >
              {s.icon} {s.label}
            </button>
          ))}
        </div>
      </GlassCard>

      {/* Cover Letters */}
      <CollapsibleSection title="Lettres de motivation" icon="✉️" defaultOpen={true}>
        {Object.keys(coverLetters).length === 0 ? (
          <div className="text-center py-8">
            <p className="mb-4" style={{ color: 'rgba(148,163,184,0.6)' }}>
              Aucune lettre générée pour l'instant
            </p>
            <NeonButton
              onClick={handleGenerateLetters}
              disabled={generatingLetters}
              className="flex items-center gap-2 mx-auto"
            >
              {generatingLetters ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-t-transparent animate-spin"
                    style={{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: 'white' }} />
                  Génération en cours...
                </>
              ) : (
                <><Sparkles className="w-4 h-4" /> Générer 3 versions</>
              )}
            </NeonButton>
          </div>
        ) : (
          <>
            {/* Tone Selector */}
            <div className="flex gap-2 mb-4">
              {Object.keys(coverLetters).map((tone) => {
                const config = toneConfig[tone];
                const isActive = activeLetterTone === tone;
                return (
                  <button
                    key={tone}
                    onClick={() => setActiveLetterTone(tone)}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all"
                    style={{
                      background: isActive ? `${config.color}20` : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${isActive ? `${config.color}50` : 'rgba(255,255,255,0.08)'}`,
                      color: isActive ? config.color : 'rgba(148,163,184,0.7)',
                      boxShadow: isActive ? `0 0 12px ${config.color}30` : 'none',
                    }}
                  >
                    {config.icon} {config.label}
                  </button>
                );
              })}
              <div className="ml-auto">
                <CopyButton text={coverLetters[activeLetterTone] || ''} />
              </div>
            </div>

            {/* Letter Content */}
            <div
              className="rounded-xl p-5 text-sm leading-relaxed whitespace-pre-wrap"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.06)',
                color: 'rgba(241,245,249,0.9)',
                fontFamily: 'Georgia, serif',
                lineHeight: '1.8',
              }}
            >
              {coverLetters[activeLetterTone]}
            </div>

            {/* Regenerate */}
            <div className="mt-4 text-right">
              <button
                onClick={handleGenerateLetters}
                disabled={generatingLetters}
                className="text-xs transition-all"
                style={{ color: 'rgba(148,163,184,0.5)' }}
              >
                {generatingLetters ? '⏳ Régénération...' : '🔄 Régénérer les 3 versions'}
              </button>
            </div>
          </>
        )}
      </CollapsibleSection>

      {/* Interview Prep */}
      <CollapsibleSection title="Préparation entretien" icon="🎤" defaultOpen={false}>
        {!interviewPrep ? (
          <div className="text-center py-8">
            <p className="mb-4" style={{ color: 'rgba(148,163,184,0.6)' }}>
              Questions probables, tips et réponses suggérées
            </p>
            <NeonButton
              onClick={handleGeneratePrep}
              disabled={generatingPrep}
              variant="cyan"
              className="flex items-center gap-2 mx-auto"
            >
              {generatingPrep ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-t-transparent animate-spin"
                    style={{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: 'white' }} />
                  Génération en cours...
                </>
              ) : (
                <><Sparkles className="w-4 h-4" /> Générer la préparation</>
              )}
            </NeonButton>
          </div>
        ) : (
          <div className="space-y-6">

            {/* Questions générales */}
            {interviewPrep.general_questions?.length > 0 && (
              <div>
                <p className="text-sm font-semibold mb-3" style={{ color: '#a855f7' }}>
                  🗣️ Questions générales
                </p>
                <div className="space-y-3">
                  {interviewPrep.general_questions.map((q, i) => (
                    <div
                      key={i}
                      className="rounded-xl p-4"
                      style={{ background: 'rgba(168,85,247,0.05)', border: '1px solid rgba(168,85,247,0.15)' }}
                    >
                      <p className="font-semibold text-white mb-2">❓ {q.question}</p>
                      <p className="text-xs mb-2" style={{ color: '#a855f7' }}>
                        💡 {q.tips}
                      </p>
                      {q.example_answer && (
                        <p className="text-sm" style={{ color: 'rgba(148,163,184,0.7)' }}>
                          → {q.example_answer}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="neon-divider" />

            {/* Questions techniques */}
            {interviewPrep.technical_questions?.length > 0 && (
              <div>
                <p className="text-sm font-semibold mb-3" style={{ color: '#06b6d4' }}>
                  💻 Questions techniques
                </p>
                <div className="space-y-3">
                  {interviewPrep.technical_questions.map((q, i) => (
                    <div
                      key={i}
                      className="rounded-xl p-4"
                      style={{ background: 'rgba(6,182,212,0.05)', border: '1px solid rgba(6,182,212,0.15)' }}
                    >
                      <p className="font-semibold text-white mb-1">❓ {q.question}</p>
                      <p className="text-xs mb-2" style={{ color: '#06b6d4' }}>
                        🎯 Sujet : {q.topic}
                      </p>
                      <p className="text-sm mb-2" style={{ color: 'rgba(148,163,184,0.7)' }}>
                        💡 {q.tips}
                      </p>
                      {q.key_points?.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {q.key_points.map((point, j) => (
                            <span key={j} className="skill-tag">{point}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="neon-divider" />

            {/* Questions comportementales */}
            {interviewPrep.behavioral_questions?.length > 0 && (
              <div>
                <p className="text-sm font-semibold mb-3" style={{ color: '#ec4899' }}>
                  🧠 Questions comportementales (STAR)
                </p>
                <div className="space-y-3">
                  {interviewPrep.behavioral_questions.map((q, i) => (
                    <div
                      key={i}
                      className="rounded-xl p-4"
                      style={{ background: 'rgba(236,72,153,0.05)', border: '1px solid rgba(236,72,153,0.15)' }}
                    >
                      <p className="font-semibold text-white mb-2">❓ {q.question}</p>
                      <p className="text-xs mb-2" style={{ color: '#ec4899' }}>
                        📌 Méthode : {q.framework}
                      </p>
                      <p className="text-sm" style={{ color: 'rgba(148,163,184,0.7)' }}>
                        💡 {q.your_example}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="neon-divider" />

            {/* Questions à poser */}
            {interviewPrep.questions_to_ask?.length > 0 && (
              <div>
                <p className="text-sm font-semibold mb-3" style={{ color: '#4ade80' }}>
                  🙋 Questions à poser au recruteur
                </p>
                <div className="space-y-3">
                  {interviewPrep.questions_to_ask.map((q, i) => (
                    <div
                      key={i}
                      className="rounded-xl p-4"
                      style={{ background: 'rgba(74,222,128,0.05)', border: '1px solid rgba(74,222,128,0.15)' }}
                    >
                      <p className="font-semibold text-white mb-1">❓ {q.question}</p>
                      <p className="text-xs" style={{ color: '#4ade80' }}>✨ {q.shows}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="neon-divider" />

            {/* Red Flags & Forces */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {interviewPrep.red_flags_to_avoid?.length > 0 && (
                <div
                  className="rounded-xl p-4"
                  style={{ background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.15)' }}
                >
                  <p className="text-sm font-semibold mb-3" style={{ color: '#f87171' }}>
                    🚫 À éviter
                  </p>
                  <ul className="space-y-2">
                    {interviewPrep.red_flags_to_avoid.map((flag, i) => (
                      <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'rgba(148,163,184,0.7)' }}>
                        <span style={{ color: '#f87171' }}>✗</span> {flag}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {interviewPrep.strengths_to_highlight?.length > 0 && (
                <div
                  className="rounded-xl p-4"
                  style={{ background: 'rgba(74,222,128,0.05)', border: '1px solid rgba(74,222,128,0.15)' }}
                >
                  <p className="text-sm font-semibold mb-3" style={{ color: '#4ade80' }}>
                    ⭐ Forces à mettre en avant
                  </p>
                  <ul className="space-y-2">
                    {interviewPrep.strengths_to_highlight.map((s, i) => (
                      <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'rgba(148,163,184,0.7)' }}>
                        <span style={{ color: '#4ade80' }}>✓</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </CollapsibleSection>

      {/* Job Requirements */}
      <CollapsibleSection title="Détails de l'offre" icon="📋" defaultOpen={false}>
        <div className="space-y-4">
          {job.requirements?.technical_skills?.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-2" style={{ color: 'rgba(148,163,184,0.6)' }}>
                🛠️ Compétences requises
              </p>
              <div className="flex flex-wrap gap-2">
                {job.requirements.technical_skills.map((skill, i) => (
                  <span key={i} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          )}
          {job.requirements?.ats_keywords?.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-2" style={{ color: 'rgba(148,163,184,0.6)' }}>
                🎯 Keywords ATS
              </p>
              <div className="flex flex-wrap gap-2">
                {job.requirements.ats_keywords.map((kw, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 rounded-full text-xs font-semibold"
                    style={{
                      background: 'rgba(168,85,247,0.1)',
                      border: '1px solid rgba(168,85,247,0.3)',
                      color: '#a855f7'
                    }}
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </CollapsibleSection>

      {/* Delete */}
      <div className="mt-6 text-center">
        <button
          onClick={handleDelete}
          className="text-sm transition-all"
          style={{ color: 'rgba(148,163,184,0.3)' }}
          onMouseEnter={e => e.target.style.color = '#f87171'}
          onMouseLeave={e => e.target.style.color = 'rgba(148,163,184,0.3)'}
        >
          🗑️ Supprimer cette candidature
        </button>
      </div>
    </div>
    );
    };


export default ApplicationDetails;