import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import 'cytoscape-edgehandles/cytoscape-edgehandles';
import 'cytoscape-panzoom/cytoscape.panzoom';
import 'cytoscape-select/cytoscape.select';
import 'cytoscape-context-menus/cytoscape-context-menus';

interface GraphCanvasProps {
  data: any;
}

const GraphCanvas: React.FC<GraphCanvasProps> = ({ data }) => {
  const cyRef = useRef<cytoscape.Core | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize Cytoscape
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: data,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#4299e1',
            'label': 'data(name)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#ffffff',
            'font-size': '12px',
            'width': '60px',
            'height': '60px',
            'shape': 'round-rectangle',
            'border-width': '2px',
            'border-color': '#2b6cb0',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'background-color': '#f6ad55',
            'border-color': '#dd6b20',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#718096',
            'target-arrow-color': '#718096',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#f6ad55',
            'target-arrow-color': '#f6ad55',
          },
        },
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
        nodeDimensionsIncludeLabels: false,
        edgeElasticity: 100,
        nodeRepulsion: 400000,
      },
    });

    // Add panzoom and select extensions
    cyRef.current.panzoom({
      fit: true,
      zoomOnly: false,
    });

    cyRef.current.select();

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [data]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full bg-gray-50 rounded-lg border border-gray-200"
    />
  );
};

export default GraphCanvas;