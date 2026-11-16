import React from 'react';
import { useLanguage } from '../context/LanguageContext';

export default function Navbar({ activeTab, setActiveTab }) {
  const { lang, toggleLanguage, t } = useLanguage();

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div
          className="brand"
          onClick={() => setActiveTab('dashboard')}
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
          </svg>
          <span>{t('appTitle')}</span>
        </div>

        <div className="nav-links">
          <button
            className={`nav-pill ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            {t('dashboard')}
          </button>

          <button
            className={`nav-pill ${activeTab === 'attendance' ? 'active' : ''}`}
            onClick={() => setActiveTab('attendance')}
          >
            {t('markAttendance')}
          </button>

          <button
            className={`nav-pill ${activeTab === 'batches' ? 'active' : ''}`}
            onClick={() => setActiveTab('batches')}
          >
            {t('batches')}
          </button>

          <button
            className={`nav-pill ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => setActiveTab('students')}
          >
            {t('students')}
          </button>

          <button
            className={`nav-pill ${activeTab === 'teachers' ? 'active' : ''}`}
            onClick={() => setActiveTab('teachers')}
          >
            {t('teachers')}
          </button>

          <button
            className={`nav-pill ${activeTab === 'fees' ? 'active' : ''}`}
            onClick={() => setActiveTab('fees')}
          >
            {t('fees')}
          </button>

          <button
            className={`nav-pill ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            {t('settings')}
          </button>

          <button
            className="nav-pill"
            onClick={toggleLanguage}
            title="Toggle Language"
            style={{ fontWeight: 700 }}
          >
            {lang === 'en' ? 'Hindi' : 'English'}
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="role-badge admin">
              Admin
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
}
