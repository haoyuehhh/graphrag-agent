export interface GraphNode {
  id: string;
  label: string;
  type: 'company' | 'tech' | 'person';
  data?: {
    name?: string;
    description?: string;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type?: 'invest' | 'tech_dep' | 'person_flow';
  data?: {
    relationship?: string;
    label?: string;
  };
}

export interface SelectedNode {
  id: string;
  label: string;
  type: 'company' | 'tech' | 'person';
  data: {
    name: string;
    description: string;
  };
}