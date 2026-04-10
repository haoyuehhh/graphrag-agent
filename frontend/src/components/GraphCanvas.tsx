import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import type { GraphNode, GraphEdge, SelectedNode } from '../types';

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick: (node: SelectedNode) => void;
}

const GraphCanvas: React.FC<GraphCanvasProps> = ({ nodes, edges, onNodeClick }) => {
  const cyRef = useRef<cytoscape.Core | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const isInitialized = useRef(false);

  // 只初始化一次
  useEffect(() => {
    if (!containerRef.current || isInitialized.current) return;
    isInitialized.current = true;

    try {
      cyRef.current = cytoscape({
        container: containerRef.current,
        elements: [],
        style: [
          {
            selector: 'node',
            style: {
              'background-color': '#fff',
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'color': '#333',
              'font-size': '12px',
              'width': '60px',
              'height': '60px',
              'shape': 'ellipse',
              'border-width': '2px',
              'border-color': '#666',
              'text-wrap': 'wrap',
              'text-max-width': '50px'
            }
          },
          {
            selector: 'node[type="company"]',
            style: {
              'background-color': '#3b82f6',
              'shape': 'ellipse',
              'width': '80px',
              'height': '80px',
              'font-size': '14px',
              'font-weight': 'bold',
              'color': 'white',
              'border-color': '#1e40af'
            }
          },
          {
            selector: 'node[type="tech"]',
            style: {
              'background-color': '#10b981',
              'shape': 'rectangle',
              'width': '70px',
              'height': '70px',
              'font-size': '12px',
              'color': 'white',
              'border-color': '#059669'
            }
          },
          {
            selector: 'node[type="person"]',
            style: {
              'background-color': '#f97316',
              'shape': 'diamond',
              'width': '60px',
              'height': '60px',
              'font-size': '12px',
              'color': 'white',
              'border-color': '#ea580c'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': '2px',
              'line-color': '#999',
              'target-arrow-color': '#999',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'label': 'data(relationship)',
              'font-size': '10px',
              'text-rotation': 'autorotate',
              'text-margin-y': -10
            }
          },
          {
            selector: 'edge[type="invest"]',
            style: {
              'line-color': '#3b82f6',
              'width': '3px',
              'font-weight': 'bold'
            }
          },
          {
            selector: 'edge[type="tech_dep"]',
            style: {
              'line-color': '#10b981',
              'width': '2px',
              'line-style': 'dashed'
            }
          },
          {
            selector: 'edge[type="person_flow"]',
            style: {
              'line-color': '#f97316',
              'width': '2px',
              'target-arrow-shape': 'triangle',
              'target-arrow-color': '#f97316'
            }
          }
        ]
      });

      cyRef.current.on('tap', 'node', (evt) => {
        const nodeData = evt.target.data();
        if (!nodeData?.id) return;
        
        onNodeClick({
          id: nodeData.id,
          label: nodeData.label || '',
          type: nodeData.type || 'company',
          data: {
            name: nodeData.name || '',
            description: nodeData.description || ''
          }
        });
      });

    } catch (e) {
      console.error('Cytoscape init error:', e);
    }

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
        isInitialized.current = false;
      }
    };
  }, []); // 空依赖，只运行一次

  // 数据更新
  useEffect(() => {
    if (!cyRef.current || !nodes?.length) return;

    const cy = cyRef.current;
    
    try {
      cy.batch(() => {
        cy.elements().remove();
        
        nodes.forEach(node => {
          cy.add({
            group: 'nodes',
            data: { 
              id: node.id, 
              label: node.label || '',
              type: node.type || 'unknown',
              ...node.data 
            }
          });
        });

        edges.forEach(edge => {
          cy.add({
            group: 'edges',
            data: { 
              id: edge.id, 
              source: edge.source, 
              target: edge.target,
              type: edge.type || '',
              relationship: edge.type || '关联'
            }
          });
        });
      });

      // 方案1：延迟布局，确保 DOM 就绪，使用 cyRef.current
      setTimeout(() => {
        if (!cyRef.current) return;  // 提前检查
        
        cyRef.current.layout({       // 用 cyRef.current 而不是 cy
          name: 'cose',
          idealEdgeLength: 100,
          nodeOverlap: 20,
          refresh: 20,
          fit: true,
          padding: 30,
          randomize: false,
          componentSpacing: 100,
          nodeRepulsion: 400000,
          edgeElasticity: 100,
          nestingFactor: 5,
          gravity: 80,
          numIter: 1000,
          initialTemp: 200,
          coolingFactor: 0.95,
          minTemp: 1.0,
          animate: false
        }).run();
      }, 0);

    } catch (e) {
      console.error('Update error:', e);
    }
  }, [nodes, edges]);

  return (
    <div 
      ref={containerRef} 
      className="w-full h-full bg-gray-50 border border-gray-200 rounded-lg"
      style={{ minHeight: '600px' }}
    />
  );
};

export default GraphCanvas;