import React, { useEffect, useRef, useState } from 'react';
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
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // 初始化Cytoscape
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: {
        nodes: nodes.map(node => ({
          data: { id: node.id, label: node.label, ...node.data }
        })),
        edges: edges.map(edge => ({
          data: { id: edge.id, source: edge.source, target: edge.target, ...edge.data }
        }))
      },
      style: [
        // 节点样式
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
        // 公司节点样式 - 蓝色圆形
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
        // 技术节点样式 - 绿色方形
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
        // 人物节点样式 - 橙色菱形
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
        // 边样式
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
        // 投资关系 - 实线
        {
          selector: 'edge[type="invest"]',
          style: {
            'line-color': '#3b82f6',
            'width': '3px',
            'font-weight': 'bold'
          }
        },
        // 技术依赖 - 虚线
        {
          selector: 'edge[type="tech_dep"]',
          style: {
            'line-color': '#10b981',
            'width': '2px',
            'line-style': 'dashed'
          }
        },
        // 人物流动 - 箭头
        {
          selector: 'edge[type="person_flow"]',
          style: {
            'line-color': '#f97316',
            'width': '2px',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#f97316'
          }
        }
      ],
      layout: {
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
        minTemp: 1.0
      }
    });

    // 添加点击事件
    if (cyRef.current) {
      cyRef.current.on('tap', 'node', function(evt) {
        const node = evt.target;
        const nodeData = node.data();
        setSelectedNode({
          id: nodeData.id,
          label: nodeData.label,
          type: nodeData.type as 'company' | 'tech' | 'person',
          data: {
            name: nodeData.name,
            description: nodeData.description
          }
        });
        if (selectedNode) {
  onNodeClick(selectedNode);
}
      });
    }

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [nodes, edges, onNodeClick]);

  // 当节点数据变化时更新图
  useEffect(() => {
    if (cyRef.current) {
      const cy = cyRef.current;
      
      // 更新节点
      nodes.forEach(node => {
        const cyNode = cy.getElementById(node.id);
        if (cyNode.length > 0) {
          cyNode.data({ ...node.data, label: node.label });
        } else {
          cy.add({
            group: 'nodes',
            data: { id: node.id, label: node.label, ...node.data }
          });
        }
      });

      // 更新边
      edges.forEach(edge => {
        const cyEdge = cy.getElementById(edge.id);
        if (cyEdge.length > 0) {
          cyEdge.data({ ...edge.data, source: edge.source, target: edge.target });
        } else {
          cy.add({
            group: 'edges',
            data: { id: edge.id, source: edge.source, target: edge.target, ...edge.data }
          });
        }
      });

      // 重新布局
      cy.layout({
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
        minTemp: 1.0
      }).run();
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