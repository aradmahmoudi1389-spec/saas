import { useState } from 'react';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import BrandAudit from './pages/BrandAudit';
import Roadmap from './pages/Roadmap';
import ContentAI from './pages/ContentAI';

type Page = 'dashboard' | 'audit' | 'roadmap' | 'content';

const navItems: { id: Page; icon: string; label: string; sublabel: string }[] = [
  { id: 'dashboard', icon: '⬡', label: 'داشبورد', sublabel: 'نمای کلی' },
  { id: 'audit', icon: '🔍', label: 'Brand Audit', sublabel: 'تحلیل پیج' },
  { id: 'roadmap', icon: '🗺️', label: 'Growth Roadmap', sublabel: 'نقشه راه' },
  { id: 'content', icon: '✍️', label: 'AI Content', sublabel: 'استراتژی محتوا' },
];

function Sidebar({
  currentPage,
  onNavigate,
  onExit,
}: {
  currentPage: Page;
  onNavigate: (p: Page) => void;
  onExit: () => void;
}) {
  return (
    <aside
      className="fixed top-0 right-0 h-full flex flex-col"
      style={{
        width: 240,
        background: 'var(--card)',
        borderLeft: '1px solid var(--border)',
        zIndex: 40,
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5" style={{ borderBottom: '1px solid var(--border)' }}>
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm font-display"
          style={{ background: 'linear-gradient(135deg, #7c3aed, #4f46e5)' }}
        >
          B
        </div>
        <div>
          <div className="font-display font-semibold text-sm" style={{ color: 'var(--foreground)' }}>
            BrandPilot
          </div>
          <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>Pro Plan</div>
        </div>
      </div>

      {/* Account */}
      <div className="px-4 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <div
          className="flex items-center gap-3 p-3 rounded-xl"
          style={{ background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.15)' }}
        >
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-white font-display text-sm"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #4f46e5)' }}
          >
            آ
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-medium truncate" style={{ color: 'var(--foreground)' }}>آرمین حسینی</div>
            <div className="text-xs truncate" style={{ color: 'var(--muted-foreground)' }}>@armin.design</div>
          </div>
          <div
            className="w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{ background: '#4ade80', boxShadow: '0 0 6px rgba(74,222,128,0.6)' }}
          />
        </div>
      </div>

      {/* Brand Score mini */}
      <div className="px-4 py-3" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>Brand Score</span>
          <span className="font-mono text-sm font-bold gradient-text">72</span>
        </div>
        <div className="h-1.5 rounded-full" style={{ background: 'var(--secondary)' }}>
          <div
            className="h-1.5 rounded-full"
            style={{ width: '72%', background: 'linear-gradient(90deg, #7c3aed, #4f46e5)' }}
          />
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <div className="text-xs font-semibold px-2 mb-2 uppercase tracking-wide" style={{ color: 'var(--muted-foreground)' }}>
          منو اصلی
        </div>
        {navItems.map(item => (
          <button
            key={item.id}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl mb-1 text-right transition-all"
            style={
              currentPage === item.id
                ? { background: 'rgba(124,58,237,0.12)', borderRight: '2px solid #7c3aed', color: '#c4b5fd' }
                : { color: 'var(--secondary-foreground)', borderRight: '2px solid transparent' }
            }
            onClick={() => onNavigate(item.id)}
            onMouseEnter={e => {
              if (currentPage !== item.id) {
                e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
                e.currentTarget.style.color = 'var(--foreground)';
              }
            }}
            onMouseLeave={e => {
              if (currentPage !== item.id) {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = 'var(--secondary-foreground)';
              }
            }}
          >
            <span className="text-base w-6 text-center flex-shrink-0">{item.icon}</span>
            <div className="min-w-0">
              <div className="text-sm font-medium leading-none mb-0.5">{item.label}</div>
              <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>{item.sublabel}</div>
            </div>
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4" style={{ borderTop: '1px solid var(--border)' }}>
        <button
          className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm transition-all"
          style={{ color: 'var(--muted-foreground)' }}
          onClick={onExit}
          onMouseEnter={e => (e.currentTarget.style.color = 'var(--foreground)')}
          onMouseLeave={e => (e.currentTarget.style.color = 'var(--muted-foreground)')}
        >
          <span>←</span>
          <span>بازگشت به صفحه اصلی</span>
        </button>
      </div>
    </aside>
  );
}

export default function App() {
  const [inApp, setInApp] = useState(false);
  const [page, setPage] = useState<Page>('dashboard');
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  if (!inApp) {
    return <Landing onEnterApp={() => setInApp(true)} />;
  }

  return (
    <div className="min-h-screen" style={{ background: 'var(--background)' }}>
      {/* Desktop sidebar */}
      <div className="hidden md:block">
        <Sidebar currentPage={page} onNavigate={setPage} onExit={() => setInApp(false)} />
      </div>

      {/* Mobile top bar */}
      <div
        className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-3"
        style={{ background: 'var(--card)', borderBottom: '1px solid var(--border)' }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white font-bold text-xs"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #4f46e5)' }}
          >
            B
          </div>
          <span className="font-display font-semibold text-sm" style={{ color: 'var(--foreground)' }}>BrandPilot</span>
        </div>
        <button
          className="p-2 rounded-lg"
          style={{ background: 'var(--secondary)' }}
          onClick={() => setMobileNavOpen(v => !v)}
        >
          <div className="flex flex-col gap-1">
            <div className="w-4 h-0.5 rounded-full" style={{ background: 'var(--foreground)' }} />
            <div className="w-4 h-0.5 rounded-full" style={{ background: 'var(--foreground)' }} />
            <div className="w-4 h-0.5 rounded-full" style={{ background: 'var(--foreground)' }} />
          </div>
        </button>
      </div>

      {/* Mobile nav overlay */}
      {mobileNavOpen && (
        <div
          className="md:hidden fixed inset-0 z-40"
          style={{ background: 'rgba(0,0,0,0.7)' }}
          onClick={() => setMobileNavOpen(false)}
        >
          <div
            className="absolute top-0 right-0 h-full w-64 flex flex-col"
            style={{ background: 'var(--card)', borderLeft: '1px solid var(--border)' }}
            onClick={e => e.stopPropagation()}
          >
            <div className="p-5 pt-16">
              {navItems.map(item => (
                <button
                  key={item.id}
                  className="w-full flex items-center gap-3 px-3 py-3 rounded-xl mb-2 text-right"
                  style={
                    page === item.id
                      ? { background: 'rgba(124,58,237,0.12)', color: '#c4b5fd' }
                      : { color: 'var(--secondary-foreground)' }
                  }
                  onClick={() => { setPage(item.id); setMobileNavOpen(false); }}
                >
                  <span>{item.icon}</span>
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main content */}
      <main
        className="md:mr-60 pt-16 md:pt-0 min-h-screen"
        style={{ direction: 'rtl' }}
      >
        {page === 'dashboard' && <Dashboard />}
        {page === 'audit' && <BrandAudit />}
        {page === 'roadmap' && <Roadmap />}
        {page === 'content' && <ContentAI />}
      </main>
    </div>
  );
}
