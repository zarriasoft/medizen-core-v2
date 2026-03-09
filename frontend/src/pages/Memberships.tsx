import React, { useState, useEffect } from 'react';
import { CreditCard, ShieldCheck, Zap, Activity, Star, Plus, X, Download } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { patientsApi, membershipsApi } from '../services/api';
import { exportToExcel } from '../utils/exportToExcel';

const memberships = [
    {
        id: 1,
        name: 'Básica',
        price: '$45,000',
        frequency: 'mensual',
        features: ['1 Sesión presencial al mes', 'Acceso a App Básica', 'Evaluación IEIM Trimestral'],
        icon: <Activity className="w-6 h-6 text-slate-500" />,
        color: 'slate'
    },
    {
        id: 2,
        name: 'Integrativa',
        price: '$85,000',
        frequency: 'mensual',
        popular: true,
        features: ['2 Sesiones presenciales al mes', 'Acceso App Premium', 'Evaluación IEIM Mensual', 'Chat con especialista'],
        icon: <Star className="w-6 h-6 text-teal-500" />,
        color: 'teal'
    },
    {
        id: 3,
        name: 'Premium Care',
        price: '$150,000',
        frequency: 'mensual',
        features: ['4 Sesiones presenciales al mes', 'Prioridad de agenda', 'IEIM Continuo', 'Programa Nutricional'],
        icon: <ShieldCheck className="w-6 h-6 text-indigo-500" />,
        color: 'indigo'
    }
];

export default function Memberships() {
    const [patientsList, setPatientsList] = useState<any[]>([]);
    const [isVentaModalOpen, setIsVentaModalOpen] = useState(false);

    // Formularios
    const { register: regVenta, handleSubmit: handleVenta, reset: resetVenta } = useForm();

    const loadData = async () => {
        try {
            const pats = await patientsApi.getAll();
            setPatientsList(pats);
        } catch (error) {
            console.error("Error loading patients", error);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const onNuevaVenta = async (data: any) => {
        try {
            await membershipsApi.create({
                patient_id: parseInt(data.patient_id),
                membership_type: data.membership_type,
                total_sessions: parseInt(data.total_sessions),
                end_date: data.end_date || null
            });
            setIsVentaModalOpen(false);
            resetVenta();
            toast.success("Membresía registrada correctamente");
        } catch (error) {
            console.error("Error registrando membresía", error);
            toast.error("Hubo un error al registrar la membresía");
        }
    };

    const handleExport = () => {
        const dataToExport = memberships.map(m => ({
            ID: m.id,
            Plan: m.name,
            Precio: m.price,
            Frecuencia: m.frequency,
            Características: m.features.join(', ')
        }));
        exportToExcel(dataToExport, 'Planes_Membresia_Medizen');
    };

    return (
        <>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Modelos de Membresía</h1>
                    <p className="text-slate-500 text-sm mt-1">Gestión de planes de suscripción para pacientes</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleExport}
                        className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2 active:scale-95 duration-200"
                    >
                        <Download className="w-4 h-4" />
                        Exportar Excel
                    </button>
                    <button onClick={() => setIsVentaModalOpen(true)} className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors shadow-lg shadow-slate-900/20 active:scale-95 duration-200 flex items-center gap-2">
                        <CreditCard className="w-4 h-4" />
                        Nueva Venta
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {memberships.map((plan) => (
                    <div key={plan.id} className={`relative bg-white rounded-2xl border ${plan.popular ? 'border-teal-500 shadow-md shadow-teal-500/10' : 'border-slate-200 shadow-sm'} p-6 flex flex-col`}>
                        {plan.popular && (
                            <div className="absolute top-0 right-6 transform -translate-y-1/2">
                                <span className="bg-gradient-to-r from-teal-500 to-emerald-400 text-white text-[10px] font-bold uppercase tracking-wider py-1 px-3 rounded-full shadow-sm">
                                    Más Elegido
                                </span>
                            </div>
                        )}

                        <div className="flex items-center gap-3 mb-4">
                            <div className={`p-3 rounded-xl bg-${plan.color}-50`}>
                                {plan.icon}
                            </div>
                            <h3 className="text-xl font-bold text-slate-800">{plan.name}</h3>
                        </div>

                        <div className="mb-6">
                            <span className="text-3xl font-bold text-slate-800">{plan.price}</span>
                            <span className="text-slate-500 text-sm">/{plan.frequency}</span>
                        </div>

                        <ul className="space-y-3 mb-8 flex-1">
                            {plan.features.map((feature, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                                    <Zap className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                                    <span>{feature}</span>
                                </li>
                            ))}
                        </ul>

                        <button onClick={() => toast('Función "Editar Plan" - Próximamente', { icon: '🚧' })} className={`w-full py-2.5 rounded-xl font-medium transition-colors ${plan.popular ? 'bg-teal-600 text-white hover:bg-teal-700 shadow-lg shadow-teal-600/20 active:scale-95' : 'bg-slate-100 text-slate-700 hover:bg-slate-200 active:scale-95'}`}>
                            Editar Plan
                        </button>
                    </div>
                ))}
            </div>
            {isVentaModalOpen && (
                <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-md shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center justify-between p-6 border-b border-slate-100">
                            <h2 className="text-xl font-bold text-slate-800">Nueva Venta de Membresía</h2>
                            <button onClick={() => setIsVentaModalOpen(false)} className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-50 rounded-full transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleVenta(onNuevaVenta)} className="p-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Paciente</label>
                                    <select required {...regVenta("patient_id")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all">
                                        <option value="">Seleccione un paciente</option>
                                        {patientsList.map(p => (
                                            <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Tipo de Plan</label>
                                        <select required {...regVenta("membership_type")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all">
                                            <option value="">Seleccionar</option>
                                            <option value="Básica">Básica</option>
                                            <option value="Integrativa">Integrativa</option>
                                            <option value="Premium Care">Premium Care</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Sesiones Totales</label>
                                        <input required type="number" {...regVenta("total_sessions")} defaultValue="1" min="1" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Fecha de Término (Opcional)</label>
                                    <input type="date" {...regVenta("end_date")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-400 focus:text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                </div>
                            </div>
                            <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-slate-50">
                                <button type="button" onClick={() => setIsVentaModalOpen(false)} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-xl transition-colors">Cancelar</button>
                                <button type="submit" className="px-5 py-2.5 bg-teal-500 hover:bg-teal-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-teal-500/20 transition-all active:scale-95">Registrar Venta</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
