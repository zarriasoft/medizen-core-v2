import React, { useState, useEffect } from 'react';
import { User, Bell, Shield, Key, Save, Mail } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { authApi, settingsApi } from '../services/api';

export default function Settings() {
    const { user, login, token } = useAuth();
    const [activeTab, setActiveTab] = useState('perfil');

    // Perfil State
    const [formData, setFormData] = useState({
        full_name: '',
        email: ''
    });

    // SMTP Settings State
    const [smtpSettings, setSmtpSettings] = useState({
        smtp_host: 'smtp.gmail.com',
        smtp_port: 587,
        smtp_user: '',
        smtp_password: '',
        admin_email: ''
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

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const data = await settingsApi.getSystemSettings();
                setSmtpSettings({
                    smtp_host: data.smtp_host || 'smtp.gmail.com',
                    smtp_port: data.smtp_port || 587,
                    smtp_user: data.smtp_user || '',
                    smtp_password: data.smtp_password || '',
                    admin_email: data.admin_email || ''
                });
            } catch (error) {
                console.error("Error fetching settings:", error);
            }
        };
        fetchSettings();
    }, []);

    const handleSaveProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const updatedUser = await authApi.updateProfile(formData);
            if (token) {
                login(token, updatedUser);
            }
            toast.success("Perfil guardado exitosamente", { icon: '✅' });
        } catch (error) {
            console.error("Failed to update profile", error);
            toast.error("Error al guardar el perfil");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveSettings = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await settingsApi.updateSystemSettings(smtpSettings);
            toast.success("Configuración de correo guardada", { icon: '✅' });
        } catch (error) {
            console.error("Failed to update settings", error);
            toast.error("Error al guardar configuración");
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
                        <button 
                            onClick={() => setActiveTab('perfil')}
                            className={`flex items-center gap-3 px-4 py-3 font-medium rounded-xl transition-all ${activeTab === 'perfil' ? 'bg-teal-50 text-teal-700' : 'text-slate-600 hover:bg-slate-100'}`}>
                            <User className={`w-5 h-5 ${activeTab === 'perfil' ? '' : 'text-slate-400'}`} />
                            Perfil
                        </button>
                        <button 
                            onClick={() => setActiveTab('notificaciones')}
                            className={`flex items-center gap-3 px-4 py-3 font-medium rounded-xl transition-all ${activeTab === 'notificaciones' ? 'bg-teal-50 text-teal-700' : 'text-slate-600 hover:bg-slate-100'}`}>
                            <Bell className={`w-5 h-5 ${activeTab === 'notificaciones' ? '' : 'text-slate-400'}`} />
                            Notificaciones (Correos)
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
                        {activeTab === 'perfil' && (
                            <div>
                                <h2 className="text-xl font-bold text-slate-800 mb-6">Información Personal</h2>
                                <form onSubmit={handleSaveProfile} className="space-y-6">
                                    <div className="flex items-center gap-6 pb-6 border-b border-slate-100">
                                        <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-teal-500 to-emerald-400 p-1 shadow-md cursor-pointer hover:opacity-90 transition-opacity">
                                            <div className="w-full h-full bg-white rounded-full flex items-center justify-center font-bold text-2xl text-teal-700">
                                                {user?.full_name ? user.full_name.substring(0, 2).toUpperCase() : 'DR'}
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
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Correo Electrónico (Login)</label>
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
                                            {isLoading ? 'Guardando...' : 'Guardar Perfil'}
                                        </button>
                                    </div>
                                </form>
                            </div>
                        )}

                        {activeTab === 'notificaciones' && (
                            <div>
                                <h2 className="text-xl font-bold text-slate-800 mb-2">Configuración de Correos</h2>
                                <p className="text-sm text-slate-500 mb-6">Administra desde dónde se envían los correos automáticos (SMTP) y quién los recibe.</p>
                                
                                <form onSubmit={handleSaveSettings} className="space-y-6">
                                    <div className="bg-blue-50/50 border border-blue-100 p-4 rounded-xl mb-6">
                                        <div className="flex items-start gap-3">
                                            <Mail className="w-5 h-5 text-blue-500 mt-0.5" />
                                            <div>
                                                <h3 className="text-sm font-semibold text-blue-800">¿Quién recibe las alertas?</h3>
                                                <p className="text-xs text-blue-600 mt-1">Este es el correo donde llegarán las notificaciones cuando un nuevo paciente se inscriba o agende una cita.</p>
                                            </div>
                                        </div>
                                        <div className="mt-3">
                                            <input
                                                type="email"
                                                required
                                                placeholder="Ej: admin@medizen.cl"
                                                value={smtpSettings.admin_email}
                                                onChange={(e) => setSmtpSettings({ ...smtpSettings, admin_email: e.target.value })}
                                                className="w-full p-2.5 bg-white border border-blue-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                                            />
                                        </div>
                                    </div>

                                    <h3 className="text-md font-semibold text-slate-800 border-b border-slate-100 pb-2">Servidor Saliente (Remitente)</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Servidor SMTP</label>
                                            <input
                                                type="text"
                                                placeholder="smtp.gmail.com"
                                                value={smtpSettings.smtp_host}
                                                onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_host: e.target.value })}
                                                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Puerto</label>
                                            <input
                                                type="number"
                                                value={smtpSettings.smtp_port}
                                                onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_port: parseInt(e.target.value) || 587 })}
                                                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Correo Remitente (Usuario SMTP)</label>
                                            <input
                                                type="email"
                                                placeholder="Ej: notificaciones@midominio.com"
                                                value={smtpSettings.smtp_user}
                                                onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_user: e.target.value })}
                                                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                                            />
                                            <p className="text-xs text-slate-500 mt-1">El sistema usará esta cuenta para despachar los correos.</p>
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Contraseña de Aplicación SMTP</label>
                                            <input
                                                type="password"
                                                placeholder="••••••••••••••••"
                                                value={smtpSettings.smtp_password}
                                                onChange={(e) => setSmtpSettings({ ...smtpSettings, smtp_password: e.target.value })}
                                                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                                            />
                                            <p className="text-xs text-slate-500 mt-1">Si usas Gmail, debes generar una "Contraseña de Aplicación" en la seguridad de tu cuenta, NO tu clave habitual.</p>
                                        </div>
                                    </div>

                                    <div className="pt-6 border-t border-slate-100 flex justify-end">
                                        <button type="submit" disabled={isLoading} className="px-6 py-2.5 bg-teal-500 hover:bg-teal-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-teal-500/20 transition-all active:scale-95 flex items-center gap-2 disabled:opacity-70 disabled:active:scale-100">
                                            <Save className="w-4 h-4" />
                                            {isLoading ? 'Guardando...' : 'Guardar Configuración SMTP'}
                                        </button>
                                    </div>
                                </form>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
