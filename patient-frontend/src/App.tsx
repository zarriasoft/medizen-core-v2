import { Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Portal from './pages/Portal';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/portal" element={
        <ProtectedRoute>
          <Portal />
        </ProtectedRoute>
      } />
    </Routes>
  );
}

export default App;
