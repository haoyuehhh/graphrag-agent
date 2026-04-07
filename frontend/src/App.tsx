import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import GraphCanvas from './components/GraphCanvas';
import CompanyPanel from './components/CompanyPanel';
import { mockNodes, mockEdges } from './data/mockData';
import type { GraphNode, GraphEdge, SelectedNode } from './types';

function App() {
  const [nodes, setNodes] = useState<GraphNode[]>(mockNodes);
  const [edges, setEdges] = useState<GraphEdge[]>(mockEdges);
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleNodeClick = (node: SelectedNode) => {
    setSelectedNode(node);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    // 这里可以实现搜索逻辑
    console.log('搜索:', query);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <SearchBar onSearch={handleSearch} />
      
      <div className="flex h-[calc(100vh-64px)]">
        {/* 左侧图谱区域 - 70% */}
        <div className="w-9/12 bg-gray-50 p-4">
          <div className="h-full bg-white rounded-lg shadow-sm border border-gray-200">
            <GraphCanvas 
              nodes={nodes} 
              edges={edges} 
              onNodeClick={handleNodeClick}
            />
          </div>
        </div>
        
        {/* 右侧面板区域 - 30% */}
        <div className="w-3/12">
          <CompanyPanel selectedNode={selectedNode} />
        </div>
      </div>
    </div>
  );
}

export default App;