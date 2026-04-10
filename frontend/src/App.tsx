import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import GraphCanvas from './components/GraphCanvas';
import CompanyPanel from './components/CompanyPanel';
import { queryGraph } from './api';
import type { GraphNode, GraphEdge, SelectedNode } from './types';
import { mockNodes, mockEdges } from './data/mockData';

function App() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useMockData, setUseMockData] = useState(false);

  const handleNodeClick = (node: SelectedNode) => {
    setSelectedNode(node);
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setSearchQuery(query);
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await queryGraph(query);
      setNodes(response.nodes);
      setEdges(response.edges);
      setUseMockData(false);
    } catch (err) {
      setError('获取数据失败，请重试');
      console.error('Search error:', err);
      // 使用 mock 数据作为 fallback
      setNodes(mockNodes);
      setEdges(mockEdges);
      setUseMockData(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // 初始加载一些示例数据
    const loadInitialData = async () => {
      setIsLoading(true);
      try {
        const response = await queryGraph('AI公司');
        setNodes(response.nodes);
        setEdges(response.edges);
        setUseMockData(false);
      } catch (err) {
        console.error('Initial load error:', err);
        // 如果初始加载失败，可以使用 mock 数据作为后备
        setNodes(mockNodes);
        setEdges(mockEdges);
        setUseMockData(true);
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-lg text-gray-600">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <SearchBar onSearch={handleSearch} isLoading={isLoading} />
      
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