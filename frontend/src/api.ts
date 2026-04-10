const API_BASE = '/api';

export interface QueryResponse {
  nodes: any[];
  edges: any[];
}

export const queryGraph = async (q: string, top_k: number = 5): Promise<QueryResponse> => {
  const res = await fetch(`${API_BASE}/v1/analyze/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: q, top_k })  // 注意：参数名改为 query
  });
  if (!res.ok) throw new Error('API error');
  return res.json();
};

export const queryKnowledge = async (q: string, top_k: number = 5): Promise<QueryResponse> => {
  const res = await fetch(`${API_BASE}/v1/analyze/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: q, top_k })
  });
  if (!res.ok) throw new Error('API error');
  return res.json();
};

export const querySearch = async (q: string, top_k: number = 5): Promise<QueryResponse> => {
  const res = await fetch(`${API_BASE}/v1/analyze/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: q, top_k })
  });
  if (!res.ok) throw new Error('API error');
  return res.json();
};