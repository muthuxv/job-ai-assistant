import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import UploadCV from './pages/UploadCV';
import NewApplication from './pages/NewApplication';
import ApplicationDetail from './pages/ApplicationDetails';
import { getActiveCV } from './services/api';

function App() {
  const [hasCV, setHasCV] = useState(false);

  useEffect(() => { checkCV(); }, []);

  const checkCV = async () => {
    try {
      const cv = await getActiveCV();
      setHasCV(!!cv);
    } catch {
      setHasCV(false);
    }
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <Navbar hasCV={hasCV} />
          <Routes>
            <Route path="/" element={<Dashboard hasCV={hasCV} />} />
            <Route path="/new" element={<NewApplication />} />
            <Route path="/upload-cv" element={<UploadCV onCVUploaded={() => setHasCV(true)} />} />
            <Route path="/application/:id" element={<ApplicationDetail />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;