import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

// Import pages
import Dashboard from './pages/Dashboard'
import ResumeUpload from './pages/ResumeUpload'
import InterviewSession from './pages/InterviewSession'
import Analytics from './pages/Analytics'
import PracticeMode from './pages/PracticeMode'

// Import components
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'

const theme = createTheme({
  palette: {
    primary: {
      main: '#2563eb',
    },
    secondary: {
      main: '#64748b',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <Sidebar />
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Topbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/resume-upload" element={<ResumeUpload />} />
            <Route path="/interview-session" element={<InterviewSession />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/practice-mode" element={<PracticeMode />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  )
}

export default App