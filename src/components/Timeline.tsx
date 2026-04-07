import React from 'react';

interface TimelineProps {
  events: any[];
}

interface TimelineEvent {
  id: string;
  date: string;
  title: string;
  description: string;
  type: 'milestone' | 'achievement' | 'challenge';
}

const Timeline: React.FC<TimelineProps> = ({ events }) => {
  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'milestone':
        return 'bg-blue-500';
      case 'achievement':
        return 'bg-green-500';
      case 'challenge':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getEventTypeIcon = (type: string) => {
    switch (type) {
      case 'milestone':
        return '🏆';
      case 'achievement':
        return '✅';
      case 'challenge':
        return '⚠️';
      default:
        return '📅';
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-6">公司发展时间线</h2>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300"></div>
        
        {/* Timeline events */}
        <div className="space-y-8">
          {events.map((event: TimelineEvent, index: number) => (
            <div key={event.id} className="relative flex items-start">
              {/* Timeline dot */}
              <div className="absolute left-6 w-4 h-4 bg-white border-4 border-gray-300 rounded-full z-10"></div>
              
              {/* Event content */}
              <div className="ml-16 flex-1">
                <div className="flex items-center mb-2">
                  <span className="text-lg mr-2">{getEventTypeIcon(event.type)}</span>
                  <h3 className="text-lg font-semibold text-gray-800">{event.title}</h3>
                  <span className="ml-4 text-sm text-gray-500">{event.date}</span>
                </div>
                <p className="text-gray-600">{event.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Timeline;