import React from 'react';

function getDemandBadge(demand) {
  if (demand > 100) return { cls: 'badge-red',    label: 'Very High' };
  if (demand > 70)  return { cls: 'badge-amber',  label: 'High' };
  if (demand > 40)  return { cls: 'badge-blue',   label: 'Moderate' };
  return              { cls: 'badge-green',  label: 'Low' };
}

function getPriceBadge(tier) {
  const map = {
    Premium:    'badge-red',
    'Standard+': 'badge-amber',
    Standard:   'badge-blue',
    Discounted: 'badge-green',
  };
  return map[tier] || 'badge-blue';
}

function ResultCards({ result }) {
  const demandBadge = getDemandBadge(result.predicted_demand);
  const priceBadge  = getPriceBadge(result.price_tier);

  return (
    <section aria-label="Prediction Results">
      <h2 className="card-title" style={{ marginBottom: '1rem' }}>
        ✅ Prediction Results
      </h2>
      <div className="result-grid">

        {/* Predicted Demand */}
        <div className="result-card demand" role="region" aria-label="Demand prediction">
          <span className="icon" aria-hidden="true">📊</span>
          <div className="label">Predicted Demand</div>
          <div className="value">{result.predicted_demand}</div>
          <div className="sub">rentals expected</div>
          <span className={`badge ${demandBadge.cls}`}>{demandBadge.label}</span>
        </div>

        {/* Suggested Price */}
        <div className="result-card price" role="region" aria-label="Suggested price">
          <span className="icon" aria-hidden="true">💰</span>
          <div className="label">Suggested Price</div>
          <div className="value">₹{result.price}</div>
          <div className="sub">Base price: ₹{result.base_price}</div>
          <span className={`badge ${priceBadge}`}>{result.price_tier}</span>
          {result.price_adjustments && (
            <ul className="adjustments" aria-label="Price adjustments">
              {result.price_adjustments.map((adj, i) => (
                <li key={i}>{adj}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Weather Recommendation */}
        <div className="result-card weather" role="region" aria-label="Weather recommendation">
          <span className="icon" aria-hidden="true">🌤️</span>
          <div className="label">Weather Insight</div>
          <div className="recommendation-text">{result.recommendation}</div>
        </div>

        {/* Operational Tip */}
        <div className="result-card ops" role="region" aria-label="Operational tip">
          <span className="icon" aria-hidden="true">🚀</span>
          <div className="label">Operational Tip</div>
          <span className={`badge badge-purple`} style={{ marginBottom: '0.5rem' }}>
            {result.demand_category} Demand
          </span>
          <div className="recommendation-text">{result.operational_tip}</div>
        </div>

      </div>
    </section>
  );
}

export default ResultCards;
