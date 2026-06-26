import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';

function statusBadge(status) {
  if (status === 'Critical') return <span className="badge badge-red">🔴 Critical</span>;
  if (status === 'Warning')  return <span className="badge badge-amber">🟡 Warning</span>;
  return                            <span className="badge badge-green">✅ Good</span>;
}

function WearBar({ label, pct }) {
  const color = pct > 80 ? '#ef4444' : pct > 60 ? '#f59e0b' : '#10b981';
  return (
    <div style={{ marginBottom: '6px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '2px' }}>
        <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{label}</span>
        <span style={{ color: 'var(--text-muted)' }}>{pct}%</span>
      </div>
      <div style={{ height: '6px', background: '#f1f5f9', borderRadius: '3px' }}>
        <div style={{ height: '100%', borderRadius: '3px', width: `${pct}%`, background: color, transition: 'width 0.4s' }} />
      </div>
    </div>
  );
}

function MaintenanceTab({ apiBase }) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);
  const [expanded, setExpanded] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await axios.get(`${apiBase}/maintenance/demo`);
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally { setLoading(false); }
  }, [apiBase]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <div className="loading-overlay"><div className="spinner" /> Loading fleet data...</div>;
  if (error)   return <div className="error-banner" role="alert">⚠️ {error} <button onClick={fetchData} style={{ marginLeft: 'auto', cursor: 'pointer', background: 'none', border: '1px solid #fca5a5', borderRadius: '6px', padding: '4px 10px', color: '#dc2626', fontSize: '0.82rem' }}>Retry</button></div>;

  const bikes = data?.assessments || [];

  return (
    <div>
      <div className="dashboard-header">
        <h2>🔧 Fleet Maintenance Dashboard</h2>
        <p>Monitor bike health, predict maintenance needs, and schedule service</p>
      </div>

      {/* Fleet Summary KPIs */}
      <div className="result-grid" style={{ marginBottom: '1.5rem' }}>
        {[
          { icon: '🚲', label: 'Total Bikes',      value: data.total_bikes,        sub: 'in fleet',         cls: 'demand' },
          { icon: '🔴', label: 'Critical',          value: data.critical_count,     sub: 'need immediate service', cls: 'price' },
          { icon: '🟡', label: 'Warning',           value: data.warning_count,      sub: 'approaching service', cls: 'weather' },
          { icon: '✅', label: 'Good',              value: data.good_count,         sub: 'no action needed', cls: 'ops' },
        ].map((k, i) => (
          <div key={i} className={`result-card ${k.cls}`}>
            <span className="icon">{k.icon}</span>
            <div className="label">{k.label}</div>
            <div className="value">{k.value}</div>
            <div className="sub">{k.sub}</div>
          </div>
        ))}
      </div>

      {/* Avg Health Score */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 className="card-title" style={{ margin: 0 }}>📊 Fleet Average Health Score</h3>
          <strong style={{ fontSize: '1.4rem', color: data.avg_health_score >= 70 ? '#10b981' : data.avg_health_score >= 40 ? '#f59e0b' : '#ef4444' }}>
            {data.avg_health_score}/100
          </strong>
        </div>
        <div style={{ height: '12px', background: '#f1f5f9', borderRadius: '6px' }}>
          <div style={{
            height: '100%', borderRadius: '6px',
            width: `${data.avg_health_score}%`,
            background: data.avg_health_score >= 70
              ? 'linear-gradient(90deg,#10b981,#34d399)'
              : data.avg_health_score >= 40
              ? 'linear-gradient(90deg,#f59e0b,#fbbf24)'
              : 'linear-gradient(90deg,#ef4444,#f87171)',
            transition: 'width 0.6s'
          }} />
        </div>
        {data.bikes_needing_service?.length > 0 && (
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '10px' }}>
            🔧 Bikes needing service: <strong>{data.bikes_needing_service.join(', ')}</strong>
          </p>
        )}
      </div>

      {/* Per-bike Table */}
      <div className="card" style={{ overflowX: 'auto' }}>
        <h3 className="card-title">🚲 Per-Bike Health Report</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.87rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--border)' }}>
              {['Bike ID', 'Usage Hours', 'Days Since Service', 'Health Score', 'Status', 'Next Service', 'Wear Details'].map(h => (
                <th key={h} style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {bikes.map(b => (
              <React.Fragment key={b.bike_id}>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '10px 12px', fontWeight: 600 }}>#{b.bike_id}</td>
                  <td style={{ padding: '10px 12px' }}>{b.usage_hours}h</td>
                  <td style={{ padding: '10px 12px' }}>{b.days_since_service} days</td>
                  <td style={{ padding: '10px 12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '50px', height: '6px', background: '#f1f5f9', borderRadius: '3px' }}>
                        <div style={{ height: '100%', borderRadius: '3px', width: `${b.health_score}%`,
                          background: b.health_score >= 70 ? '#10b981' : b.health_score >= 40 ? '#f59e0b' : '#ef4444' }} />
                      </div>
                      <span style={{ fontWeight: 600 }}>{b.health_score}</span>
                    </div>
                  </td>
                  <td style={{ padding: '10px 12px' }}>{statusBadge(b.status)}</td>
                  <td style={{ padding: '10px 12px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>{b.next_service_in}</td>
                  <td style={{ padding: '10px 12px' }}>
                    <button onClick={() => setExpanded(expanded === b.bike_id ? null : b.bike_id)}
                      style={{ background: 'none', border: '1px solid var(--border)', borderRadius: '6px',
                        padding: '4px 10px', cursor: 'pointer', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {expanded === b.bike_id ? 'Hide ▲' : 'Show ▼'}
                    </button>
                  </td>
                </tr>
                {expanded === b.bike_id && (
                  <tr style={{ background: 'rgba(15,76,129,0.03)' }}>
                    <td colSpan={7} style={{ padding: '14px 16px' }}>
                      {b.alert && (
                        <div className="error-banner" style={{ marginBottom: '12px', background: b.alert.includes('🔴') ? '#fef2f2' : '#fefce8', borderColor: b.alert.includes('🔴') ? '#fca5a5' : '#fde68a', color: b.alert.includes('🔴') ? '#dc2626' : '#92400e' }}>
                          {b.alert}
                        </div>
                      )}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(160px,1fr))', gap: '0 2rem', maxWidth: '600px' }}>
                        {Object.entries(b.wear_components).map(([part, pct]) => (
                          <WearBar key={part} label={part} pct={pct} />
                        ))}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default MaintenanceTab;
