import React from 'react';

interface CompanyPanelProps {
  company: any;
  onSelectCompany: (companyId: string) => void;
}

const CompanyPanel: React.FC<CompanyPanelProps> = ({ company, onSelectCompany }) => {
  if (!company) {
    return (
      <div className="p-6 text-gray-500">
        请选择一个公司查看详细信息
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          {company.name}
        </h2>
        <p className="text-gray-600">
          {company.description}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-sm font-semibold text-blue-800 mb-1">
            成立时间
          </h3>
          <p className="text-lg text-blue-600">
            {company.founded}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-sm font-semibold text-green-800 mb-1">
            员工数量
          </h3>
          <p className="text-lg text-green-600">
            {company.employees}
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-sm font-semibold text-purple-800 mb-1">
            行业
          </h3>
          <p className="text-lg text-purple-600">
            {company.industry}
          </p>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <h3 className="text-sm font-semibold text-orange-800 mb-1">
            估值
          </h3>
          <p className="text-lg text-orange-600">
            ${company.valuation}
          </p>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          主要产品
        </h3>
        <div className="space-y-2">
          {company.products.map((product: any, index: number) => (
            <div key={index} className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <span className="text-gray-700">{product}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          关键人物
        </h3>
        <div className="space-y-2">
          {company.keyPeople.map((person: any, index: number) => (
            <div key={index} className="flex items-center">
              <div className="w-8 h-8 bg-gray-300 rounded-full mr-3 flex items-center justify-center">
                <span className="text-xs font-semibold text-gray-700">
                  {person.name.charAt(0)}
                </span>
              </div>
              <div>
                <p className="text-gray-800 font-medium">{person.name}</p>
                <p className="text-sm text-gray-600">{person.title}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          联系方式
        </h3>
        <div className="space-y-2">
          <div className="flex items-center">
            <span className="text-gray-500 w-20">网站:</span>
            <a href={company.website} className="text-blue-600 hover:underline">
              {company.website}
            </a>
          </div>
          <div className="flex items-center">
            <span className="text-gray-500 w-20">邮箱:</span>
            <span className="text-gray-700">{company.email}</span>
          </div>
          <div className="flex items-center">
            <span className="text-gray-500 w-20">电话:</span>
            <span className="text-gray-700">{company.phone}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyPanel;