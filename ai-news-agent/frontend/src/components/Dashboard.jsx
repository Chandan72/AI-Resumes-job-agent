import React, { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const cardStyle = {
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '12px',
  background: '#fff',
  boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
};

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [indRes, tsRes] = await Promise.all([
        fetch(`${API_BASE}/industries`),
        fetch(`${API_BASE}/last_updated`)
      ]);
      const indJson = await indRes.json();
      const tsJson = await tsRes.json();
      setData(indJson.industries || []);
      setLastUpdated(tsJson.last_updated || null);
    } catch (e) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 5 * 60 * 1000); // auto-refresh 5 minutes
    return () => clearInterval(id);
  }, []);

  const triggerRun = async () => {
    try {
      await fetch(`${API_BASE}/trigger`, { method: 'POST' });
      await fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: 16, background: '#f9fafb', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0 }}>AI News Curation Dashboard</h2>
          <div style={{ color: '#6b7280', fontSize: 14 }}>Last updated: {lastUpdated ? new Date(lastUpdated).toLocaleString() : 'N/A'}</div>
        </div>
        <button onClick={triggerRun} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #e5e7eb', background: '#111827', color: '#fff' }}>Manual Trigger</button>
      </div>

      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
        {data.map((item) => (
          <div key={item.industry} style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: 16 }}>{item.industry}</h3>
              <span style={{ background: '#eef2ff', color: '#3730a3', borderRadius: 999, padding: '2px 8px', fontSize: 12 }}>{item.count}</span>
            </div>
            <ul style={{ marginTop: 8, paddingLeft: 18 }}>
              {(item.articles || []).slice(0, 5).map((a) => (
                <li key={a.url} style={{ marginBottom: 6 }}>
                  <a href={a.url} target="_blank" rel="noreferrer" style={{ color: '#2563eb', textDecoration: 'none' }}>
                    {a.title}
                  </a>
                  {a.source && <span style={{ color: '#6b7280', marginLeft: 6, fontSize: 12 }}>({a.source})</span>}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}