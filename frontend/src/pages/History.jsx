import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/history/')
      .then(res => setHistory(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="history-page">
      <h1 style={{ marginBottom: '2rem', fontSize: '2rem' }}>Historique des Analyses</h1>
      
      <div className="glass" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--glass-border)', background: 'rgba(255,255,255,0.02)' }}>
              <th style={{ padding: '1.5rem', color: 'var(--text-secondary)' }}>Date</th>
              <th style={{ padding: '1.5rem', color: 'var(--text-secondary)' }}>Type</th>
              <th style={{ padding: '1.5rem', color: 'var(--text-secondary)' }}>Contenu Analysé</th>
              <th style={{ padding: '1.5rem', color: 'var(--text-secondary)' }}>Verdict</th>
              <th style={{ padding: '1.5rem', color: 'var(--text-secondary)' }}>Score</th>
            </tr>
          </thead>
          <tbody>
            {history.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  Aucun historique disponible.
                </td>
              </tr>
            ) : (
              history.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '1.5rem' }}>
                    {format(new Date(item.created_at), "d MMM yyyy, HH:mm", { locale: fr })}
                  </td>
                  <td style={{ padding: '1.5rem', textTransform: 'uppercase', fontSize: '0.9rem' }}>
                    {item.scan_type}
                  </td>
                  <td style={{ padding: '1.5rem', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.content}
                  </td>
                  <td style={{ padding: '1.5rem' }}>
                    <span style={{ 
                      padding: '0.4rem 0.8rem', 
                      borderRadius: '4px', 
                      fontSize: '0.85rem',
                      fontWeight: 'bold',
                      background: item.verdict === 'PHISHING' ? 'rgba(255,71,87,0.2)' : 'rgba(46,213,115,0.2)',
                      color: item.verdict === 'PHISHING' ? 'var(--danger)' : 'var(--safe)'
                    }}>
                      {item.verdict}
                    </span>
                  </td>
                  <td style={{ padding: '1.5rem' }}>
                    {item.risk_score.toFixed(2)}%
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
