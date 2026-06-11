import React, { useEffect } from 'react';
import { useStore } from './store';
import { ViewState } from './types';
import { LucideLayoutDashboard, LucideCalculator, LucideListTodo, LucideSettings, LucideLeaf } from 'lucide-react';
import Dashboard from './components/Dashboard';
import EstimateForm from './components/EstimateForm';
import PicksGrid from './components/PicksGrid';
import SettingsPanel from './components/SettingsPanel';

const App: React.FC = () => {
  const { currentView, setView, settings } = useStore();

  // Initialize dark mode from store on mount (failsafe)
  useEffect(() => {
    if (settings.theme === 'dark') {
      document.documentElement.classList.add('dark');
    }
  }, [settings.theme]);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard': return <Dashboard />;
      case 'estimate': return <EstimateForm />;
      case 'picks': return <PicksGrid />;
      case 'settings': return <SettingsPanel />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-20 lg:w-64 bg-white/60 dark:bg-slate-900/80 backdrop-blur-lg border-r border-white/10 flex flex-col justify-between z-20 transition-all">
        <div className="p-6 flex items-center justify-center lg:justify-start gap-3">
          <div className="bg-emerald-500 p-2 rounded-xl text-white shadow-lg shadow-emerald-500/30">
            <LucideLeaf size={24} />
          </div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white hidden lg:block tracking-tight">CarbonTrace</h1>
        </div>

        <nav className="flex-1 px-3 py-6 space-y-2">
          <NavItem view="dashboard" current={currentView} onClick={setView} icon={<LucideLayoutDashboard />} label="Dashboard" />
          <NavItem view="estimate" current={currentView} onClick={setView} icon={<LucideCalculator />} label="Estimate" />
          <NavItem view="picks" current={currentView} onClick={setView} icon={<LucideListTodo />} label="Action Picks" />
        </nav>

        <div className="p-3 pb-6">
          <NavItem view="settings" current={currentView} onClick={setView} icon={<LucideSettings />} label="Settings" />
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto relative scroll-smooth">
        {/* Background Orbs for Aesthetics */}
        <div className="fixed top-[-20%] right-[-10%] w-[500px] h-[500px] bg-emerald-400/20 rounded-full blur-[120px] pointer-events-none mix-blend-multiply dark:mix-blend-screen" />
        <div className="fixed bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-teal-400/20 rounded-full blur-[120px] pointer-events-none mix-blend-multiply dark:mix-blend-screen" />

        <div className="max-w-7xl mx-auto p-6 lg:p-12 relative z-10">
          {renderView()}
        </div>
      </main>
    </div>
  );
};

const NavItem = ({ view, current, onClick, icon, label }: { view: ViewState, current: ViewState, onClick: (v: ViewState) => void, icon: React.ReactNode, label: string }) => (
  <button
    onClick={() => onClick(view)}
    className={`
      w-full flex items-center gap-4 px-3 py-3 rounded-xl transition-all duration-200 group
      ${current === view 
        ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20' 
        : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}
    `}
  >
    <span className={current === view ? 'text-white' : 'group-hover:scale-110 transition-transform'}>{icon}</span>
    <span className="hidden lg:block font-medium">{label}</span>
  </button>
);

export default App;