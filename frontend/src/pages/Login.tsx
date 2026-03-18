import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Login: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            // Usar form-urlencoded para OAuth2
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await api.post('/auth/login', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            // Con el token, obtenemos el usuario actual
            const tempToken = response.data.access_token;
            api.defaults.headers.common['Authorization'] = `Bearer ${tempToken}`;

            const userResponse = await api.get('/auth/me');

            // Iniciar sesión en el contexto
            login(tempToken, userResponse.data);

            toast.success('¡Bienvenido de nuevo!');
            navigate('/');
        } catch (error: any) {
            console.error('Login error:', error);
            const errorMsg = error.response?.data?.detail || error.message || 'Error desconocido';
            toast.error(`Error: ${errorMsg}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
            {/* Background decorations */}
            <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-blue-500/10 blur-3xl mix-blend-multiply"></div>
            <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 rounded-full bg-amber-500/10 blur-3xl mix-blend-multiply"></div>

            <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <motion.div
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5 }}
                    className="flex justify-center"
                >
                    <div className="bg-white p-3 rounded-2xl shadow-lg border border-slate-100">
                        <Activity className="h-12 w-12 text-blue-600" />
                    </div>
                </motion.div>
                <motion.h2
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="mt-6 text-center text-3xl font-bold tracking-tight text-slate-900"
                >
                    MediZen Core 2.0
                </motion.h2>
                <motion.p
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="mt-2 text-center text-sm text-slate-500"
                >
                    Inicia sesión para acceder al sistema
                </motion.p>
            </div>

            <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10"
            >
                <div className="bg-white/80 backdrop-blur-md py-8 px-4 shadow-xl shadow-slate-200/50 sm:rounded-2xl sm:px-10 border border-slate-100/50">
                    <form className="space-y-6" onSubmit={handleLogin}>
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-slate-700">
                                Usuario
                            </label>
                            <div className="mt-2 relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Mail className="h-5 w-5 text-slate-400" />
                                </div>
                                <input
                                    id="username"
                                    name="username"
                                    type="text"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="block w-full pl-10 sm:text-sm border-slate-200 rounded-xl focus:ring-blue-500 focus:border-blue-500 transition-colors bg-slate-50 border py-3"
                                    placeholder="usuario123"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
                                Contraseña
                            </label>
                            <div className="mt-2 relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-slate-400" />
                                </div>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full pl-10 sm:text-sm border-slate-200 rounded-xl focus:ring-blue-500 focus:border-blue-500 transition-colors bg-slate-50 border py-3"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <input
                                    id="remember-me"
                                    name="remember-me"
                                    type="checkbox"
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                                />
                                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-700">
                                    Recordarme
                                </label>
                            </div>

                            <div className="text-sm">
                                <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
                                    ¿Olvidaste tu contraseña?
                                </a>
                            </div>
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed disabled:active:scale-100"
                            >
                                {isLoading ? (
                                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                                ) : (
                                    'Ingresar'
                                )}
                            </button>
                        </div>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-xs text-slate-500">
                            Usa un entorno seguro. Los accesos están monitorizados.
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Login;
