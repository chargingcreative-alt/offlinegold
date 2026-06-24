import React, { useState, useEffect } from 'react';
import SearchForm from './components/SearchForm';
import ResultsTable from './components/ResultsTable';

function App() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, noWebsite: 0, avgScore: 0 });

  useEffect(() => {
    fetchLeads();
  }, []);

  useEffect(() => {
    if (leads.length > 0) {
      const noWebsite = leads.filter(l => !l.website).length;
      const totalScore = leads.reduce((acc, l) => acc + l.closing_chance, 0);
      setStats({
        total: leads.length,
        noWebsite: noWebsite,
        avgScore: Math.round(totalScore / leads.length)
      });
    } else {
      setStats({ total: 0, noWebsite: 0, avgScore: 0 });
    }
  }, [leads]);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/leads');
      const data = await response.json();
      setLeads(data);
    } catch (error) {
      console.error('Error fetching leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (newLeads) => {
    // Backend already saves them, so we just refresh the full list 
    // to include previous searches as well
    fetchLeads();
  };

  const handleExport = () => {
    window.open('/api/leads/export', '_blank');
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
      <header style={{ backgroundColor: '#202124', color: '#fff', padding: '15px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '22px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ color: '#f29900' }}>Offline</span>Gold
        </h1>
        <button 
          onClick={handleExport} 
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#188038', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: 'pointer',
            fontWeight: '500'
          }}
        >
          Export CSV
        </button>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '30px 20px' }}>
        <section>
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ margin: '0 0 5px 0', fontSize: '18px' }}>Lead Discovery</h2>
            <p style={{ margin: 0, color: '#5f6368', fontSize: '14px' }}>Search Google Maps for local businesses without a web presence.</p>
          </div>
          <SearchForm onSearch={handleSearch} lastResults={leads.slice(0, 10)} />
        </section>

        <section style={{ marginTop: '30px' }}>
          <div className="stats-bar" style={{ 
            display: 'flex', 
            gap: '20px', 
            marginBottom: '20px' 
          }}>
            <StatCard label="Total Leads" value={stats.total} />
            <StatCard label="Offline (No Website)" value={`${stats.noWebsite} (${stats.total ? Math.round(stats.noWebsite/stats.total*100) : 0}%)`} />
            <StatCard label="Avg. Closing Chance" value={`${stats.avgScore}%`} color="#f29900" />
          </div>

          <div style={{ backgroundColor: '#fff', borderRadius: '8px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h2 style={{ margin: 0, fontSize: '18px' }}>Recent Opportunities</h2>
              <button onClick={fetchLeads} style={{ background: 'none', border: 'none', color: '#1a73e8', cursor: 'pointer', fontSize: '14px' }}>Refresh List</button>
            </div>
            {loading && leads.length === 0 ? <p>Loading leads...</p> : <ResultsTable leads={leads} />}
          </div>
        </section>
      </main>
    </div>
  );
}

const StatCard = ({ label, value, color = '#1a73e8' }) => (
  <div style={{ 
    flex: 1, 
    backgroundColor: '#fff', 
    padding: '15px 20px', 
    borderRadius: '8px', 
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    borderLeft: `4px solid ${color}`
  }}>
    <div style={{ fontSize: '12px', color: '#5f6368', textTransform: 'uppercase', marginBottom: '5px' }}>{label}</div>
    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#202124' }}>{value}</div>
  </div>
);

export default App;
