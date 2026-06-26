import React, { useState } from 'react';

const DEFAULTS = {
  temperature:    25,
  humidity:       60,
  hour:           8,
  weekday:        1,
  holiday:        0,
  month:          6,
  windspeed:      10,
  rainfall:       0,
  available_bikes: 20,
  event_type:     'None',
};

const FIELDS = [
  {
    key: 'temperature', label: 'Temperature (°C)',
    type: 'number', min: -10, max: 50, step: 0.1,
    icon: '🌡️', hint: '-10 to 50'
  },
  {
    key: 'humidity', label: 'Humidity (%)',
    type: 'number', min: 0, max: 100, step: 1,
    icon: '💧', hint: '0 to 100'
  },
  {
    key: 'hour', label: 'Hour of Day',
    type: 'number', min: 0, max: 23, step: 1,
    icon: '🕐', hint: '0 to 23'
  },
  {
    key: 'weekday', label: 'Weekday',
    type: 'select',
    icon: '📅',
    options: [
      { value: 0, label: 'Monday' },
      { value: 1, label: 'Tuesday' },
      { value: 2, label: 'Wednesday' },
      { value: 3, label: 'Thursday' },
      { value: 4, label: 'Friday' },
      { value: 5, label: 'Saturday' },
      { value: 6, label: 'Sunday' },
    ]
  },
  {
    key: 'holiday', label: 'Holiday',
    type: 'select',
    icon: '🎉',
    options: [
      { value: 0, label: 'No' },
      { value: 1, label: 'Yes' },
    ]
  },
  {
    key: 'month', label: 'Month',
    type: 'select',
    icon: '📆',
    options: [
      { value: 1,  label: 'January' },
      { value: 2,  label: 'February' },
      { value: 3,  label: 'March' },
      { value: 4,  label: 'April' },
      { value: 5,  label: 'May' },
      { value: 6,  label: 'June' },
      { value: 7,  label: 'July' },
      { value: 8,  label: 'August' },
      { value: 9,  label: 'September' },
      { value: 10, label: 'October' },
      { value: 11, label: 'November' },
      { value: 12, label: 'December' },
    ]
  },
  {
    key: 'windspeed', label: 'Wind Speed (km/h)',
    type: 'number', min: 0, max: 100, step: 0.1,
    icon: '💨', hint: '0 to 100'
  },
  {
    key: 'rainfall', label: 'Rainfall (mm)',
    type: 'number', min: 0, max: 200, step: 0.1,
    icon: '🌧️', hint: '0 to 200'
  },
  {
    key: 'available_bikes', label: 'Available Bikes',
    type: 'number', min: 0, max: 200, step: 1,
    icon: '🚲', hint: '0 to 200'
  },
  {
    key: 'event_type', label: 'Event Type',
    type: 'select',
    icon: '🎪',
    options: [
      { value: 'None',     label: 'No Event' },
      { value: 'Festival', label: 'Festival' },
      { value: 'Concert',  label: 'Concert' },
      { value: 'Sports',   label: 'Sports Event' },
    ]
  },
];

function PredictionForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULTS);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (form.temperature < -10 || form.temperature > 50)
      errs.temperature = 'Must be between -10 and 50';
    if (form.humidity < 0 || form.humidity > 100)
      errs.humidity = 'Must be between 0 and 100';
    if (form.hour < 0 || form.hour > 23)
      errs.hour = 'Must be between 0 and 23';
    if (form.rainfall < 0)
      errs.rainfall = 'Cannot be negative';
    if (form.available_bikes < 0)
      errs.available_bikes = 'Cannot be negative';
    return errs;
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : (name === 'event_type' ? value : parseInt(value, 10))
    }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: undefined }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    onSubmit(form);
  };

  const handleReset = () => {
    setForm(DEFAULTS);
    setErrors({});
  };

  return (
    <div className="card">
      <h2 className="card-title">
        🎯 Predict Bike Rental Demand
      </h2>
      <form onSubmit={handleSubmit} noValidate aria-label="Prediction form">
        <div className="form-grid">
          {FIELDS.map(field => (
            <div className="form-group" key={field.key}>
              <label htmlFor={field.key}>
                {field.icon} {field.label}
              </label>
              {field.type === 'select' ? (
                <select
                  id={field.key}
                  name={field.key}
                  value={form[field.key]}
                  onChange={handleChange}
                  aria-invalid={!!errors[field.key]}
                >
                  {field.options.map(opt => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  id={field.key}
                  type="number"
                  name={field.key}
                  value={form[field.key]}
                  onChange={handleChange}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  placeholder={field.hint}
                  aria-invalid={!!errors[field.key]}
                  aria-describedby={errors[field.key] ? `${field.key}-err` : undefined}
                />
              )}
              {errors[field.key] && (
                <span
                  id={`${field.key}-err`}
                  style={{ color: '#dc2626', fontSize: '0.78rem' }}
                  role="alert"
                >
                  {errors[field.key]}
                </span>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '1.25rem' }}>
          <button
            type="submit"
            className="predict-btn"
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                Predicting...
              </>
            ) : (
              '🔮 Predict Demand'
            )}
          </button>
          <button
            type="button"
            onClick={handleReset}
            style={{
              padding: '14px 22px',
              background: 'none',
              border: '1.5px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              fontSize: '0.9rem',
              color: 'var(--text-muted)',
              fontFamily: 'inherit'
            }}
          >
            ↺ Reset
          </button>
        </div>
      </form>
    </div>
  );
}

export default PredictionForm;
