import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, ShieldCheck, ShieldAlert, Target } from 'lucide-react';

const COLORS = ['#ef4444', '#10b981']; // Red for Phishing, Green for Safe

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/stats/')
      .then(res => setStats(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!stats) return <div style={{padding: '2rem'}}>Chargement des statistiques...</div>;

  const pieData = [
    { name: 'Menaces', value: stats.phishing_count },
    { name: 'Sécurisé', value: stats.safe_count }
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="dashboard-page">
      <h1 style={{ marginBottom: '2rem', fontSize: '2rem' }}>Tableau de bord Analytique</h1>
      
      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <div className="glass" style={{ padding: '1.5rem' }}>
          <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={18}/> Total Scans
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginTop: '10px' }}>{stats.total_scans}</div>
        </div>
        <div className="glass" style={{ padding: '1.5rem', borderLeft: '4px solid var(--danger)' }}>
          <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={18}/> Menaces Bloquées
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginTop: '10px', color: 'var(--danger)' }}>{stats.phishing_count}</div>
        </div>
        <div className="glass" style={{ padding: '1.5rem', borderLeft: '4px solid var(--safe)' }}>
          <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={18}/> Contenus Sûrs
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginTop: '10px', color: 'var(--safe)' }}>{stats.safe_count}</div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
        
        <div className="glass" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={20} color="var(--accent-primary)"/> Répartition Globale
          </h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-dark)', border: '1px solid var(--glass-border)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Vecteurs de Menaces</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.threat_vectors}>
                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" allowDecimals={false} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-dark)', border: '1px solid var(--glass-border)' }} cursor={{fill: 'rgba(255,255,255,0.05)'}}/>
                <Bar dataKey="value" fill="var(--danger)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </motion.div>
  );
}
