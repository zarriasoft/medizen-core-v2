import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Users, Calendar, ChevronRight, TrendingUp, AlertCircle, Bell, Download } from 'lucide-react';
import { dashboardApi } from '../services/api';
import { exportToExcel } from '../utils/exportToExcel';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const mockIeimData = [
    { name: 'Sem 1', score: 6.2 },
    { name: 'Sem 2', score: 6.8 },
    { name: 'Sem 3', score: 6.5 },
    { name: 'Sem 4', score: 7.2 },
    { name: 'Sem 5', score: 7.8 },
    { name: 'Sem 6', score: 8.5 },
];

function StatCard({ title, value, trend, icon }: any) {
    const isPositive = trend.includes('+');
    return (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-slate-50 rounded-lg">{icon}</div>
                <span className={`text-xs font-medium px-2 py-1 rounded-md flex items-center gap-1 ${isPositive ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
                    {trend}
                </span>
            </div>
            <div>
                <h3 className="text-slate-500 font-medium text-sm">{title}</h3>
                <p className="text-2xl font-bold text-slate-800 mt-1">{value}</p>
            </div>
        </div>
    );
}

export default function Dashboard() {
    const [metrics, setMetrics] = useState<any>({
        active_patients: 0,
        avg_ieim_score: 0.0,
        sessions_today: 0,
        abandonment_risk: 0
    });
    const [alerts, setAlerts] = useState<any[]>([]);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const metricsData = await dashboardApi.getMetrics();
                setMetrics(metricsData);
                const alertsData = await dashboardApi.getAlerts();
                setAlerts(alertsData);
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            }
        };
        fetchDashboardData();
    }, []);

    const handleExport = () => {
        const dataToExport = [
            {
                'Pacientes Activos': metrics.active_patients,
                'Promedio IEIM': metrics.avg_ieim_score,
                'Sesiones Hoy': metrics.sessions_today,
                'Riesgo Abandono': metrics.abandonment_risk,
                'Alertas Críticas': alerts.filter(a => a.type === 'critical').length,
                'Total Alertas': alerts.length
            }
        ];
        exportToExcel(dataToExport, 'Dashboard_Resumen_Medizen');
    };

    return (
        <>
            <div className="flex items-center justify-between xl:mb-2 text-slate-800">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Panel de Control</h1>
                    <p className="text-slate-500 text-sm mt-1">Visión integral de la clínica y pacientes activos</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleExport}
                        className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2 active:scale-95 duration-200"
                    >
                        <Download className="w-4 h-4" />
                        Exportar Excel
                    </button>
                    <Link to="/patients" className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors shadow-lg shadow-slate-900/20 active:scale-95 duration-200 flex items-center gap-2">
                        + Nuevo Paciente
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard title="Pacientes Activos" value={metrics.active_patients} trend="N/A" icon={<Users className="w-6 h-6 text-indigo-500" />} />
                <StatCard title="Promedio IEIM" value={metrics.avg_ieim_score} trend="N/A" icon={<Activity className="w-6 h-6 text-teal-500" />} />
                <StatCard title="Sesiones Hoy" value={metrics.sessions_today} trend="N/A" icon={<Calendar className="w-6 h-6 text-amber-500" />} />
                <StatCard title="Riesgo Abandono" value={metrics.abandonment_risk} trend="N/A" icon={<TrendingUp className="w-6 h-6 text-rose-500" />} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                    <h2 className="text-lg font-semibold text-slate-800 mb-4">Evolución IEIM Global</h2>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={mockIeimData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} dx={-10} domain={[0, 10]} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    cursor={{ stroke: '#f1f5f9', strokeWidth: 2 }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="score"
                                    stroke="#0d9488"
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#0d9488', strokeWidth: 2, stroke: '#fff' }}
                                    activeDot={{ r: 6, strokeWidth: 0 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 overflow-hidden flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Bell className="w-5 h-5 text-rose-500" />
                            <h2 className="text-lg font-semibold text-slate-800">Alertas Clínicas</h2>
                        </div>
                        <span className="bg-rose-100 text-rose-600 px-2 py-0.5 rounded-full text-xs font-bold">{alerts.length}</span>
                    </div>
                    <div className="space-y-3 overflow-y-auto flex-1 pr-2">
                        {alerts.length === 0 ? (
                            <p className="text-sm text-slate-500 text-center mt-10">No hay alertas pendientes.</p>
                        ) : (
                            alerts.map((alert, idx) => (
                                <div key={idx} className={`flex items-start gap-3 p-3 rounded-xl border transition-colors ${alert.type === 'critical' ? 'bg-rose-50 border-rose-100 text-rose-800' :
                                    alert.type === 'warning' ? 'bg-amber-50 border-amber-100 text-amber-800' :
                                        'bg-blue-50 border-blue-100 text-blue-800'
                                    }`}>
                                    <AlertCircle className={`w-5 h-5 shrink-0 mt-0.5 ${alert.type === 'critical' ? 'text-rose-500' :
                                        alert.type === 'warning' ? 'text-amber-500' :
                                            'text-blue-500'
                                        }`} />
                                    <div className="flex-1">
                                        <p className="text-sm font-medium leading-snug">{alert.message}</p>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
