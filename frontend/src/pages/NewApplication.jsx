import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Briefcase, Link, Sparkles } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import NeonButton from '../components/NeonButton';
import { analyzeJob } from '../services/api';

const NewApplication = () => {
  const navigate = useNavigate();
  const [description, setDescription] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!description.trim()) {
      setError('Veuillez coller une offre d\'emploi');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await analyzeJob(description, url);
      setResult(data);
    } catch (err) {
      setError('Erreur lors de l\'analyse : ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return '#4ade80';
    if (score >= 50) return '#a855f7';
    return '#f59e0b';
  };

  const getScoreLabel = (score) => {
    if (score >= 75) return 'Excellent match ! 🎉';
    if (score >= 60) return 'Bon match 👍';
    if (score >= 45) return 'Match moyen ⚡';
    return 'Match faible 💪';
  };

  if (result) {
    const { analysis, match_score, match_details, application_id } = result;

    return (
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/')}
            className="w-10 h-10 rounded-xl glass-card flex items-center justify-center hover:border-purple-500/40 transition-all"
          >
            <ArrowLeft className="w-5 h-5" style={{ color: '#a855f7' }} />
          </button>
          <div>
            <h1 className="text-3xl font-bold neon-gradient-text">Offre analysée !</h1>
            <p style={{ color: 'rgba(148,163,184,0.7)' }}>Voici ce que l'IA a trouvé</p>
          </div>
        </div>

        {/* Match Score */}
        {match_score !== null && match_score !== undefined && (
          <GlassCard className="mb-6 text-center" hover={false}>
            <p className="text-sm mb-2" style={{ color: 'rgba(148,163,184,0.6)' }}>Score de compatibilité</p>
            <div
              className="text-7xl font-black mb-2"
              style={{ color: getScoreColor(match_score) }}
            >
              {match_score}%
            </div>
            <p className="text-lg font-semibold mb-4" style={{ color: getScoreColor(match_score) }}>
              {getScoreLabel(match_score)}
            </p>
            <div className="score-bar-track mx-auto max-w-md mb-4" style={{ height: '8px' }}>
              <div
                className="h-full rounded-full"
                style={{
                  width: `${match_score}%`,
                  background: `linear-gradient(90deg, #a855f7, ${getScoreColor(match_score)})`,
                  transition: 'width 1.5s ease',
                  boxShadow: `0 0 10px ${getScoreColor(match_score)}`,
                }}
              />
            </div>

            {/* Strengths & Gaps */}
            {match_details && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left mt-6">
                <div
                  className="rounded-xl p-4"
                  style={{ background: 'rgba(74,222,128,0.06)', border: '1px solid rgba(74,222,128,0.2)' }}
                >
                  <p className="font-semibold mb-3 flex items-center gap-2" style={{ color: '#4ade80' }}>
                    ✅ Points forts
                  </p>
                  <ul className="space-y-2">
                    {match_details.strengths?.map((s, i) => (
                      <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'rgba(148,163,184,0.8)' }}>
                        <span className="mt-1 text-green-400">•</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>
                <div
                  className="rounded-xl p-4"
                  style={{ background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)' }}
                >
                  <p className="font-semibold mb-3 flex items-center gap-2" style={{ color: '#f87171' }}>
                    ⚠️ Points à travailler
                  </p>
                  <ul className="space-y-2">
                    {match_details.gaps?.map((g, i) => (
                      <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'rgba(148,163,184,0.8)' }}>
                        <span className="mt-1 text-red-400">•</span> {g}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {match_details?.recommendations?.length > 0 && (
              <div
                className="rounded-xl p-4 text-left mt-4"
                style={{ background: 'rgba(168,85,247,0.06)', border: '1px solid rgba(168,85,247,0.2)' }}
              >
                <p className="font-semibold mb-3" style={{ color: '#a855f7' }}>💡 Recommandations</p>
                <ul className="space-y-2">
                  {match_details.recommendations.map((r, i) => (
                    <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'rgba(148,163,184,0.8)' }}>
                      <span className="mt-1 text-purple-400">→</span> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </GlassCard>
        )}

        {/* Job Details */}
        <GlassCard className="mb-6" hover={false}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white">{analysis.title}</h2>
              <p style={{ color: 'rgba(148,163,184,0.7)' }}>{analysis.company} · {analysis.location}</p>
            </div>
            <div className="flex gap-2">
              {analysis.contract_type && (
                <span className="skill-tag">{analysis.contract_type}</span>
              )}
              {analysis.experience_level && (
                <span className="skill-tag">{analysis.experience_level}</span>
              )}
            </div>
          </div>

          {analysis.salary_range && analysis.salary_range !== 'Non spécifié' && (
            <div
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl mb-4 text-sm font-semibold"
              style={{ background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.3)', color: '#4ade80' }}
            >
              💰 {analysis.salary_range}
            </div>
          )}

          <div className="neon-divider" />

          {/* Technical Skills */}
          <div className="mb-4">
            <p className="text-sm font-semibold mb-3" style={{ color: 'rgba(148,163,184,0.6)' }}>
              🛠️ COMPÉTENCES TECHNIQUES
            </p>
            <div className="flex flex-wrap gap-2">
              {analysis.technical_skills?.map((skill, i) => (
                <span key={i} className="skill-tag">{skill}</span>
              ))}
            </div>
          </div>

          {/* ATS Keywords */}
          <div className="mb-4">
            <p className="text-sm font-semibold mb-3" style={{ color: 'rgba(148,163,184,0.6)' }}>
              🎯 KEYWORDS ATS
            </p>
            <div className="flex flex-wrap gap-2">
              {analysis.ats_keywords?.map((kw, i) => (
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

          {/* Responsibilities */}
          <div>
            <p className="text-sm font-semibold mb-3" style={{ color: 'rgba(148,163,184,0.6)' }}>
              📋 RESPONSABILITÉS
            </p>
            <ul className="space-y-2">
              {analysis.key_responsibilities?.map((resp, i) => (
                <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'rgba(148,163,184,0.8)' }}>
                  <span style={{ color: '#06b6d4' }} className="mt-0.5">→</span> {resp}
                </li>
              ))}
            </ul>
          </div>
        </GlassCard>

        {/* Actions */}
        <div className="flex gap-4">
          <NeonButton
            onClick={() => navigate(`/application/${application_id}`)}
            className="flex-1 flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Générer ma candidature complète
          </NeonButton>
          <NeonButton
            onClick={() => { setResult(null); setDescription(''); setUrl(''); }}
            variant="outline"
            className="flex-1"
          >
            Analyser une autre offre
          </NeonButton>
        </div>

      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">

      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => navigate('/')}
          className="w-10 h-10 rounded-xl glass-card flex items-center justify-center transition-all"
          style={{ border: '1px solid rgba(255,255,255,0.08)' }}
        >
          <ArrowLeft className="w-5 h-5" style={{ color: '#a855f7' }} />
        </button>
        <div>
          <h1 className="text-3xl font-bold neon-gradient-text">Nouvelle candidature</h1>
          <p style={{ color: 'rgba(148,163,184,0.7)' }}>Analysez une offre avec l'IA</p>
        </div>
      </div>

      <GlassCard hover={false}>

        {/* URL */}
        <div className="mb-5">
          <label className="block text-sm font-medium mb-2" style={{ color: 'rgba(148,163,184,0.8)' }}>
            <Link className="inline w-4 h-4 mr-1" /> Lien de l'offre (optionnel)
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://linkedin.com/jobs/..."
            className="neon-input w-full px-4 py-3 rounded-xl text-sm"
          />
        </div>

        {/* Description */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2" style={{ color: 'rgba(148,163,184,0.8)' }}>
            <Briefcase className="inline w-4 h-4 mr-1" />
            Description de l'offre <span style={{ color: '#ec4899' }}>*</span>
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Copiez-collez ici le texte complet de l'offre d'emploi..."
            rows={12}
            className="neon-input w-full px-4 py-3 rounded-xl text-sm resize-none"
          />
          <p className="text-xs mt-2" style={{ color: 'rgba(148,163,184,0.4)' }}>
            {description.length} caractères · Plus l'offre est complète, meilleure sera l'analyse
          </p>
        </div>

        {error && (
          <div
            className="mb-4 p-4 rounded-xl text-sm"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}
          >
            ❌ {error}
          </div>
        )}

        <NeonButton
          onClick={handleAnalyze}
          disabled={loading || !description.trim()}
          className="w-full flex items-center justify-center gap-2 py-4 text-base"
        >
          {loading ? (
            <>
              <div
                className="w-5 h-5 rounded-full border-2 border-t-transparent animate-spin"
                style={{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: 'white' }}
              />
              Analyse en cours...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Analyser l'offre avec l'IA
            </>
          )}
        </NeonButton>

      </GlassCard>
    </div>
  );
};

export default NewApplication;