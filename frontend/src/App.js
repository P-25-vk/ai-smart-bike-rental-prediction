import React, { useState, useEffect } from 'react';
import './App.css';
import PredictionForm from './components/PredictionForm';
import ResultCards from './components/ResultCards';
import GraphDashboard from './components/GraphDashboard';
import ForecastTab from './components/ForecastTab';
import OperationsTab from './components/OperationsTab';
import SustainabilityTab from './components/SustainabilityTab';
import MaintenanceTab from './components/MaintenanceTab';
import Header from './components/Header';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const TABS = [
  { key: 'predict',      label: '🎯 Predict' },
  { key: 'forecast',     label: '📈 24h Forecast' },
  { key: 'dashboard',    label: '📊 Analytics' },
  { key: 'operations',   label: '🚦 Operations' },
  { key: 'sustainability', label: '🌱 Sustainability' },
  { key: 'maintenance',  label: '🔧 Maintenance' },
];

function App() {
  const [result, setResult]       = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [activeTab, setActiveTab] = useState('predict');
  const [theme, setTheme]         = useState(() => localStorage.getItem('theme') || 'light');
  const [alerts, setAlerts]       = useState([]);

  // Apply theme to body
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Load notifications on start
  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const [opsRes, maintRes] = await Promise.all([
          axios.get(`${API_BASE}/operations/demo`).catch(() => null),
          axios.get(`${API_BASE}/maintenance/demo`).catch(() => null),
        ]);
        const newAlerts = [];
        if (opsRes?.data?.stations) {
          opsRes.data.stations.forEach(s => {
            if (s.alert) newAlerts.push({ id: `ops-${s.station_id}`, type: 'Operations', ref: `Station ${s.station_id}`, msg: s.alert, dismissed: false });
          });
        }
        if (maintRes?.data?.assessments) {
          maintRes.data.assessments.forEach(b => {
            if (b.alert) newAlerts.push({ id: `maint-${b.bike_id}`, type: 'Maintenance', ref: `Bike ${b.bike_id}`, msg: b.alert, dismissed: false });
          });
        }
        setAlerts(newAlerts);
      } catch (_) {}
    };
    loadAlerts();
  }, []);

  const handlePredict = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await axios.post(`${API_BASE}/predict`, formData, {
        headers: { 'Content-Type': 'application/json' }
      });
      setResult(response.data);
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Prediction failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const undismissed = alerts.filter(a => !a.dismissed);

  return (
    <div className="app">
      <Header
        theme={theme}
        onToggleTheme={() => setTheme(t => t === 'light' ? 'dark' : 'light')}
        alerts={alerts}
        onDismissAlert={(id) => setAlerts(prev => prev.map(a => a.id === id ? {...a, dismissed: true} : a))}
      />

      <nav className="tab-nav" role="navigation" aria-label="Main navigation">
        {TABS.map(t => (
          <button
            key={t.key}
            className={`tab-btn ${activeTab === t.key ? 'active' : ''}`}
            onClick={() => setActiveTab(t.key)}
            aria-current={activeTab === t.key ? 'page' : undefined}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="main-content">

        {activeTab === 'predict' && (
          <div className="predict-page">
            <PredictionForm onSubmit={handlePredict} loading={loading} />
            {error && (
              <div className="error-banner" role="alert">
                <span>⚠️</span> {error}
              </div>
            )}
            {result && <ResultCards result={result} />}
          </div>
        )}

        {activeTab === 'forecast' && (
          <ForecastTab apiBase={API_BASE} />
        )}

        {activeTab === 'dashboard' && (
          <GraphDashboard apiBase={API_BASE} />
        )}

        {activeTab === 'operations' && (
          <OperationsTab apiBase={API_BASE} />
        )}

        {activeTab === 'sustainability' && (
          <SustainabilityTab apiBase={API_BASE} />
        )}

        {activeTab === 'maintenance' && (
          <MaintenanceTab apiBase={API_BASE} />
        )}

      </main>

      <footer className="footer">
        <p>🚲 AI-Powered Smart Bike Rental System &nbsp;|&nbsp; React · Flask · XGBoost · PostgreSQL · AWS</p>
      </footer>
    </div>
  );
}

export default App;
