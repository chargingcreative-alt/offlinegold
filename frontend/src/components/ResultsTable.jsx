import React, { useState, useMemo } from 'react';

const ResultsTable = ({ leads }) => {
  const [filterNoWebsite, setFilterNoWebsite] = useState(false);
  const [sortConfig, setSortConfig] = useState({ key: 'closing_chance', direction: 'desc' });

  const sortedAndFilteredLeads = useMemo(() => {
    let result = [...leads];
    
    if (filterNoWebsite) {
      result = result.filter(lead => !lead.website);
    }
    
    result.sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];
      
      if (aValue === null || aValue === undefined) aValue = sortConfig.direction === 'asc' ? Infinity : -1;
      if (bValue === null || bValue === undefined) bValue = sortConfig.direction === 'asc' ? Infinity : -1;

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
    
    return result;
  }, [leads, filterNoWebsite, sortConfig]);

  const requestSort = (key) => {
    let direction = 'desc';
    if (sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    setSortConfig({ key, direction });
  };

  const getScoreColor = (score) => {
    if (score >= 70) return '#d93025'; // Red
    if (score >= 40) return '#f29900'; // Orange
    return '#188038'; // Green
  };

  if (!leads || leads.length === 0) {
    return <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>No leads found. Start a search above!</div>;
  }

  return (
    <div style={{ marginTop: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px', alignItems: 'center' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '14px' }}>
          <input 
            type="checkbox" 
            checked={filterNoWebsite} 
            onChange={(e) => setFilterNoWebsite(e.target.checked)} 
          />
          Show only businesses without website
        </label>
        <span style={{ fontSize: '14px', color: '#666' }}>
          Showing {sortedAndFilteredLeads.length} of {leads.length} leads
        </span>
      </div>

      <div style={{ overflowX: 'auto', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderRadius: '8px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#fff' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #eee' }}>
              <th onClick={() => requestSort('closing_chance')} style={headerStyle}>
                Score {sortConfig.key === 'closing_chance' ? (sortConfig.direction === 'desc' ? '▼' : '▲') : ''}
              </th>
              <th style={headerStyle}>Business Name</th>
              <th style={headerStyle}>Category</th>
              <th onClick={() => requestSort('rating')} style={headerStyle}>
                Rating {sortConfig.key === 'rating' ? (sortConfig.direction === 'desc' ? '▼' : '▲') : ''}
              </th>
              <th onClick={() => requestSort('reviews')} style={headerStyle}>
                Reviews {sortConfig.key === 'reviews' ? (sortConfig.direction === 'desc' ? '▼' : '▲') : ''}
              </th>
              <th style={headerStyle}>Website</th>
              <th style={headerStyle}>Phone</th>
              <th style={headerStyle}>Address</th>
            </tr>
          </thead>
          <tbody>
            {sortedAndFilteredLeads.map((lead) => (
              <tr key={lead.id} style={{ borderBottom: '1px solid #eee' }} className="table-row">
                <td style={{ padding: '12px 15px' }}>
                  <div style={{ 
                    backgroundColor: getScoreColor(lead.closing_chance), 
                    color: '#fff', 
                    padding: '4px 8px', 
                    borderRadius: '12px', 
                    fontSize: '12px',
                    fontWeight: 'bold',
                    display: 'inline-block',
                    minWidth: '40px',
                    textAlign: 'center'
                  }}>
                    {lead.closing_chance}%
                  </div>
                </td>
                <td style={{ padding: '12px 15px', fontWeight: '500' }}>{lead.name}</td>
                <td style={{ padding: '12px 15px', color: '#666', fontSize: '13px' }}>{lead.category}</td>
                <td style={{ padding: '12px 15px' }}>{lead.rating || 'N/A'}</td>
                <td style={{ padding: '12px 15px' }}>{lead.reviews}</td>
                <td style={{ padding: '12px 15px' }}>
                  {lead.website ? (
                    <a href={lead.website} target="_blank" rel="noopener noreferrer" style={{ color: '#1a73e8', textDecoration: 'none' }}>✓ Visit</a>
                  ) : (
                    <span style={{ color: '#d93025', fontWeight: 'bold' }}>✗ None</span>
                  )}
                </td>
                <td style={{ padding: '12px 15px', fontSize: '13px' }}>{lead.phone}</td>
                <td style={{ padding: '12px 15px', fontSize: '13px', color: '#666' }}>{lead.address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <style>{`
        .table-row:hover {
          background-color: #f1f3f4;
        }
      `}</style>
    </div>
  );
};

const headerStyle = {
  padding: '12px 15px',
  textAlign: 'left',
  fontSize: '13px',
  fontWeight: '600',
  color: '#5f6368',
  cursor: 'pointer',
  userSelect: 'none'
};

export default ResultsTable;
