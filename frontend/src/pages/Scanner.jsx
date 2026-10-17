import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, ShieldCheck, Link as LinkIcon, Mail, Activity, Loader2, Info } from 'lucide-react';

export default function Scanner() {
  const [scanType, setScanType] = useState('url');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [showAI, setShowAI] = useState(false);

  const handleScan = async () => {
    if (!content.trim()) {
      setError('Veuillez entrer un contenu à analyser.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setShowAI(false);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/analyze/', {
        type: scanType,
        content: content
      });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError('Erreur de connexion avec le serveur.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="scanner-page">
      {/* HERO SECTION */}
      <section className="hero-section" style={{ marginTop: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '1rem' }}>
          Détection de Menaces en Temps Réel
        </h1>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
          Notre moteur d'intelligence artificielle analyse la structure et le contexte pour bloquer le phishing avant qu'il ne frappe.
        </p>
      </section>

      {/* SCANNER BOX */}
      <div className="glass scanner-box" style={{ marginTop: '3rem' }}>
        <div className="type-toggle">
          <button 
            className={`toggle-btn ${scanType === 'url' ? 'active' : ''}`}
            onClick={() => setScanType('url')}
          >
            <LinkIcon size={18} /> Analyser une URL
          </button>
          <button 
            className={`toggle-btn ${scanType === 'email' ? 'active' : ''}`}
            onClick={() => setScanType('email')}
          >
            <Mail size={18} /> Analyser un E-mail
          </button>
        </div>

        <div className="input-group">
          {scanType === 'url' ? (
            <input 
              type="text" 
              className="main-input" 
              placeholder="Collez l'URL suspecte ici..." 
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleScan()}
            />
          ) : (
            <textarea 
              className="main-input" 
              placeholder="Collez le texte de l'e-mail ici..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          )}
          
          <button 
            className="analyze-btn" 
            onClick={handleScan}
            disabled={loading}
          >
            {loading ? (
              <><Loader2 className="spinner" size={20} /> Analyse...</>
            ) : (
              <><Activity size={20} /> Scanner</>
            )}
          </button>
        </div>

        {error && <div style={{ color: 'var(--danger)', marginTop: '1rem', textAlign: 'center' }}>{error}</div>}

        {/* RÉSULTATS */}
        <AnimatePresence>
          {result && (
            <motion.div 
              className={`glass result-card ${result.verdict === 'PHISHING' ? 'phishing' : 'safe'}`}
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: 'auto', marginTop: '3rem' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="result-header">
                <div className="verdict-title">
                  {result.verdict === 'PHISHING' ? <ShieldAlert size={28} /> : <ShieldCheck size={28} />}
                  {result.verdict === 'PHISHING' ? 'MENACE DÉTECTÉE' : 'CONTENU SÉCURISÉ'}
                </div>
                
                {/* Score supprimé selon tes consignes. L'utilisateur veut juste savoir si c'est sûr ou non. */}
                {/* Bouton "En savoir plus" */}
                {result.verdict === 'PHISHING' && (
                  <button 
                    onClick={() => setShowAI(!showAI)}
                    style={{
                      background: 'rgba(255,255,255,0.1)',
                      border: '1px solid var(--glass-border)',
                      color: 'white',
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    <Info size={18} /> {showAI ? 'Masquer le rapport' : 'Rapport de notre IA'}
                  </button>
                )}
              </div>
              
              <AnimatePresence>
                {showAI && (
                  <motion.div 
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="explanation"
                  >
                    <strong>Analyse Sémantique :</strong><br/><br/>
                    {result.explanation}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
