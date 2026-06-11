import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserSettings, ViewState } from './types';

interface AppState {
  currentView: ViewState;
  setView: (view: ViewState) => void;
  settings: UserSettings;
  updateSettings: (settings: Partial<UserSettings>) => void;
  toggleTheme: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      currentView: 'dashboard',
      setView: (view) => set({ currentView: view }),
      settings: {
        theme: 'light',
        reducedMotion: false,
        animationSpeed: 1,
        units: 'kg',
      },
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),
      toggleTheme: () => {
        const current = get().settings.theme;
        const next = current === 'light' ? 'dark' : 'light';
        set((state) => ({ settings: { ...state.settings, theme: next } }));
        
        // Apply to DOM
        if (next === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },
    }),
    {
      name: 'carbon-trace-storage',
      onRehydrateStorage: () => (state) => {
        // Sync theme on load
        if (state?.settings.theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      }
    }
  )
);