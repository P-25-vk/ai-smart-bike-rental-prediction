import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  LineElement, PointElement, Title, Tooltip, Legend, Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend, Filler);

const DEFAULTS = {
  temperature: 25, humidity: 60, windspeed: 10,
  rainfall: 0, available_bikes: 20, weekday: 1,
  month: 6, holiday: 0, event_type: 'None'
};

function ForecastTab({ apiBase }) {
  const [form, setForm]       = useState(DEFAULTS);
  const [forecast, setForecast] = useState(null);
  const [peaks, setPeaks]     = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : (name === 'event_type' ? value : parseInt(value, 10))
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null); setForecast(null);
    try {
      const res = await axios.post(`${apiBase}/forecast`, form);
      setForecast(res.data.forecast);
      setPeaks(res.data.peak_hours);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = forecast ? {
    labels: forecast.map(h => h.label),
    datasets: [{
      data: forecast.map(h => h.predicted_demand),
      borderColor: '#0f4c81',
      backgroundColor: 'rgba(15,76,129,0.12)',
      borderWidth: 2.5,
      pointBackgroundColor: forecast.map(h => h.peak ? '#f59e0b' : '#0f4c81'),
      pointRadius: forecast.map(h => h.peak ? 8 : 4),
      tension: 0.4, fill: true,
    }]
  } : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1e293b', titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1', padding: 10, cornerRadius: 8,
        callbacks: { label: ctx => ` ${ctx.parsed.y.toFixed(1)} rentals` }
      }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 10 } } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { color: '#64748b' } }
    }
  };

  return (
    <div>
      <div className="dashboard-header">
        <h2>📈 24-Hour Demand Forecast</h2>
        <p>Predict hourly bike demand for the next 24 hours at your station</p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title">⚙️ Forecast Parameters</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {[
              { key: 'temperature', label: '🌡️ Temperature (°C)', type: 'number', min: -10, max: 50, step: 0.1 },
              { key: 'humidity',    label: '💧 Humidity (%)',      type: 'number', min: 0, max: 100, step: 1 },
              { key: 'windspeed',   label: '💨 Wind Speed (km/h)', type: 'number', min: 0, max: 100, step: 0.1 },
              { key: 'rainfall',    label: '🌧️ Rainfall (mm)',     type: 'number', min: 0, max: 200, step: 0.1 },
              { key: 'available_bikes', label: '🚲 Available Bikes', type: 'number', min: 0, max: 200, step: 1 },
            ].map(f => (
              <div className="form-group" key={f.key}>
                <label htmlFor={f.key}>{f.label}</label>
                <input id={f.key} type="number" name={f.key} value={form[f.key]}
                  onChange={handleChange} min={f.min} max={f.max} step={f.step} />
              </div>
            ))}
            <div className="form-group">
              <label htmlFor="f-weekday">📅 Weekday</label>
              <select id="f-weekday" name="weekday" value={form.weekday} onChange={handleChange}>
                {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map((d,i) => (
                  <option key={i} value={i}>{d}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="f-month">📆 Month</label>
              <select id="f-month" name="month" value={form.month} onChange={handleChange}>
                {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].map((m,i) => (
                  <option key={i+1} value={i+1}>{m}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="f-event">🎪 Event Type</label>
              <select id="f-event" name="event_type" value={form.event_type} onChange={handleChange}>
                {['None','Festival','Concert','Sports'].map(e => (
                  <option key={e} value={e}>{e === 'None' ? 'No Event' : e}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="f-holiday">🎉 Holiday</label>
              <select id="f-holiday" name="holiday" value={form.holiday} onChange={handleChange}>
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </div>
          </div>
          <button type="submit" className="predict-btn" disabled={loading} style={{ marginTop: '1rem' }}>
            {loading ? <><span className="spinner" aria-hidden="true" /> Forecasting...</> : '📈 Generate Forecast'}
          </button>
        </form>
      </div>

      {error && <div className="error-banner" role="alert">⚠️ {error}</div>}

      {forecast && (
        <>
          {/* Peak Hours */}
          <div className="result-grid" style={{ marginBottom: '1.5rem' }}>
            {peaks.map((p, i) => (
              <div key={i} className="result-card demand">
                <span className="icon">🏆</span>
                <div className="label">Peak Hour #{i + 1}</div>
                <div className="value">{p.label}</div>
                <div className="sub">{p.predicted_demand} rentals expected</div>
              </div>
            ))}
            <div className="result-card ops">
              <span className="icon">📊</span>
              <div className="label">Daily Total</div>
              <div className="value">{forecast.reduce((a, h) => a + h.predicted_demand, 0).toFixed(0)}</div>
              <div className="sub">estimated rentals</div>
            </div>
          </div>

          {/* Chart */}
          <div className="chart-card">
            <h3>🕐 Hourly Demand Forecast — <span style={{ color: '#f59e0b' }}>● Peak Hour</span></h3>
            <Line data={chartData} options={chartOptions} />
          </div>

          {/* Hourly Table */}
          <div className="card" style={{ marginTop: '1.5rem', overflowX: 'auto' }}>
            <h3 className="card-title">📋 Hourly Breakdown</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.87rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  {['Hour', 'Demand', 'Level'].map(h => (
                    <th key={h} style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {forecast.map(h => {
                  const level = h.predicted_demand > 80 ? { label: 'High', cls: 'badge-red' }
                               : h.predicted_demand > 50 ? { label: 'Moderate', cls: 'badge-amber' }
                               : { label: 'Low', cls: 'badge-green' };
                  return (
                    <tr key={h.hour} style={{ borderBottom: '1px solid var(--border)', background: h.peak ? 'rgba(245,158,11,0.05)' : '' }}>
                      <td style={{ padding: '8px 12px', fontWeight: h.peak ? 700 : 400 }}>{h.label} {h.peak && '⭐'}</td>
                      <td style={{ padding: '8px 12px', fontWeight: 600 }}>{h.predicted_demand}</td>
                      <td style={{ padding: '8px 12px' }}><span className={`badge ${level.cls}`}>{level.label}</span></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default ForecastTab;
