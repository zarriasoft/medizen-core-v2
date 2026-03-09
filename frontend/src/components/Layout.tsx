import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, Users, Calendar, Brain, Settings, HeartPulse, Menu, Search, Bell, LogOut, CreditCard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

import { motion, AnimatePresence } from 'framer-motion';

export default function Layout() {
    const [sidebarOpen, setSidebarOpen] = React.useState(true);
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const NavItem = ({ icon, text, to }: { icon: any, text: string, to: string }) => {
        const active = location.pathname === to || (to !== '/' && location.pathname.startsWith(to));
        return (
            <Link to={to} className={`flex items-center gap-3 p-3 rounded-xl w-full transition-all duration-200 group ${active ? 'bg-teal-50 text-teal-700' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'}`}>
                <div className={`${active ? 'text-teal-600' : 'text-slate-400 group-hover:text-slate-600'}`}>
                    {icon}
                </div>
                {sidebarOpen && <span className="font-medium text-sm whitespace-nowrap">{text}</span>}
                {sidebarOpen && active && <div className="ml-auto w-1.5 h-4 bg-teal-500 rounded-full" />}
            </Link>
        );
    };

    return (
        <div className="flex h-screen bg-slate-50 text-slate-900 font-sans selection:bg-teal-200">

            {/* Sidebar */}
            <aside className={`bg-white border-r border-slate-200 flex flex-col transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-20'}`}>
                <div className="h-16 flex items-center justify-between px-4 border-b border-slate-100">
                    {sidebarOpen ? (
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center shadow-lg shadow-teal-600/20">
                                <HeartPulse className="text-white w-5 h-5" />
                            </div>
                            <span className="font-bold text-xl tracking-tight text-slate-800">Medi<span className="text-teal-600">Zen</span></span>
                        </div>
                    ) : (
                        <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center mx-auto shadow-lg shadow-teal-600/20">
                            <HeartPulse className="text-white w-5 h-5" />
                        </div>
                    )}
                </div>

                <nav className="flex-1 overflow-y-auto py-4 px-3 flex flex-col gap-1">
                    <NavItem icon={<Activity />} text="Dashboard" to="/" />
                    <NavItem icon={<Users />} text="Pacientes" to="/patients" />
                    <NavItem icon={<Calendar />} text="Agenda" to="/calendar" />
                    <NavItem icon={<Brain />} text="IEIM & Evolución" to="/ieim" />
                    <NavItem icon={<Activity />} text="Programas" to="/programs" />
                    <NavItem icon={<CreditCard />} text="Membresías" to="/memberships" />
                    <div className="mt-auto">
                        <NavItem icon={<Settings />} text="Configuración" to="/settings" />
                    </div>
                </nav>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">

                {/* Header */}
                <header className="h-16 bg-white flex items-center justify-between px-6 border-b border-slate-200 z-10">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="p-2 -ml-2 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors"
                        >
                            <Menu className="w-5 h-5" />
                        </button>
                        <div className="relative hidden md:block w-64">
                            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                            <input
                                type="text"
                                placeholder="Buscar paciente, ID..."
                                className="w-full pl-9 pr-4 py-2 bg-slate-100 border-none rounded-full text-sm focus:ring-2 focus:ring-teal-500/50 outline-none transition-all"
                            />
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <button className="relative p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-colors">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
                        </button>
                        <div className="flex flex-col items-end mr-2 hidden sm:flex">
                            <span className="text-sm font-medium text-slate-700">{user?.full_name || user?.username}</span>
                            <span className="text-xs text-slate-500 capitalize">{user?.role}</span>
                        </div>
                        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-teal-500 to-emerald-400 p-0.5 shadow-sm cursor-pointer">
                            <div className="w-full h-full bg-white rounded-full flex items-center justify-center font-medium text-sm text-teal-700 uppercase">
                                {user?.username?.substring(0, 2) || 'DR'}
                            </div>
                        </div>
                        <button onClick={handleLogout} className="p-2 ml-2 text-rose-500 hover:bg-rose-50 rounded-full transition-colors" title="Cerrar Sesión">
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </header>

                {/* Page Content View */}
                <main className="flex-1 overflow-y-auto p-6 bg-slate-50/50">
                    <div className="max-w-7xl mx-auto space-y-6">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={location.pathname}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.2 }}
                            >
                                <Outlet />
                            </motion.div>
                        </AnimatePresence>
                    </div>
                </main>
            </div>
        </div>
    );
}
