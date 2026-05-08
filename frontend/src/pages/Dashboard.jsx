import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Plus, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import NeonButton from '../components/NeonButton';
import StatusBadge from '../components/StatusBadge';
import { getAllApplications, getStats } from '../services/api';

const Dashboard = ({ hasCV }) => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [appsData, statsData] = await Promise.all([
        getAllApplications(),
        getStats(),
      ]);
      setApplications(appsData);
      setStats(statsData);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreConfig = (score) => {
    if (score >= 75) return { barClass: 'score-bar-high', color: '#4ade80' };
    if (score >= 50) return { barClass: 'score-bar-mid', color: '#a855f7' };
    return { barClass: 'score-bar-low', color: '#f59e0b' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div 
            className="w-14 h-14 rounded-full border-4 border-t-transparent animate-spin mx-auto mb-4"
            style={{ borderColor: 'rgba(168,85,247,0.3)', borderTopColor: '#a855f7' }}
          />
          <p style={{ color: 'rgba(148,163,184,0.6)' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-1 neon-gradient-text">Dashboard</h1>
          <p style={{ color: 'rgba(148,163,184,0.7)' }}>Gérez vos candidatures avec l'IA</p>
        </div>
        <NeonButton onClick={() => navigate('/new')} className="flex items-center gap-2">
          <Plus className="w-5 h-5" /> Nouvelle candidature
        </NeonButton>
      </div>

      {/* Banner pas de CV */}
      {!hasCV && applications.length > 0 && (
        <div 
          className="glass-card rounded-2xl p-5 mb-6 flex items-start gap-4"
          style={{ borderColor: 'rgba(6,182,212,0.3)', boxShadow: '0 0 20px rgba(6,182,212,0.1)' }}
        >
          <div className="w-10 h-10 rounded-xl icon-cyan flex items-center justify-center flex-shrink-0">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <p className="font-semibold mb-1" style={{ color: '#06b6d4' }}>
              Uploadez votre CV pour des candidatures personnalisées
            </p>
            <p className="text-sm mb-3" style={{ color: 'rgba(148,163,184,0.7)' }}>
              Score de compatibilité, lettres de motivation personnalisées et préparation d'entretien.
            </p>
            <NeonButton onClick={() => navigate('/upload-cv')} variant="cyan" className="text-sm py-2 px-4">
              Uploader mon CV
            </NeonButton>
          </div>
        </div>
      )}

      {/* Stat Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total', value: stats.total, cardClass: 'stat-card-violet', iconClass: 'icon-violet', icon: <Briefcase className="w-5 h-5" /> },
            { label: 'En cours', value: (stats.by_status?.applied || 0) + (stats.by_status?.interview || 0), cardClass: 'stat-card-cyan', iconClass: 'icon-cyan', icon: <Clock className="w-5 h-5" /> },
            { label: 'Entretiens', value: stats.by_status?.interview || 0, cardClass: 'stat-card-green', iconClass: 'icon-green', icon: <CheckCircle className="w-5 h-5" /> },
            { label: 'Score moyen', value: stats.average_match_score ? `${stats.average_match_score}%` : '--', cardClass: 'stat-card-pink', iconClass: 'icon-pink', icon: <TrendingUp className="w-5 h-5" /> },
          ].map((stat, i) => (
            <div key={i} className={`${stat.cardClass} rounded-2xl p-5 flex items-center gap-4`}>
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${stat.iconClass}`}>
                {stat.icon}
              </div>
              <div>
                <p className="text-xs mb-0.5" style={{ color: 'rgba(148,163,184,0.6)' }}>{stat.label}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Applications */}
      {applications.length === 0 ? (
        <GlassCard className="text-center py-16">
          <div 
            className="w-20 h-20 mx-auto mb-4 rounded-2xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, rgba(168,85,247,0.15), rgba(6,182,212,0.15))' }}
          >
            <Briefcase className="w-10 h-10" style={{ color: '#a855f7' }} />
          </div>
          <h3 className="text-xl font-bold mb-2">Aucune candidature</h3>
          <p className="mb-6" style={{ color: 'rgba(148,163,184,0.6)' }}>
            Commencez par analyser une offre d'emploi
          </p>
          <NeonButton onClick={() => navigate('/new')}>Analyser une offre</NeonButton>
        </GlassCard>
      ) : (
        <div className="space-y-4">
          {applications.map((app, index) => {
            const { barClass, color } = app.match_score ? getScoreConfig(app.match_score) : {};
            return (
              <div
                key={app.id}
                className="glass-card glow-hover rounded-2xl p-6 cursor-pointer animate-fadeInUp"
                style={{ animationDelay: `${index * 0.05}s` }}
                onClick={() => navigate(`/application/${app.id}`)}
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white mb-1">{app.job.title}</h3>
                    <p className="text-sm" style={{ color: 'rgba(148,163,184,0.7)' }}>{app.job.company}</p>
                  </div>
                  <StatusBadge status={app.status} />
                </div>

                {/* Score */}
                {app.match_score !== null && app.match_score !== undefined ? (
                  <div className="flex items-center gap-3 mb-4">
                    <div className="score-bar-track flex-1">
                      <div
                        className={`h-full rounded-full ${barClass}`}
                        style={{ width: `${app.match_score}%`, transition: 'width 1s ease' }}
                      />
                    </div>
                    <span className="text-sm font-bold w-10 text-right" style={{ color }}>
                      {app.match_score}%
                    </span>
                  </div>
                ) : (
                  <p className="text-xs mb-4" style={{ color: 'rgba(148,163,184,0.4)' }}>
                    Score non calculé · Uploadez votre CV
                  </p>
                )}

                <div className="neon-divider" />

                {/* Footer */}
                <div className="flex items-center gap-4 text-xs" style={{ color: 'rgba(148,163,184,0.5)' }}>
                  {app.applied_date && (
                    <span>📅 {new Date(app.applied_date).toLocaleDateString('fr-FR')}</span>
                  )}
                  {app.cover_letters_count > 0 && (
                    <span>✉️ {app.cover_letters_count} lettre(s)</span>
                  )}
                  {app.job.url && (
                    <a
                      href={app.job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      style={{ color: '#06b6d4' }}
                      className="hover:underline"
                    >
                      🔗 Voir l'offre
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Dashboard;