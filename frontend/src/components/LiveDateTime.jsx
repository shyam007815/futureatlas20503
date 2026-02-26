import React, { useState, useEffect } from 'react';

const LiveDateTime = () => {
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDate(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="group flex items-center gap-4 bg-slate-900/90 backdrop-blur-xl border border-white/10 px-6 py-3 rounded-2xl shadow-2xl transition-all duration-300 hover:border-white/20 hover:shadow-cyan-900/20">
      {/* Pulsing Live Indicator */}
      <div className="relative flex h-3 w-3">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
        <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.6)]"></span>
      </div>

      <div className="flex flex-col">
        <span className="text-[10px] uppercase tracking-[0.25em] text-cyan-200/60 font-bold mb-1 transition-colors group-hover:text-cyan-200/80">
          Live System Time
        </span>
        <div className="flex items-baseline gap-2.5">
          <span className="text-2xl font-bold text-white tracking-tight tabular-nums leading-none drop-shadow-sm font-sans">
            {formatTime(currentDate)}
          </span>
          <span className="text-xs font-medium text-slate-400 border-l border-white/10 pl-2.5 leading-none h-3 flex items-center">
            {formatDate(currentDate)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default LiveDateTime;
