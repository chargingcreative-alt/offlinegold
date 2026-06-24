import React, { useState } from 'react';

const SearchForm = ({ onSearch, lastResults }) => {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, max_results: parseInt(maxResults) }),
      });
      const data = await response.json();
      onSearch(data);
    } catch (error) {
      console.error('Error searching:', error);
      alert('Failed to search leads');
    } finally {
      setLoading(false);
    }
  };

  const noWebsiteCount = lastResults ? lastResults.filter(l => !l.website).length : 0;

  return (
    <div className="search-container" style={{ marginBottom: '30px' }}>
      <form onSubmit={handleSubmit} style={{ 
        display: 'flex', 
        flexDirection: 'column',
        gap: '15px', 
        padding: '20px', 
        backgroundColor: '#fff',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        borderRadius: '8px' 
      }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search niche (e.g. dentists in Miami)"
            style={{ flex: 1, padding: '12px', borderRadius: '4px', border: '1px solid #ddd' }}
            disabled={loading}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <label style={{ fontSize: '14px', color: '#666' }}>Limit:</label>
            <input 
              type="number"
              min="1"
              max="50"
              value={maxResults} 
              onChange={(e) => setMaxResults(e.target.value)}
              style={{ width: '60px', padding: '12px', borderRadius: '4px', border: '1px solid #ddd' }}
              disabled={loading}
            />
          </div>
          <button 
            type="submit" 
            disabled={loading} 
            style={{ 
              padding: '12px 24px', 
              backgroundColor: '#1a73e8', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: loading ? 'not-allowed' : 'pointer',
              minWidth: '140px'
            }}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
                <span className="spinner"></span> Scraping...
              </span>
            ) : 'Find Leads'}
          </button>
        </div>
        
        {lastResults && (
          <div style={{ display: 'flex', gap: '15px', fontSize: '14px' }}>
            <span style={{ padding: '4px 10px', backgroundColor: '#e8f0fe', color: '#1967d2', borderRadius: '20px' }}>
              Scraped: <strong>{lastResults.length}</strong>
            </span>
            <span style={{ padding: '4px 10px', backgroundColor: '#fce8e6', color: '#d93025', borderRadius: '20px' }}>
              No Website: <strong>{noWebsiteCount}</strong>
            </span>
          </div>
        )}
      </form>
      
      <style>{`
        .spinner {
          width: 14px;
          height: 14px;
          border: 2px solid #fff;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default SearchForm;
