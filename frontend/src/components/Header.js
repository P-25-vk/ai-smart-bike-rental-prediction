import React, { useState } from 'react';

function Header({ theme, onToggleTheme, alerts = [], onDismissAlert }) {
  const [showNotifs, setShowNotifs] = useState(false);
  const undismissed = alerts.filter(a => !a.dismissed);

  return (
    <header className="header" role="banner">
      <div className="header-brand">
        <span className="logo" aria-hidden="true">🚲</span>
        <div>
          <h1>AI Smart Bike Rental System</h1>
          <p>XGBoost · Flask · PostgreSQL · AWS · Real-time Analytics</p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Notification Bell */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowNotifs(v => !v)}
            aria-label={`Notifications — ${undismissed.length} active`}
            style={{
              background: 'rgba(255,255,255,0.18)', border: '1px solid rgba(255,255,255,0.3)',
              borderRadius: '50%', width: '38px', height: '38px', cursor: 'pointer',
              fontSize: '1.1rem', color: '#fff', position: 'relative'
            }}
          >
            🔔
            {undismissed.length > 0 && (
              <span style={{
                position: 'absolute', top: '-4px', right: '-4px',
                background: '#ef4444', color: '#fff', borderRadius: '50%',
                fontSize: '0.65rem', width: '18px', height: '18px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700
              }}>
                {undismissed.length}
              </span>
            )}
          </button>

          {showNotifs && (
            <div style={{
              position: 'absolute', right: 0, top: '44px', width: '320px',
              background: 'var(--surface)', border: '1px solid var(--border)',
              borderRadius: '12px', boxShadow: 'var(--shadow-lg)', zIndex: 1000,
              maxHeight: '360px', overflowY: 'auto'
            }}>
              <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text)' }}>
                🔔 Notifications ({undismissed.length} active)
              </div>
              {undismissed.length === 0 && (
                <div style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '0.87rem', textAlign: 'center' }}>
                  ✅ No active alerts
                </div>
              )}
              {undismissed.map(a => (
                <div key={a.id} style={{
                  padding: '12px 16px', borderBottom: '1px solid var(--border)',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px'
                }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '2px' }}>
                      {a.type} · {a.ref}
                    </div>
                    <div style={{ fontSize: '0.83rem', color: 'var(--text)' }}>{a.msg}</div>
                  </div>
                  <button
                    onClick={() => onDismissAlert(a.id)}
                    aria-label="Dismiss alert"
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '0.9rem', flexShrink: 0 }}
                  >✕</button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={onToggleTheme}
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          style={{
            background: 'rgba(255,255,255,0.18)', border: '1px solid rgba(255,255,255,0.3)',
            borderRadius: '20px', padding: '6px 14px', cursor: 'pointer',
            fontSize: '0.85rem', color: '#fff', fontWeight: 600
          }}
        >
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>

        <span className="header-badge">⚡ XGBoost</span>
      </div>
    </header>
  );
}

export default Header;
