import React, { createContext, useContext, useState } from 'react';

const translations = {
  en: {
    appTitle: 'Apex Institute',
    markAttendance: 'Mark Attendance',
    dashboard: 'Dashboard',
    batches: 'Batches',
    students: 'Students',
    teachers: 'Teachers',
    fees: 'Fees',
    settings: 'Settings',
    logout: 'Logout',
    present: 'Present',
    absent: 'Absent',
    unmarked: 'Unmarked',
    totalStudents: 'Total Students',
    submitAttendance: 'Submit Attendance',
    alreadyMarkedToday: 'Attendance already submitted for today. You can update it below.',
    sendWhatsAppAll: 'Send WhatsApp to All Parents',
    absentSummary: 'Absent List Summary',
    retryFailed: 'Retry Failed',
    waDirectLink: 'Send via WhatsApp App',
    selectBatch: 'Select Batch',
    selectDate: 'Select Date',
    loginTitle: 'Apex Institute Login',
    email: 'Email',
    password: 'Password',
    loginBtn: 'Sign In',
    quickFillAdmin: 'Demo: Login as Admin',
    quickFillTeacher: 'Demo: Login as Teacher (Rahul)',
    attendanceRate: 'Attendance Rate',
    todayOverview: "Today's Attendance Overview",
    noAbsentToday: 'No absent students in this batch today!'
  },
  hi: {
    appTitle: 'एपेक्स इंस्टिट्यूट',
    markAttendance: 'हाज़िरी लगाएँ',
    dashboard: 'डैशबोर्ड',
    batches: 'बैच',
    students: 'छात्र',
    teachers: 'शिक्षक',
    fees: 'फीस',
    settings: 'सेटिंग्स',
    logout: 'लॉगआउट',
    present: 'उपस्थित (P)',
    absent: 'अनुपस्थित (A)',
    unmarked: 'अचिह्नित',
    totalStudents: 'कुल छात्र',
    submitAttendance: 'हाज़िरी जमा करें',
    alreadyMarkedToday: 'आज की हाज़िरी पहले ही दर्ज हो चुकी है। आप नीचे बदलाव कर सकते हैं।',
    sendWhatsAppAll: 'सभी अभिभावकों को WhatsApp भेजें',
    absentSummary: 'अनुपस्थित छात्रों की सूची',
    retryFailed: 'पुनः प्रयास करें',
    waDirectLink: 'WhatsApp ऐप से भेजें',
    selectBatch: 'बैच चुनें',
    selectDate: 'तारीख चुनें',
    loginTitle: 'एपेक्स इंस्टिट्यूट लॉगिन',
    email: 'ईमेल',
    password: 'पासवर्ड',
    loginBtn: 'लॉग इन करें',
    quickFillAdmin: 'डेमो: एडमिन लॉगिन',
    quickFillTeacher: 'डेमो: शिक्षक लॉगिन (राहुल)',
    attendanceRate: 'उपस्थिति दर',
    todayOverview: 'आज की उपस्थिति विवरण',
    noAbsentToday: 'आज इस बैच में कोई छात्र अनुपस्थित नहीं है! 🎉'
  }
};

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(localStorage.getItem('apex_lang') || 'en');

  const toggleLanguage = () => {
    const nextLang = lang === 'en' ? 'hi' : 'en';
    setLang(nextLang);
    localStorage.setItem('apex_lang', nextLang);
  };

  const t = (key) => translations[lang]?.[key] || translations.en[key] || key;

  return (
    <LanguageContext.Provider value={{ lang, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used within LanguageProvider');
  return context;
}
