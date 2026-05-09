import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useStore } from './store'
import { getOnboardingStatus, listModels, getStatus } from './api/client'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import SettingsPage from './pages/Settings'
import LogsPage from './pages/Logs'
import PermissionsPage from './pages/Permissions'
import Layout from './components/Layout'

export default function App() {
  const { onboardingComplete, setOnboardingComplete, setModels, setAgentStatus } = useStore()

  useEffect(() => {
    getOnboardingStatus()
      .then(({ complete }) => setOnboardingComplete(complete))
      .catch(() => {}) // backend may not be ready yet

    listModels()
      .then(setModels)
      .catch(() => {})

    // Poll agent status every 3s
    const interval = setInterval(() => {
      getStatus().then(setAgentStatus).catch(() => {})
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/onboarding"
          element={
            onboardingComplete ? <Navigate to="/" replace /> : <Onboarding />
          }
        />
        <Route
          path="/*"
          element={
            !onboardingComplete ? (
              <Navigate to="/onboarding" replace />
            ) : (
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/chat" element={<Chat />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/logs" element={<LogsPage />} />
                  <Route path="/permissions" element={<PermissionsPage />} />
                </Routes>
              </Layout>
            )
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
