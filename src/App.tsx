import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import GraphCanvas from './components/GraphCanvas';
import CompanyPanel from './components/CompanyPanel';
import Timeline from './components/Timeline';
import { mockGraphData, mockCompanies, mockTimelineEvents } from './data/mockData';
import { Company, TimelineEvent } from './types';

function App() {
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    // 这里可以添加实际的搜索逻辑
    console.log('Searching for:', query);
  };

  const handleCompanySelect = (companyId: string) => {
    const company = mockCompanies.find(c => c.id === companyId);
    setSelectedCompany(company || null);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <SearchBar onSearch={handleSearch} />
      
      <div className="flex flex-col lg:flex-row">
        {/* 左侧：知识图谱 */}
        <div className="w-full lg:w-2/3 p-4">
          <div className="bg-white rounded-lg shadow-lg h-96">
            <GraphCanvas data={mockGraphData} />
          </div>
        </div>
        
        {/* 右侧：公司详情和时间线 */}
        <div className="w-full lg:w-1/3 p-4 space-y-4">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <CompanyPanel 
              company={selectedCompany} 
              onSelectCompany={handleCompanySelect}
            />
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-4">
            <Timeline events={mockTimelineEvents} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;