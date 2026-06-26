import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';

function alertBadge(alert) {
  if (!alert) return null;
  if (alert.includes('LOW STOCK') || alert.includes('CRITICAL') || alert.includes('SHORTAGE'))
    return <span className="badge badge-red">🔴 Critical</span>;
  if (alert.includes('WARNING') || alert.includes('OVERDUE') || alert.includes('NEAR FULL'))
    return <span className="badge badge-amber">🟡 Warning</span>;
  if (alert.includes('OVERSTOCKED'))
    return <span className="badge badge-blue">📦 Info</span>;
  return <span className="badge badge-green">✅ OK</span>;
}

function OperationsTab({ apiBase }) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await axios.get(`${apiBase}/operations/demo`);
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <div className="loading-overlay"><div className="spinner" /> Loading operations data...</div>;
  if (error)   return <div className="error-banner" role="alert">⚠️ {error} <button onClick={fetchData} style={{ marginLeft: 'auto', cursor: 'pointer', background: 'none', border: '1px solid #fca5a5', borderRadius: '6px', padding: '4px 10px', color: '#dc2626', fontSize: '0.82rem' }}>Retry</button></div>;

  const stations = data?.stations || [];
  const plan     = data?.redistribution_plan || [];
  const alertCount = stations.filter(s => s.alert).length;

  return (
    <div>
      <div className="dashboard-header">
        <h2>🚦 Smart Operations Center</h2>
        <p>Real-time station monitoring, alerts, and bike redistribution recommendations</p>
      </div>

      {/* KPI Row */}
      <div className="result-grid" style={{ marginBottom: '1.5rem' }}>
        {[
          { icon: '🚉', label: 'Stations Monitored', value: stations.length, sub: 'active stations', cls: 'demand' },
          { icon: '⚠️', label: 'Active Alerts',      value: alertCount, sub: 'need attention', cls: 'price' },
          { icon: '🔄', label: 'Transfers Needed',   value: plan.length, sub: 'redistribution tasks', cls: 'weather' },
          { icon: '✅', label: 'Stations OK',         value: stations.filter(s => !s.alert).length, sub: 'no action needed', cls: 'ops' },
        ].map((k, i) => (
          <div key={i} className={`result-card ${k.cls}`}>
            <span className="icon">{k.icon}</span>
            <div className="label">{k.label}</div>
            <div className="value">{k.value}</div>
            <div className="sub">{k.sub}</div>
          </div>
        ))}
      </div>

      {/* Station Table */}
      <div className="card" style={{ marginBottom: '1.5rem', overflowX: 'auto' }}>
        <h3 className="card-title">📍 Station Status</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.87rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--border)' }}>
              {['Station', 'Available', 'Docks', 'Occupancy', 'Pred. Demand', 'Status', 'Action'].map(h => (
                <th key={h} style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {stations.map(s => (
              <tr key={s.station_id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 600 }}>#{s.station_id}</td>
                <td style={{ padding: '10px 12px' }}>{s.available_bikes}</td>
                <td style={{ padding: '10px 12px' }}>{s.total_docks}</td>
                <td style={{ padding: '10px 12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ flex: 1, height: '6px', background: '#f1f5f9', borderRadius: '3px', minWidth: '60px' }}>
                      <div style={{ height: '100%', borderRadius: '3px', width: `${s.occupancy_pct}%`,
                        background: s.occupancy_pct > 85 ? '#ef4444' : s.occupancy_pct > 60 ? '#f59e0b' : '#10b981' }} />
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.occupancy_pct}%</span>
                  </div>
                </td>
                <td style={{ padding: '10px 12px' }}>{s.predicted_demand}</td>
                <td style={{ padding: '10px 12px' }}>{alertBadge(s.alert)}</td>
                <td style={{ padding: '10px 12px', fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '200px' }}>{s.action || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Redistribution Plan */}
      {plan.length > 0 && (
        <div className="card">
          <h3 className="card-title">🔄 Redistribution Plan</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {plan.map((p, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '16px', padding: '14px 16px',
                border: '1px solid var(--border)', borderRadius: '10px', background: 'var(--surface)'
              }}>
                <span className={`badge ${p.priority === 'High' ? 'badge-red' : 'badge-amber'}`}>{p.priority}</span>
                <div style={{ flex: 1 }}>
                  <strong>Station #{p.from_station}</strong>
                  <span style={{ color: 'var(--text-muted)', margin: '0 8px' }}>→</span>
                  <strong>Station #{p.to_station}</strong>
                  <span style={{ color: 'var(--text-muted)', marginLeft: '8px', fontSize: '0.85rem' }}>
                    Move {p.bikes_to_move} bikes
                  </span>
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{p.reason}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {plan.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
          ✅ No redistribution needed — all stations are balanced.
        </div>
      )}
    </div>
  );
}

export default OperationsTab;
