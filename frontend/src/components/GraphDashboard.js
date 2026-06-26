import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend, Filler
);

const MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun',
                      'Jul','Aug','Sep','Oct','Nov','Dec'];

const CHART_COLORS = {
  blue:   'rgba(15,76,129,0.85)',
  teal:   'rgba(14,165,233,0.85)',
  amber:  'rgba(245,158,11,0.85)',
  green:  'rgba(16,185,129,0.85)',
  purple: 'rgba(139,92,246,0.85)',
  red:    'rgba(239,68,68,0.85)',
};

const baseOptions = (title) => ({
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    title:  { display: false },
    tooltip: {
      backgroundColor: '#1e293b',
      titleColor: '#f1f5f9',
      bodyColor: '#cbd5e1',
      padding: 10,
      cornerRadius: 8,
    }
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 11 } } },
    y: { grid: { color: '#f1f5f9' }, ticks: { color: '#64748b', font: { size: 11 } } }
  }
});

function GraphDashboard({ apiBase }) {
  const [stats, setStats]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${apiBase}/stats`);
      setStats(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  if (loading) {
    return (
      <div className="loading-overlay" role="status" aria-live="polite">
        <div className="spinner" style={{ borderColor: 'rgba(15,76,129,0.2)', borderTopColor: '#0f4c81' }} />
        Loading analytics data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-banner" role="alert">
        ⚠️ {error}
        <button
          onClick={fetchStats}
          style={{ marginLeft: 'auto', cursor: 'pointer', background: 'none',
                   border: '1px solid #fca5a5', borderRadius: '6px',
                   padding: '4px 12px', color: '#dc2626', fontSize: '0.82rem' }}
        >
          Retry
        </button>
      </div>
    );
  }

  // ── Prepare Chart Data ─────────────────────────────────────────────────────
  const hourlyLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
  const hourlyValues = hourlyLabels.map((_, i) => stats.hourly_avg[String(i)] || 0);

  const monthlyLabels = MONTH_LABELS;
  const monthlyValues = Array.from({ length: 12 }, (_, i) =>
    stats.monthly_avg[String(i + 1)] || 0
  );

  const stationKeys   = Object.keys(stats.station_total).slice(0, 15);
  const stationValues = stationKeys.map(k => stats.station_total[k]);

  // Average rentals summary (weekday vs weekend approx from hourly)
  const peakHour   = hourlyValues.indexOf(Math.max(...hourlyValues));
  const morningSum = hourlyValues.slice(6, 10).reduce((a, b) => a + b, 0);
  const eveningSum = hourlyValues.slice(16, 20).reduce((a, b) => a + b, 0);
  const nightSum   = hourlyValues.slice(0, 6).reduce((a, b) => a + b, 0);
  const afternoonSum = hourlyValues.slice(10, 16).reduce((a, b) => a + b, 0);

  // ── Chart Datasets ─────────────────────────────────────────────────────────
  const hourlyChartData = {
    labels: hourlyLabels,
    datasets: [{
      data:            hourlyValues,
      backgroundColor: hourlyValues.map((v, i) =>
        i === peakHour ? CHART_COLORS.amber : CHART_COLORS.blue
      ),
      borderRadius: 5,
      borderSkipped: false,
    }]
  };

  const monthlyChartData = {
    labels: monthlyLabels,
    datasets: [{
      data:            monthlyValues,
      borderColor:     '#0f4c81',
      backgroundColor: 'rgba(15,76,129,0.12)',
      borderWidth:     2.5,
      pointBackgroundColor: '#0f4c81',
      pointRadius:     5,
      tension:         0.4,
      fill:            true,
    }]
  };

  const stationChartData = {
    labels: stationKeys.map(k => `Station ${k}`),
    datasets: [{
      data:            stationValues,
      backgroundColor: Object.values(CHART_COLORS),
      borderColor:     '#fff',
      borderWidth:     2,
    }]
  };

  const timePeriodData = {
    labels: ['Night (0–5)', 'Morning (6–9)', 'Afternoon (10–15)', 'Evening (16–19)'],
    datasets: [{
      data:            [nightSum, morningSum, afternoonSum, eveningSum],
      backgroundColor: [CHART_COLORS.purple, CHART_COLORS.teal,
                        CHART_COLORS.amber, CHART_COLORS.green],
      borderColor:     '#fff',
      borderWidth:     3,
    }]
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: 'right',
        labels: { color: '#64748b', font: { size: 11 }, padding: 12 }
      },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        padding: 10,
        cornerRadius: 8,
      }
    }
  };

  return (
    <div>
      <div className="dashboard-header">
        <h2>📊 Analytics Dashboard</h2>
        <p>Aggregated insights from 15,000 bike rental records</p>
      </div>

      {/* KPI Summary Row */}
      <div className="result-grid" style={{ marginBottom: '1.5rem' }}>
        {[
          { icon: '⏰', label: 'Peak Hour', value: `${peakHour}:00`, sub: `${hourlyValues[peakHour].toFixed(1)} avg rentals`, cls: 'demand' },
          { icon: '📅', label: 'Best Month', value: MONTH_LABELS[monthlyValues.indexOf(Math.max(...monthlyValues))],
            sub: `${Math.max(...monthlyValues).toFixed(1)} avg rentals`, cls: 'price' },
          { icon: '🚉', label: 'Top Station', value: `#${stationKeys[stationValues.indexOf(Math.max(...stationValues))]}`,
            sub: `${Math.max(...stationValues).toLocaleString()} total rentals`, cls: 'weather' },
          { icon: '📈', label: 'Avg Hourly', value: (hourlyValues.reduce((a,b)=>a+b,0)/24).toFixed(1),
            sub: 'rentals per hour', cls: 'ops' },
        ].map((kpi, i) => (
          <div key={i} className={`result-card ${kpi.cls}`}>
            <span className="icon" aria-hidden="true">{kpi.icon}</span>
            <div className="label">{kpi.label}</div>
            <div className="value" style={{ fontSize: '1.6rem' }}>{kpi.value}</div>
            <div className="sub">{kpi.sub}</div>
          </div>
        ))}
      </div>

      <div className="charts-grid">

        {/* Peak Hours Bar Chart */}
        <div className="chart-card">
          <h3>⏰ Average Rentals by Hour</h3>
          <Bar data={hourlyChartData} options={baseOptions('Hourly Average')} />
        </div>

        {/* Monthly Demand Line Chart */}
        <div className="chart-card">
          <h3>📅 Monthly Demand Trend</h3>
          <Line data={monthlyChartData} options={baseOptions('Monthly Demand')} />
        </div>

        {/* Station-wise Demand Bar Chart */}
        <div className="chart-card">
          <h3>🚉 Station-wise Total Rentals (Top 15)</h3>
          <Bar
            data={stationChartData}
            options={{
              ...baseOptions('Station'),
              indexAxis: 'y',
              plugins: { ...baseOptions().plugins, legend: { display: false } }
            }}
          />
        </div>

        {/* Time Period Doughnut */}
        <div className="chart-card">
          <h3>🕐 Rentals by Time of Day</h3>
          <Doughnut data={timePeriodData} options={doughnutOptions} />
        </div>

      </div>
    </div>
  );
}

export default GraphDashboard;
