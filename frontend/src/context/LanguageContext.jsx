import React, { createContext, useContext, useState } from 'react';

const translations = {
  en: {
    appTitle: "HealthID AI",
    login: "Login",
    register: "Register",
    logout: "Logout",
    dashboard: "Dashboard",
    patientName: "Patient Name",
    healthId: "Health ID",
    doctor: "Doctor",
    appointments: "Appointments",
    labOrders: "Lab Orders",
    prescriptions: "Prescriptions",
    timeline: "Smart Medical Timeline",
    offlineMessage: "You are currently offline. Changes will be synced automatically when connection is restored.",
    micStart: "Voice Dictation",
    micListening: "Listening...",
    language: "Language",
    english: "English",
    hindi: "हिन्दी"
  },
  hi: {
    appTitle: "हेल्थ-आईडी एआई",
    login: "लॉग इन",
    register: "पंजीकरण",
    logout: "लॉग आउट",
    dashboard: "डैशबोर्ड",
    patientName: "मरीज़ का नाम",
    healthId: "स्वास्थ्य आईडी",
    doctor: "चिकित्सक",
    appointments: "अपॉइंटमेंट",
    labOrders: "लैब टेस्ट",
    prescriptions: "दवा पर्ची",
    timeline: "स्मार्ट मेडिकल टाइमलाइन",
    offlineMessage: "आप ऑफलाइन हैं। नेटवर्क आते ही आपका डेटा स्वतः सिंक हो जाएगा।",
    micStart: "बोलकर दर्ज करें",
    micListening: "सुन रहा है...",
    language: "भाषा",
    english: "English",
    hindi: "हिन्दी"
  }
};

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState('en');

  const t = (key) => {
    return translations[lang]?.[key] || translations['en'][key] || key;
  };

  const toggleLanguage = (newLang) => {
    setLang(newLang || (lang === 'en' ? 'hi' : 'en'));
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang: toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
