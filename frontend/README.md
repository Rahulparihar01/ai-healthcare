# 💻 HealthID AI — Frontend PWA Documentation

The **HealthID AI Frontend** is a modern, glassmorphic Progressive Web Application (PWA) built with **React**, **Vite**, and **TailwindCSS**. It provides intuitive, role-tailored dashboards for doctors, receptionists, lab technicians, patients, and administrators, equipped with voice dictation and offline-first queueing.

---

## 🌟 Core Features & Innovations

### 1. Role-Tailored Glassmorphic Interfaces
- **Doctor Dashboard**: Smart patient timeline, AI clinical assistant, e-prescription issuer, and automated allergy/interaction alerts.
- **Receptionist Dashboard**: Quick patient registration, appointment queue management, and HealthID QR scanner integration.
- **Patient Dashboard**: Personal medical record access, appointment history, and downloadable prescription/billing receipts.
- **Lab Technician & Admin Dashboards**: Lab order processing and clinic-wide analytics.

### 2. Hands-Free Voice Dictation (`useVoiceInput.js`)
- Uses the Browser Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) to allow doctors and receptionists to dictate notes, diagnoses, and patient details hands-free.

### 3. Multi-Language i18n Support (`LanguageContext.jsx`)
- Built-in internationalization context supporting seamless dynamic switching between **English (`en`)** and **Hindi (`hi`)**.

### 4. PWA Offline Request Queueing (`OfflineIndicator.jsx`)
- **Offline First**: Automatically detects network loss, displays an offline banner, and queues patient registration and record creation requests locally in `localStorage`.
- **Auto-Sync Replay**: Automatically replays queued requests sequentially when network connectivity is restored.

---

## 📂 Project Structure

```
frontend/
├── public/               # Static Assets & PWA Icons
├── src/
│   ├── components/       # UI Dashboards & Components
│   │   ├── DoctorDashboard.jsx
│   │   ├── PatientDashboard.jsx
│   │   ├── ReceptionistDashboard.jsx
│   │   ├── HospitalAdminDashboard.jsx
│   │   ├── LabTechnicianDashboard.jsx
│   │   ├── OfflineIndicator.jsx   # Offline banner & request queueing
│   │   ├── Login.jsx
│   │   └── Register.jsx
│   ├── context/          # State Providers
│   │   ├── AuthContext.jsx       # Authentication & JWT Management
│   │   └── LanguageContext.jsx   # English & Hindi i18n Context
│   ├── hooks/            # Custom Hooks
│   │   └── useVoiceInput.js      # Web Speech API Voice Dictation Hook
│   ├── api.js            # Axios Instance with Interceptors & Base URL Configuration
│   ├── App.jsx           # Router Configuration & Provider Wrappers
│   └── index.css         # Global Styles & Glassmorphic Utilities
├── index.html            # Main HTML Shell
├── package.json          # Frontend Dependencies & Scripts
└── vite.config.js        # Vite Build & Proxy Configuration
```

---

## ⚡ Setup & Development

### 1. Installation
Install project dependencies:
```bash
cd frontend
npm install
```

### 2. Environment Configuration
Create a `.env` file in the `frontend` root:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Starting Development Server
Launch Vite development server with hot module replacement (HMR):
```bash
npm run dev
```
The application will be accessible at `http://localhost:5173`.

### 4. Production Build
Compile optimized production assets:
```bash
npm run build
```
Output files will be generated in `frontend/dist/`.

---

## 🎤 Usage Guide: Voice Dictation & Language Switching

### Voice Dictation
Call the custom hook inside any component:
```javascript
import useVoiceInput from '../hooks/useVoiceInput';

const { isListening, startListening, stopListening, transcript } = useVoiceInput((text) => {
  setNotes((prev) => prev + ' ' + text);
});

// Trigger start:
<button onClick={() => startListening('en-US')}>🎤 Dictate Notes</button>
```

### Language Toggle
Access translations using `useLanguage()`:
```javascript
import { useLanguage } from '../context/LanguageContext';

const { lang, setLang, t } = useLanguage();

return (
  <button onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}>
    {t('language')}: {lang.toUpperCase()}
  </button>
);
```
