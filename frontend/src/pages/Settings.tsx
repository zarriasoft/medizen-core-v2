import React, { useState, useEffect } from 'react';
import { User, Bell, Shield, Key, Save } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';

export default function Settings() {
    const { user, login, token } = useAuth();

    // Split full_name into first and last name for the form if needed, or just use full_name
    const [formData, setFormData] = useState({
        full_name: '',
        email: ''
    });

    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (user) {
            setFormData({
                full_name: user.full_name || '',
                email: user.email || ''
            });
        }
    }, [user]);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const updatedUser = await authApi.updateProfile(formData);

            // Update auth context
            if (token) {
                login(token, updatedUser);
            }

            toast.success("Configuraciones guardadas exitosamente", { icon: '✅' });
        } catch (error) {
            console.error("Failed to update profile", error);
            toast.error("Error al guardar la configuración");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-slate-800">Configuración</h1>
                <p className="text-slate-500 text-sm mt-1">Administra tus preferencias y ajustes del sistema</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="flex flex-col md:flex-row">
                    {/* Sidebar Settings */}
                    <div className="w-full md:w-64 bg-slate-50/50 border-r border-slate-100 p-6 flex flex-col gap-2">
                        <button className="flex items-center gap-3 px-4 py-3 bg-teal-50 text-teal-700 font-medium rounded-xl transition-all">
                            <User className="w-5 h-5" />
                            Perfil
                        </button>
                        <button className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-100 font-medium rounded-xl transition-all">
                            <Bell className="w-5 h-5 text-slate-400" />
                            Notificaciones
                        </button>
                        <button className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-100 font-medium rounded-xl transition-all">
                            <Shield className="w-5 h-5 text-slate-400" />
                            Privacidad
                        </button>
                        <button className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-100 font-medium rounded-xl transition-all">
                            <Key className="w-5 h-5 text-slate-400" />
                            Seguridad
                        </button>
                    </div>

                    {/* Main Settings Area */}
                    <div className="flex-1 p-8">
                        <h2 className="text-xl font-bold text-slate-800 mb-6">Información Personal</h2>

                        <form onSubmit={handleSave} className="space-y-6">
                            <div className="flex items-center gap-6 pb-6 border-b border-slate-100">
                                <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-teal-500 to-emerald-400 p-1 shadow-md cursor-pointer hover:opacity-90 transition-opacity">
                                    <div className="w-full h-full bg-white rounded-full flex items-center justify-center font-bold text-2xl text-teal-700">
                                        DR
                                    </div>
                                </div>
                                <div>
                                    <button type="button" className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm mb-2">
                                        Cambiar foto
                                    </button>
                                    <p className="text-xs text-slate-500">JPG, GIF o PNG. Max 1MB.</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Nombre Completo</label>
                                    <input
                                        type="text"
                                        value={formData.full_name}
                                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                        className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Correo Electrónico</label>
                                    <input
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Especialidad (Visual)</label>
                                    <input type="text" defaultValue="Medicina Funcional e Integrativa" disabled className="w-full p-2.5 bg-slate-100 border border-slate-200 rounded-lg text-sm text-slate-500 cursor-not-allowed" />
                                </div>
                            </div>

                            <div className="pt-6 border-t border-slate-100 flex justify-end">
                                <button type="submit" disabled={isLoading} className="px-6 py-2.5 bg-teal-500 hover:bg-teal-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-teal-500/20 transition-all active:scale-95 flex items-center gap-2 disabled:opacity-70 disabled:active:scale-100">
                                    <Save className="w-4 h-4" />
                                    {isLoading ? 'Guardando...' : 'Guardar Cambios'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
