import React, { useState } from 'react';
import Navbar from './components/Navbar';
import MarkAttendancePage from './pages/MarkAttendancePage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import BatchesPage from './pages/BatchesPage';
import StudentsPage from './pages/StudentsPage';
import TeachersPage from './pages/TeachersPage';
import SettingsPage from './pages/SettingsPage';
import FeeTrackingPage from './pages/FeeTrackingPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <AdminDashboardPage setActiveTab={setActiveTab} />
        )}

        {activeTab === 'attendance' && (
          <MarkAttendancePage />
        )}

        {activeTab === 'batches' && (
          <BatchesPage />
        )}

        {activeTab === 'students' && (
          <StudentsPage />
        )}

        {activeTab === 'teachers' && (
          <TeachersPage />
        )}

        {activeTab === 'fees' && (
          <FeeTrackingPage />
        )}

        {activeTab === 'settings' && (
          <SettingsPage />
        )}
      </main>
    </div>
  );
}
