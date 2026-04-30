import React, { useState, useEffect } from 'react';
import { CreditCard, ShieldCheck, Zap, Activity, Star, Plus, X, Download, Trash2, Edit2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { patientsApi, membershipsApi, membershipPlansApi } from '../services/api';
import { exportToExcel } from '../utils/exportToExcel';

export default function Memberships() {
    const [patientsList, setPatientsList] = useState<any[]>([]);
    const [plans, setPlans] = useState<any[]>([]);
    const [memberships, setMemberships] = useState<any[]>([]);
    const [isVentaModalOpen, setIsVentaModalOpen] = useState(false);

    // Tabs state
    const [activeTab, setActiveTab] = useState<'plans' | 'assigned'>('plans');

    // Modal for Creating/Editing Plans
    const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
    const [editingPlanId, setEditingPlanId] = useState<number | null>(null);

    // Modal for Editing Assigned Memberships
    const [isEditAssignedModalOpen, setIsEditAssignedModalOpen] = useState(false);
    const [editingAssignedId, setEditingAssignedId] = useState<number | null>(null);

    // Forms
    const { register: regVenta, handleSubmit: handleVenta, reset: resetVenta, setValue: setVentaValue } = useForm();
    const { register: regPlan, handleSubmit: handlePlan, reset: resetPlan, setValue: setPlanValue } = useForm();
    const { register: regEditAssigned, handleSubmit: handleEditAssigned, reset: resetEditAssigned, setValue: setEditAssignedValue } = useForm();

    const loadData = async () => {
        try {
            const [pats, loadedPlans, loadedMemberships] = await Promise.all([
                patientsApi.getAll(),
                membershipPlansApi.getAll(),
                membershipsApi.getAll()
            ]);
            setPatientsList(pats);
            setPlans(loadedPlans.filter((p: any) => p.is_active));
            setMemberships(loadedMemberships);
        } catch (error) {
            console.error("Error loading data", error);
            toast.error("Error al cargar datos");
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
            loadData();
        } catch (error) {
            console.error("Error registrando membresía", error);
            toast.error("Hubo un error al registrar la venta");
        }
    };

    const getIconForPlan = (color: string) => {
        switch (color) {
            case 'teal': return <Star className={`w-6 h-6 text-teal-500`} />;
            case 'indigo': return <ShieldCheck className={`w-6 h-6 text-indigo-500`} />;
            default: return <Activity className={`w-6 h-6 text-slate-500`} />;
        }
    };

    const handleExport = () => {
        const dataToExport = plans.map(p => ({
            ID: p.id,
            Plan: p.name,
            Precio: p.price,
            Frecuencia: p.frequency,
            Características: p.features
        }));
        exportToExcel(dataToExport, 'Planes_Membresia_Medizen');
    };

    const openCreatePlan = () => {
        setEditingPlanId(null);
        resetPlan();
        setIsPlanModalOpen(true);
    };

    const openEditPlan = (plan: any) => {
        setEditingPlanId(plan.id);
        setPlanValue('name', plan.name);
        setPlanValue('price', plan.price);
        setPlanValue('frequency', plan.frequency);
        setPlanValue('features', plan.features);
        setPlanValue('description', plan.description);
        setPlanValue('color', plan.color);
        setPlanValue('total_sessions', plan.total_sessions || 1);
        setPlanValue('is_popular', plan.is_popular);
        setIsPlanModalOpen(true);
    };

    const onSavePlan = async (data: any) => {
        try {
            const payload = { ...data, is_popular: Boolean(data.is_popular), total_sessions: parseInt(data.total_sessions) || 1 };
            if (editingPlanId) {
                await membershipPlansApi.update(editingPlanId, payload);
                toast.success("Plan actualizado");
            } else {
                await membershipPlansApi.create(payload);
                toast.success("Plan creado");
            }
            setIsPlanModalOpen(false);
            loadData();
        } catch (error) {
            console.error("Error saving plan", error);
            toast.error("Error al guardar el plan");
        }
    };

    const onDeletePlan = async (id: number) => {
        if (!confirm("¿Está seguro de eliminar este plan de membresía?")) return;
        try {
            await membershipPlansApi.delete(id);
            toast.success("Plan eliminado");
            loadData();
        } catch (error: any) {
            console.error("Error deleting plan", error);
            // Mostrar el mensaje de error del backend si existe (ej. plan en uso)
            const detail = error.response?.data?.detail || "No se pudo eliminar el plan";
            toast.error(detail);
        }
    };

    const openEditAssigned = (membership: any) => {
        setEditingAssignedId(membership.id);
        setEditAssignedValue('used_sessions', membership.used_sessions);
        setEditAssignedValue('total_sessions', membership.total_sessions);
        setEditAssignedValue('is_active', membership.is_active);
        setIsEditAssignedModalOpen(true);
    };

    const onSaveAssigned = async (data: any) => {
        try {
            const payload = {
                used_sessions: parseInt(data.used_sessions),
                total_sessions: parseInt(data.total_sessions),
                is_active: data.is_active === true || data.is_active === 'true'
            };
            await membershipsApi.update(editingAssignedId!, payload);
            toast.success("Membresía actualizada correctamente");
            setIsEditAssignedModalOpen(false);
            loadData();
        } catch (error) {
            console.error("Error updating assigned membership", error);
            toast.error("Error al actualizar la membresía");
        }
    };

    return (
        <>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Suscripciones y Membresías</h1>
                    <p className="text-slate-500 text-sm mt-1">Gestión de planes y membresías asignadas a pacientes</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleExport}
                        className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2 active:scale-95 duration-200"
                    >
                        <Download className="w-4 h-4" />
                        Exportar Excel
                    </button>
                    {activeTab === 'plans' && (
                        <button onClick={openCreatePlan} className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm active:scale-95 duration-200 flex items-center gap-2">
                            <Plus className="w-4 h-4" />
                            Nuevo Plan
                        </button>
                    )}
                    <button onClick={() => setIsVentaModalOpen(true)} className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors shadow-lg shadow-slate-900/20 active:scale-95 duration-200 flex items-center gap-2">
                        <CreditCard className="w-4 h-4" />
                        Vender Membresía
                    </button>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-slate-200 mb-8">
                <button
                    className={`pb-4 px-6 text-sm font-medium transition-colors ${activeTab === 'plans' ? 'border-b-2 border-teal-500 text-teal-600' : 'text-slate-500 hover:text-slate-700'}`}
                    onClick={() => setActiveTab('plans')}
                >
                    Modelos de Membresía
                </button>
                <button
                    className={`pb-4 px-6 text-sm font-medium transition-colors ${activeTab === 'assigned' ? 'border-b-2 border-teal-500 text-teal-600' : 'text-slate-500 hover:text-slate-700'}`}
                    onClick={() => setActiveTab('assigned')}
                >
                    Membresías Asignadas
                </button>
            </div>

            {activeTab === 'plans' ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {plans.map((plan) => {
                        const featureList = plan.features ? plan.features.split(',').map((f: string) => f.trim()) : [];
                        return (
                        <div key={plan.id} className={`relative bg-white rounded-2xl border ${plan.is_popular ? 'border-teal-500 shadow-md shadow-teal-500/10' : 'border-slate-200 shadow-sm'} p-6 flex flex-col hover:shadow-md transition-shadow`}>
                            {plan.is_popular && (
                                <div className="absolute top-0 right-6 transform -translate-y-1/2">
                                    <span className="bg-gradient-to-r from-teal-500 to-emerald-400 text-white text-[10px] font-bold uppercase tracking-wider py-1 px-3 rounded-full shadow-sm">
                                        Más Elegido
                                    </span>
                                </div>
                            )}

                            <div className="flex items-center justify-between gap-3 mb-4">
                                <div className="flex items-center gap-3">
                                    <div className={`p-3 rounded-xl bg-slate-50`}>
                                        {getIconForPlan(plan.color)}
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-800">{plan.name}</h3>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button onClick={() => openEditPlan(plan)} className="text-slate-400 hover:text-blue-500 transition-colors" title="Editar Plan">
                                        <Edit2 className="w-4 h-4" />
                                    </button>
                                    <button onClick={() => onDeletePlan(plan.id)} className="text-slate-400 hover:text-red-500 transition-colors" title="Eliminar Plan">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <div className="mb-6">
                                <span className="text-3xl font-bold text-slate-800">{plan.price}</span>
                                <span className="text-slate-500 text-sm">/{plan.frequency}</span>
                            </div>

                            <ul className="space-y-3 mb-4 flex-1">
                                {featureList.map((feature: string, i: number) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                                        <Zap className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                                        <span>{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            {plan.description && (
                                <div className="mt-auto pt-4 border-t border-slate-100 text-center italic text-slate-500 text-sm">
                                    "{plan.description}"
                                </div>
                            )}
                        </div>
                    )})}
                    {plans.length === 0 && (
                        <div className="col-span-3 text-center py-12 bg-white rounded-2xl border border-slate-200">
                            <CreditCard className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-slate-800">No hay planes creados</h3>
                            <p className="text-slate-500 mt-1">Crea tu primer plan de membresía para empezar a administrar pacientes.</p>
                            <button onClick={openCreatePlan} className="mt-4 px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors">
                                Crear Plan
                            </button>
                        </div>
                    )}
                </div>
            ) : (
                <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                    {memberships.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-medium">
                                    <tr>
                                        <th className="px-6 py-4">Paciente</th>
                                        <th className="px-6 py-4">Plan Activo</th>
                                        <th className="px-6 py-4">Sesiones Usadas</th>
                                        <th className="px-6 py-4">Estado</th>
                                        <th className="px-6 py-4 text-right">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {memberships.map((membership: any) => (
                                        <tr key={membership.id} className="hover:bg-slate-50/50 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="font-medium text-slate-800">
                                                    {membership.patient_name} {membership.patient_last_name}
                                                </div>
                                                <div className="text-xs text-slate-400 mt-1">
                                                    Inició: {new Date(membership.start_date).toLocaleDateString()}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-teal-50 text-teal-700 rounded-lg font-medium">
                                                    <Star className="w-3.5 h-3.5" />
                                                    {membership.membership_type}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden w-24">
                                                        <div
                                                            className="h-full bg-teal-500 rounded-full transition-all duration-500"
                                                            style={{ width: `${Math.min((membership.used_sessions / membership.total_sessions) * 100, 100)}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-xs font-medium text-slate-600">
                                                        {membership.used_sessions} / {membership.total_sessions}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${membership.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'}`}>
                                                    {membership.is_active ? 'Activo' : 'Inactivo'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <button
                                                    onClick={() => openEditAssigned(membership)}
                                                    className="text-slate-400 hover:text-blue-500 transition-colors"
                                                    title="Modificar Membresía"
                                                >
                                                    <Edit2 className="w-4 h-4" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="p-12 text-center flex flex-col items-center">
                            <Activity className="w-12 h-12 text-slate-300 mb-4" />
                            <h3 className="text-base font-medium text-slate-800">Sin membresías asignadas</h3>
                            <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
                                No hay pacientes con membresías activas. Utiliza el botón "Vender Membresía" para asignar planes.
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* Modal para Crear/Editar Plan */}
            {isPlanModalOpen && (
                <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-lg shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center justify-between p-6 border-b border-slate-100">
                            <h2 className="text-xl font-bold text-slate-800">{editingPlanId ? 'Editar Plan' : 'Nuevo Plan de Membresía'}</h2>
                            <button onClick={() => setIsPlanModalOpen(false)} className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-50 rounded-full transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handlePlan(onSavePlan)} className="p-6">
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Nombre del Plan</label>
                                        <input required type="text" {...regPlan("name")} placeholder="Ej: Básica" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Precio (Texto)</label>
                                        <input required type="text" {...regPlan("price")} placeholder="Ej: $45,000" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Frecuencia</label>
                                        <input required type="text" {...regPlan("frequency")} placeholder="Ej: mensual o anual" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Color/Icono Principal</label>
                                        <select {...regPlan("color")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all">
                                            <option value="slate">Gris (Activity)</option>
                                            <option value="teal">Verde (Star)</option>
                                            <option value="indigo">Índigo (ShieldCheck)</option>
                                        </select>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Beneficios / Características (3 Puntos)</label>
                                    <textarea required {...regPlan("features")} placeholder="Ej: 2 sesiones de Acupuntura, 1 sesión Cama de Cuarzo, 10% de descuento (Separados por coma)" rows={3} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"></textarea>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Nota Inferior / Descripción corta</label>
                                    <input type="text" {...regPlan("description")} placeholder="Ej: Equilibra tu energía y salud" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Sesiones Totales del Plan</label>
                                        <input required type="number" {...regPlan("total_sessions")} min="1" defaultValue="1" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                    </div>
                                    <div className="flex items-center gap-2 pt-6">
                                        <input type="checkbox" id="is_popular" {...regPlan("is_popular")} className="w-4 h-4 text-teal-600 rounded border-gray-300" />
                                        <label htmlFor="is_popular" className="text-sm font-medium text-slate-700">Marcar como "Destacado"</label>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-slate-50">
                                <button type="button" onClick={() => setIsPlanModalOpen(false)} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-xl transition-colors">Cancelar</button>
                                <button type="submit" className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl shadow-lg transition-all active:scale-95">Guardar Plan</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal Editar Membresía Asignada */}
            {isEditAssignedModalOpen && (
                <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-sm shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center justify-between p-6 border-b border-slate-100">
                            <h2 className="text-xl font-bold text-slate-800">Modificar Membresía</h2>
                            <button onClick={() => setIsEditAssignedModalOpen(false)} className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-50 rounded-full transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleEditAssigned(onSaveAssigned)} className="p-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Sesiones Usadas</label>
                                    <input required type="number" {...regEditAssigned("used_sessions")} min="0" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Sesiones Totales</label>
                                    <input required type="number" {...regEditAssigned("total_sessions")} min="1" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                </div>
                                <div className="flex items-center gap-2 pt-2">
                                    <input type="checkbox" id="is_active" {...regEditAssigned("is_active")} className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500" />
                                    <label htmlFor="is_active" className="text-sm font-medium text-slate-700">Membresía Activa</label>
                                </div>
                            </div>
                            <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-slate-50">
                                <button type="button" onClick={() => setIsEditAssignedModalOpen(false)} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-xl transition-colors">Cancelar</button>
                                <button type="submit" className="px-5 py-2.5 bg-teal-500 hover:bg-teal-600 text-white text-sm font-bold rounded-xl shadow-lg transition-all active:scale-95">Guardar Cambios</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal de Nueva Venta */}
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
                                        <select required {...regVenta("membership_type", {
                                            onChange: (e) => {
                                                const selectedPlan = plans.find(p => p.name === e.target.value);
                                                if (selectedPlan) {
                                                    setVentaValue("total_sessions", selectedPlan.total_sessions || 1);
                                                }
                                            }
                                        })} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all">
                                            <option value="">Seleccionar</option>
                                            {plans.map(p => (
                                                <option key={p.id} value={p.name}>{p.name}</option>
                                            ))}
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
