import './styles/App.css';
import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import Header from './components/header.js'
import SideBar from './components/sidebar.js';

import Inici from './pages/Inici.js';
import Quisom from './pages/Quisom.js';
import Bot from './pages/Bot.js';
import Ajuda from './pages/Ajuda.js';

export const metadata = {
  title: 'Eulàlia Chat'
}

function App() {
  const [sidebarOpen, setSideBarOpen] = useState(false);
  
  const handleViewSidebar = () => {
    setSideBarOpen(!sidebarOpen);
  };
  
  return (
    <div>
      <Router>
        <Header onClick={handleViewSidebar} />
        <SideBar isOpen={sidebarOpen} />
          <Routes>
            <Route path='/' element={<Inici/>} />
            <Route path='/quisom' element={<Quisom/>} />
            <Route path='/bot' element={<Bot/>} />
            <Route path='/ajuda' element={<Ajuda/>} />
          </Routes>
      </Router>
    </div>
  );
}

export default App;