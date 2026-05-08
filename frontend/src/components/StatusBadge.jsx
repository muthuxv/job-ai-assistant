import React from 'react';

const StatusBadge = ({ status }) => {
  const statusConfig = {
    draft: { color: 'bg-slate-600', text: 'Brouillon', icon: '📝' },
    applied: { color: 'bg-neon-cyan', text: 'Envoyée', icon: '📤' },
    interview: { color: 'bg-neon-violet', text: 'Entretien', icon: '🎤' },
    rejected: { color: 'bg-red-500', text: 'Refusée', icon: '❌' },
    offer: { color: 'bg-green-500', text: 'Offre', icon: '🎉' },
  };

  const config = statusConfig[status] || statusConfig.draft;

  return (
    <span className={`
      inline-flex items-center gap-1.5
      px-3 py-1 rounded-full text-xs font-semibold
      ${config.color} text-white
    `}>
      <span>{config.icon}</span>
      {config.text}
    </span>
  );
};

export default StatusBadge;
