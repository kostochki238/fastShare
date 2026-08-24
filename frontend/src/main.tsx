import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import {CookiesProvider} from 'react-cookie'

createRoot(document.getElementsByTagName('body')[0]!).render(
  <CookiesProvider>
    <App />
  </CookiesProvider>
)
