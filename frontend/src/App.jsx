import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Scanner from './pages/Scanner';
import History from './pages/History';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scanner" element={<Scanner />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
