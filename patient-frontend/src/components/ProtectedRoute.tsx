import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, isLoading } = useAuth();
    
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <div className="text-emerald-600 font-medium">Cargando portal...</div>
            </div>
        );
    }
    
    return isAuthenticated ? children : <Navigate to="/login" replace />;
}
