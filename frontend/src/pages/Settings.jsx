import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Check, ExternalLink, Eye, EyeOff } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import NeonButton from '../components/NeonButton';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const PROVIDERS = {
  gemini: {
    name: 'Google Gemini',
    color: '#06b6d4',
    description: 'Rapide, gratuit, idéal pour démarrer',
    badge: 'Gratuit',
    badgeColor: 'rgba(74,222,128,0.2)',
    badgeBorder: 'rgba(74,222,128,0.4)',
    badgeText: '#4ade80',
    docsUrl: 'https://makersuite.google.com/app/apikey',
    placeholder: 'AIza...',
  },
  claude: {
    name: 'Anthropic Claude',
    color: '#a855f7',
    description: 'Meilleur pour l\'écriture et l\'analyse nuancée',
    badge: 'Payant',
    badgeColor: 'rgba(168,85,247,0.1)',
    badgeBorder: 'rgba(168,85,247,0.3)',
    badgeText: '#a855f7',
    docsUrl: 'https://console.anthropic.com',
    placeholder: 'sk-ant-...',
  },
  openai: {
    name: 'OpenAI GPT',
    color: '#10b981',
    description: 'GPT-4o-mini, polyvalent et fiable',
    badge: 'Payant',
    badgeColor: 'rgba(16,185,129,0.1)',
    badgeBorder: 'rgba(16,185,129,0.3)',
    badgeText: '#10b981',
    docsUrl: 'https://platform.openai.com/api-keys',
    placeholder: 'sk-...',
  }
};

const Settings = () => {
  const [currentSettings, setCurrentSettings] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { loadSettings(); }, []);

  const loadSettings = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/settings/`);
      setCurrentSettings(data);
      setSelectedProvider(data.provider || 'gemini');
    } catch (err) {
      console.error('Erreur chargement settings:', err);
    }
  };

  const handleSave = async () => {
    if (!apiKey.trim()) {
      setError('La clé API est requise');
      return;
    }

    setSaving(true);
    setError('');

    try {
      await axios.post(`${API_URL}/settings/`, {
        provider: selectedProvider,
        api_key: apiKey,
      });

      setSaved(true);
      setApiKey('');
      await loadSettings();
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">

      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ background: 'rgba(168,85,247,0.15)', border: '1px solid rgba(168,85,247,0.3)' }}>
          <SettingsIcon className="w-6 h-6" style={{ color: '#a855f7' }} />
        </div>
        <div>
          <h1 className="text-3xl font-bold neon-gradient-text">Paramètres</h1>
          <p style={{ color: 'rgba(148,163,184,0.7)' }}>Configurez votre provider IA</p>
        </div>
      </div>

      {/* Current Provider */}
      {currentSettings?.api_key_set && (
        <div className="glass-card rounded-2xl p-5 mb-6 flex items-center gap-4"
          style={{ borderColor: 'rgba(74,222,128,0.3)' }}>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'rgba(74,222,128,0.15)' }}>
            <Check className="w-5 h-5" style={{ color: '#4ade80' }} />
          </div>
          <div>
            <p className="font-semibold" style={{ color: '#4ade80' }}>
              Provider actuel : {PROVIDERS[currentSettings.provider]?.name}
            </p>
            <p className="text-sm" style={{ color: 'rgba(148,163,184,0.6)' }}>
              Clé API configurée · Modèle : {currentSettings.model_name}
            </p>
          </div>
        </div>
      )}

      {/* Provider Selection */}
      <GlassCard hover={false} className="mb-6">
        <p className="text-sm font-semibold mb-4" style={{ color: 'rgba(148,163,184,0.6)' }}>
          CHOISIR UN PROVIDER
        </p>

        <div className="space-y-3 mb-6">
          {Object.entries(PROVIDERS).map(([key, config]) => (
            <button
              key={key}
              onClick={() => { setSelectedProvider(key); setApiKey(''); setError(''); }}
              className="w-full flex items-center justify-between p-4 rounded-xl transition-all text-left"
              style={{
                background: selectedProvider === key
                  ? `${config.color}15`
                  : 'rgba(255,255,255,0.03)',
                border: `1px solid ${selectedProvider === key
                  ? `${config.color}40`
                  : 'rgba(255,255,255,0.08)'}`,
                boxShadow: selectedProvider === key
                  ? `0 0 15px ${config.color}20`
                  : 'none',
              }}
            >
              <div className="flex items-center gap-4">
                {/* Radio indicator */}
                <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{
                    border: `2px solid ${selectedProvider === key ? config.color : 'rgba(148,163,184,0.3)'}`,
                    background: selectedProvider === key ? config.color : 'transparent'
                  }}>
                  {selectedProvider === key && (
                    <div className="w-2 h-2 rounded-full bg-white" />
                  )}
                </div>
                <div>
                  <p className="font-semibold text-white">{config.name}</p>
                  <p className="text-sm" style={{ color: 'rgba(148,163,184,0.6)' }}>
                    {config.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs px-2.5 py-1 rounded-full font-semibold"
                  style={{
                    background: config.badgeColor,
                    border: `1px solid ${config.badgeBorder}`,
                    color: config.badgeText
                  }}>
                  {config.badge}
                </span>
                <a
                  href={config.docsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={e => e.stopPropagation()}
                  className="text-xs flex items-center gap-1 transition-all"
                  style={{ color: 'rgba(148,163,184,0.5)' }}
                  onMouseEnter={e => e.currentTarget.style.color = config.color}
                  onMouseLeave={e => e.currentTarget.style.color = 'rgba(148,163,184,0.5)'}
                >
                  Obtenir une clé <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </button>
          ))}
        </div>

        {/* API Key Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2" style={{ color: 'rgba(148,163,184,0.8)' }}>
            Clé API {PROVIDERS[selectedProvider]?.name}
            <span style={{ color: '#ec4899' }}> *</span>
          </label>
          <div className="relative">
            <input
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder={PROVIDERS[selectedProvider]?.placeholder}
              className="neon-input w-full px-4 py-3 rounded-xl pr-12 text-sm"
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 transition-all"
              style={{ color: 'rgba(148,163,184,0.5)' }}
            >
              {showKey
                ? <EyeOff className="w-5 h-5" />
                : <Eye className="w-5 h-5" />
              }
            </button>
          </div>
          <p className="text-xs mt-2" style={{ color: 'rgba(148,163,184,0.4)' }}>
            🔒 Votre clé est stockée localement et n'est jamais partagée
          </p>
        </div>

        {error && (
          <div className="mb-4 p-4 rounded-xl text-sm"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}>
            ❌ {error}
          </div>
        )}

        {saved && (
          <div className="mb-4 p-4 rounded-xl text-sm"
            style={{ background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.3)', color: '#4ade80' }}>
            ✅ Provider configuré avec succès !
          </div>
        )}

        <NeonButton
          onClick={handleSave}
          disabled={saving || !apiKey.trim()}
          className="w-full flex items-center justify-center gap-2 py-4"
        >
          {saving ? (
            <>
              <div className="w-4 h-4 rounded-full border-2 border-t-transparent animate-spin"
                style={{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: 'white' }} />
              Test de la clé en cours...
            </>
          ) : (
            <>💾 Sauvegarder</>
          )}
        </NeonButton>
      </GlassCard>

      {/* Info box */}
      <div className="rounded-xl p-4"
        style={{ background: 'rgba(168,85,247,0.06)', border: '1px solid rgba(168,85,247,0.2)' }}>
        <p className="text-sm font-semibold mb-2" style={{ color: '#a855f7' }}>
          💡 Quel provider choisir ?
        </p>
        <ul className="space-y-1 text-sm" style={{ color: 'rgba(148,163,184,0.7)' }}>
          <li>→ <strong className="text-white">Gemini</strong> : Gratuit, idéal pour tester et démarrer</li>
          <li>→ <strong className="text-white">Claude</strong> : Meilleure qualité d'écriture pour les lettres de motivation</li>
          <li>→ <strong className="text-white">OpenAI</strong> : Très polyvalent, excellent pour l'analyse technique</li>
        </ul>
      </div>

    </div>
  );
};

export default Settings;