import React from 'react';

const LeadDetail = ({ lead }) => {
  if (!lead) return null;

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', marginTop: '20px' }}>
      <h3>{lead.name}</h3>
      <p><strong>Address:</strong> {lead.address}</p>
      <p><strong>Phone:</strong> {lead.phone}</p>
      <p><strong>Category:</strong> {lead.category}</p>
      <p><strong>Rating:</strong> {lead.rating} ({lead.reviews} reviews)</p>
      <p><strong>Website:</strong> {lead.website || 'No website'}</p>
      <p><strong>Closing Chance Score:</strong> {lead.closing_chance}%</p>
    </div>
  );
};

export default LeadDetail;
