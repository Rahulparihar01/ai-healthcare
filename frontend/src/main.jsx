import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { registerSW } from 'virtual:pwa-register'

// Register Service Worker for offline capability
const updateSW = registerSW({
  onNeedRefresh() {
    console.log('New content available, refresh page to update.')
  },
  onOfflineReady() {
    console.log('App is ready for offline use.')
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

