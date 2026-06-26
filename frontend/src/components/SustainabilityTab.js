import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BADGE_STYLE = {
  '🌱 Eco Starter':      { bg: '#f1f5f9', color: '#475569' },
  '🥉 Bronze Eco Rider': { bg: '#fef3c7', color: '#92400e' },
  '🥈 Silver Eco Rider': { bg: '#f1f5f9', color: '#475569' },
  '🥇 Gold Eco Rider':   { bg: '#fef9c3', color: '#854d0e' },
  '🏆 Platinum Eco Rider': { bg: '#ede9fe', color: '#5b21b6' },
};

function SustainabilityTab({ apiBase }) {
  const [distKm, setDistKm]   = useState(5);
  const [trips, setTrips]     = useState(10);
  const [eco, setEco]         = useState(null);
  const [fleet, setFleet]     = useState(null);
  const [loading, setLoading] = useState(false);
  const [fleetLoading, setFleetLoading] = useState(true);
  const [error, setError]     = useState(null);

  const fetchFleet = useCallback(async () => {
    setFleetLoading(true);
    try {
      const res = await axios.get(`${apiBase}/sustainability/fleet`);
      setFleet(res.data);
    } catch (_) {}
    finally { setFleetLoading(false); }
  }, [apiBase]);

  useEffect(() => { fetchFleet(); }, [fetchFleet]);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await axios.post(`${apiBase}/sustainability`, { distance_km: distKm, trips });
      setEco(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally { setLoading(false); }
  };

  const badgeStyle = eco ? (BADGE_STYLE[eco.badge] || { bg: '#f1f5f9', color: '#475569' }) : {};

  return (
    <div>
      <div className="dashboard-header">
        <h2>🌱 Sustainability Dashboard</h2>
        <p>Track carbon savings, eco scores, and environmental impact</p>
      </div>

      {/* Fleet Stats */}
      {!fleetLoading && fleet && (
        <div className="result-grid" style={{ marginBottom: '1.5rem' }}>
          {[
            { icon: '🚲', label: 'Total Rides',      value: fleet.total_rides?.toLocaleString(),  sub: 'recorded rides', cls: 'demand' },
            { icon: '🛣️', label: 'Total Distance',   value: `${fleet.total_km?.toLocaleString()} km`, sub: 'cycled by all users', cls: 'price' },
            { icon: '🌍', label: 'CO₂ Saved',        value: `${fleet.co2_saved_kg?.toLocaleString()} kg`, sub: 'vs driving a car', cls: 'weather' },
            { icon: '🌳', label: 'Trees Equivalent', value: fleet.trees_equivalent?.toLocaleString(), sub: 'trees worth of CO₂/year', cls: 'ops' },
          ].map((k, i) => (
            <div key={i} className={`result-card ${k.cls}`}>
              <span className="icon">{k.icon}</span>
              <div className="label">{k.label}</div>
              <div className="value" style={{ fontSize: '1.5rem' }}>{k.value}</div>
              <div className="sub">{k.sub}</div>
            </div>
          ))}
        </div>
      )}

      {/* Personal Calculator */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title">🧮 Personal CO₂ Savings Calculator</h3>
        <form onSubmit={handleCalculate}>
          <div className="form-grid" style={{ maxWidth: '500px' }}>
            <div className="form-group">
              <label htmlFor="dist">🛣️ Distance per trip (km)</label>
              <input id="dist" type="number" min="0.1" max="100" step="0.1"
                value={distKm} onChange={e => setDistKm(parseFloat(e.target.value))} />
            </div>
            <div className="form-group">
              <label htmlFor="trips">🔢 Number of trips</label>
              <input id="trips" type="number" min="1" max="1000" step="1"
                value={trips} onChange={e => setTrips(parseInt(e.target.value))} />
            </div>
          </div>
          <button type="submit" className="predict-btn" disabled={loading} style={{ marginTop: '1rem' }}>
            {loading ? <><span className="spinner" aria-hidden="true" /> Calculating...</> : '🌱 Calculate My Impact'}
          </button>
        </form>
        {error && <div className="error-banner" role="alert" style={{ marginTop: '1rem' }}>⚠️ {error}</div>}
      </div>

      {/* Results */}
      {eco && (
        <div className="card">
          <h3 className="card-title">🏆 Your Eco Profile</h3>
          <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'flex-start' }}>

            {/* Badge */}
            <div style={{
              padding: '1.5rem 2rem', borderRadius: '16px', textAlign: 'center',
              background: badgeStyle.bg, color: badgeStyle.color, minWidth: '180px'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{eco.badge.split(' ')[0]}</div>
              <div style={{ fontWeight: 700, fontSize: '1rem' }}>{eco.badge.replace(/^[^\s]+\s/, '')}</div>
              <div style={{ fontSize: '0.82rem', marginTop: '4px', opacity: 0.8 }}>{eco.message}</div>
            </div>

            {/* Stats */}
            <div style={{ flex: 1, minWidth: '220px' }}>
              {[
                { label: 'Total Distance', value: `${eco.distance_km} km` },
                { label: 'CO₂ Saved',      value: `${eco.co2_saved_kg} kg (${eco.co2_saved_g} g)` },
                { label: 'Trees Equivalent', value: `${eco.trees_equivalent} trees/year` },
              ].map(stat => (
                <div key={stat.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>{stat.label}</span>
                  <strong style={{ color: 'var(--text)', fontSize: '0.88rem' }}>{stat.value}</strong>
                </div>
              ))}
              {/* Eco Score Bar */}
              <div style={{ marginTop: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text)' }}>Eco Score</span>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{eco.eco_score}/100</span>
                </div>
                <div style={{ height: '10px', background: '#f1f5f9', borderRadius: '5px' }}>
                  <div style={{
                    height: '100%', borderRadius: '5px',
                    width: `${eco.eco_score}%`,
                    background: 'linear-gradient(90deg, #10b981, #0f4c81)',
                    transition: 'width 0.6s ease'
                  }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SustainabilityTab;
