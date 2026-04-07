import React from 'react';
import { SelectedNode } from '../types';

interface CompanyPanelProps {
  selectedNode: SelectedNode | null;
}

const CompanyPanel: React.FC<CompanyPanelProps> = ({ selectedNode }) => {
  if (!selectedNode) {
    return (
      <div className="w-full h-full bg-white border-l border-gray-200 p-6">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-gray-400 mb-2">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-gray-500">请选择一个节点查看详情</p>
          </div>
        </div>
      </div>
    );
  }

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'company':
        return '🏢';
      case 'tech':
        return '💻';
      case 'person':
        return '👤';
      default:
        return '📄';
    }
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'company':
        return 'text-blue-600';
      case 'tech':
        return 'text-green-600';
      case 'person':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="w-full h-full bg-white border-l border-gray-200 p-6 overflow-y-auto">
      <div className="mb-6">
        <div className="flex items-center mb-4">
          <span className="text-3xl mr-3">{getNodeIcon(selectedNode.type)}</span>
          <h2 className="text-2xl font-bold text-gray-800">{selectedNode.label}</h2>
        </div>
        
        <div className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700">
          {selectedNode.type === 'company' && '公司'}
          {selectedNode.type === 'tech' && '技术'}
          {selectedNode.type === 'person' && '人物'}
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">基本信息</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-600 mb-2">
              <span className="font-medium">名称：</span>
              <span className="text-gray-800">{selectedNode.data.name}</span>
            </p>
            {selectedNode.data.description && (
              <p className="text-gray-600">
                <span className="font-medium">描述：</span>
                <span className="text-gray-800">{selectedNode.data.description}</span>
              </p>
            )}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">关联实体</h3>
          <div className="space-y-2">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="flex items-center">
                <span className="text-blue-600 mr-2">🔗</span>
                <span className="text-sm text-gray-600">关联节点</span>
              </div>
              <p className="text-sm text-gray-500 mt-1">点击图谱中的节点查看关联关系</p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">详细信息</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">
              此节点代表 {selectedNode.type === 'company' ? '一家AI公司' : 
                       selectedNode.type === 'tech' ? '一项技术栈' : 
                       '一位关键人物'}，在知识图谱中与其他实体存在关联。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyPanel;