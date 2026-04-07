export interface Company {
  id: string;
  name: string;
  description: string;
  founded: string;
  employees: number;
  industry: string;
  valuation: string;
  website: string;
  email: string;
  phone: string;
  products: string[];
  keyPeople: {
    name: string;
    title: string;
  }[];
}

export interface TimelineEvent {
  id: string;
  date: string;
  title: string;
  description: string;
  type: 'milestone' | 'achievement' | 'challenge';
}

export interface GraphNode {
  id: string;
  name: string;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SearchQuery {
  query: string;
}