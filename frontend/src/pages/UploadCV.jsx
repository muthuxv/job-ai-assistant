// src/pages/UploadCV.jsx
import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle, FileText, Trash2 } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import NeonButton from '../components/NeonButton';
import { uploadCV, getAllCVs, getActiveCV } from '../services/api';

const UploadCV = ({ onCVUploaded }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [cvs, setCvs] = useState([]);
  const [activeCV, setActiveCV] = useState(null);
  const [needsRecalculation, setNeedsRecalculation] = useState(false);

  useEffect(() => {
    loadCVs();
  }, []);

  const loadCVs = async () => {
    try {
      const allCvs = await getAllCVs();
      const active = await getActiveCV();
      setCvs(allCvs);
      setActiveCV(active);
    } catch (error) {
      console.error('Erreur chargement CVs:', error);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
    } else {
      alert('Veuillez sélectionner un fichier PDF');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress('📤 Upload en cours...');

    try {
      setUploadProgress('🧠 Analyse du CV avec IA...');
      const result = await uploadCV(file);

      setUploadProgress('✅ CV analysé avec succès !');
      
      // Si des candidatures existent sans score
      if (result.applications_without_score > 0) {
        setNeedsRecalculation(true);
      }

      setFile(null);
      await loadCVs();
      
      if (onCVUploaded) {
        onCVUploaded(result);
      }

      setTimeout(() => {
        setUploadProgress('');
      }, 2000);

    } catch (error) {
      console.error('Erreur upload:', error);
      alert('❌ Erreur lors de l\'upload : ' + (error.response?.data?.detail || error.message));
      setUploadProgress('');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-neon-violet to-neon-cyan bg-clip-text text-transparent">
          Mon CV
        </h1>
        <p className="text-slate-400">
          Uploadez votre CV pour des candidatures personnalisées
        </p>
      </div>

      {/* Upload Section */}
      <GlassCard className="mb-6">
        <div className="text-center">
          <div className="mb-6">
            <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-neon-violet/20 to-neon-cyan/20 flex items-center justify-center mb-4">
              <Upload className="w-10 h-10 text-neon-violet" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Uploader votre CV</h2>
            <p className="text-slate-400">
              Format PDF uniquement • Max 16 MB
            </p>
          </div>

          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            id="cv-upload"
          />

          <label
            htmlFor="cv-upload"
            className="
              inline-flex items-center gap-2 px-6 py-3 mb-4
              rounded-xl border-2 border-dashed border-neon-violet/50
              hover:border-neon-violet hover:bg-neon-violet/5
              cursor-pointer transition-all duration-300
            "
          >
            <FileText className="w-5 h-5" />
            <span>{file ? file.name : 'Sélectionner un fichier'}</span>
          </label>

          {file && (
            <div className="mb-4">
              <NeonButton
                onClick={handleUpload}
                disabled={uploading}
                variant="violet"
                className="w-full max-w-xs"
              >
                {uploading ? '⏳ Upload en cours...' : '🚀 Analyser le CV'}
              </NeonButton>
            </div>
          )}

          {uploadProgress && (
            <div className="mt-4 p-4 rounded-xl bg-neon-violet/10 border border-neon-violet/30">
              <p className="text-neon-violet font-medium">{uploadProgress}</p>
            </div>
          )}
        </div>
      </GlassCard>

      {/* Active CV */}
      {activeCV && (
        <GlassCard neonColor="cyan" className="mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-neon-cyan/20 flex items-center justify-center flex-shrink-0">
                <CheckCircle className="w-6 h-6 text-neon-cyan" />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-lg font-bold">CV Actif</h3>
                  <span className="px-2 py-0.5 rounded-full bg-neon-cyan/20 text-neon-cyan text-xs font-semibold">
                    ACTIF
                  </span>
                </div>
                <p className="text-slate-400 text-sm mb-2">{activeCV.filename}</p>
                <div className="flex flex-wrap gap-2 mt-3">
                  {activeCV.parsed_data?.personal_info?.name && (
                    <span className="px-3 py-1 rounded-full bg-white/5 text-sm">
                      👤 {activeCV.parsed_data.personal_info.name}
                    </span>
                  )}
                  {activeCV.parsed_data?.experience?.length > 0 && (
                    <span className="px-3 py-1 rounded-full bg-white/5 text-sm">
                      💼 {activeCV.parsed_data.experience.length} expériences
                    </span>
                  )}
                  {activeCV.parsed_data?.technical_skills && (
                    <span className="px-3 py-1 rounded-full bg-white/5 text-sm">
                      🛠️ {Object.values(activeCV.parsed_data.technical_skills).flat().length} compétences
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </GlassCard>
      )}

      {/* CV History */}
      {cvs.length > 1 && (
        <GlassCard>
          <h3 className="text-xl font-bold mb-4">Historique des CV</h3>
          <div className="space-y-3">
            {cvs.filter(cv => cv.id !== activeCV?.id).map((cv) => (
              <div
                key={cv.id}
                className="flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all"
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-slate-400" />
                  <div>
                    <p className="font-medium">{cv.filename}</p>
                    <p className="text-sm text-slate-400">
                      {new Date(cv.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
};

export default UploadCV;