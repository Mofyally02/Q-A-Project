import { create } from 'zustand';

export interface LiveQuestion {
  id: string;
  subject: string;
  status: 'processing' | 'reviewing' | 'typing' | 'delivered';
  expert?: { name: string; avatar: string };
  timestamp: string;
  preview?: string;
}

export interface RecentAnswer {
  id: string;
  question: string;
  answer: string;
  expert: string;
  rating?: number;
  subject: string;
  timestamp: string;
  image?: string;
}

interface RealTimeStore {
  liveQuestions: LiveQuestion[];
  recentAnswers: RecentAnswer[];
  notifications: number;
  credits: number;
  addLiveQuestion: (q: LiveQuestion) => void;
  updateQuestionStatus: (id: string, updates: Partial<LiveQuestion>) => void;
  addRecentAnswer: (a: RecentAnswer) => void;
  removeLiveQuestion: (id: string) => void;
  incrementNotifications: () => void;
  setCredits: (c: number) => void;
  setNotifications: (n: number) => void;
  clearNotifications: () => void;
}

export const useRealTimeStore = create<RealTimeStore>((set) => ({
  liveQuestions: [],
  recentAnswers: [],
  notifications: 0,
  credits: 12,

  addLiveQuestion: (q) => set((state) => ({
    liveQuestions: [q, ...state.liveQuestions].slice(0, 10)
  })),

  updateQuestionStatus: (id, updates) => set((state) => ({
    liveQuestions: state.liveQuestions.map(q =>
      q.id === id ? { ...q, ...updates } : q
    )
  })),

  addRecentAnswer: (a) => set((state) => ({
    recentAnswers: [a, ...state.recentAnswers].slice(0, 8),
    liveQuestions: state.liveQuestions.filter(q => q.id !== a.id)
  })),

  removeLiveQuestion: (id) => set((state) => ({
    liveQuestions: state.liveQuestions.filter(q => q.id !== id)
  })),

  incrementNotifications: () => set((state) => ({ notifications: state.notifications + 1 })),
  
  setCredits: (c) => set({ credits: c }),
  
  setNotifications: (n) => set({ notifications: n }),
  
  clearNotifications: () => set({ notifications: 0 }),
}));

