/**
 * App — Root application component with routing.
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Violations from './pages/Violations';
import Analytics from './pages/Analytics';
import LiveFeed from './pages/LiveFeed';
import Assistant from './pages/Assistant';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/violations" element={<Violations />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/live-feed" element={<LiveFeed />} />
            <Route path="/assistant" element={<Assistant />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
