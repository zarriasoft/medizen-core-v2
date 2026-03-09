import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Plus, Activity, CreditCard } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { patientsApi, Patient, IeimRecord, membershipsApi } from '../services/api';

type IeimFormData = Omit<IeimRecord, 'id' | 'patient_id' | 'record_date' | 'overall_score'>;

export default function PatientDetail() {
    const { id } = useParams<{ id: string }>();
    const patientId = Number(id);

    const [patient, setPatient] = useState<Patient | null>(null);
    const [ieimRecords, setIeimRecords] = useState<IeimRecord[]>([]);
    const [memberships, setMemberships] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Membership Edit Modal State
    const [isEditingMembership, setIsEditingMembership] = useState(false);
    const [editingMembershipData, setEditingMembershipData] = useState<any>(null);
    const { register: regMem, handleSubmit: handleMemSubmit, reset: resetMem, setValue: setMemValue } = useForm();

    const { register, handleSubmit, reset, formState: { errors } } = useForm<IeimFormData>();

    useEffect(() => {
        if (patientId) {
            fetchData();
        }
    }, [patientId]);

    const fetchData = async () => {
        try {
            setIsLoading(true);
            const [patientData, recordsData, membershipsData] = await Promise.all([
                patientsApi.getOne(patientId),
                patientsApi.getIeimRecords(patientId),
                membershipsApi.getPatientMemberships(patientId)
            ]);
            setPatient(patientData);
            setIeimRecords(recordsData.sort((a, b) => new Date(a.record_date).getTime() - new Date(b.record_date).getTime()));
            setMemberships(membershipsData);
        } catch (error) {
            console.error("Error fetching patient details", error);
        } finally {
            setIsLoading(false);
        }
    };

    const openEditMembership = (membership: any) => {
        setEditingMembershipData(membership);
        setMemValue('membership_type', membership.membership_type);
        setMemValue('total_sessions', membership.total_sessions);
        setMemValue('used_sessions', membership.used_sessions);
        setMemValue('is_active', membership.is_active);
        // format dates
        if (membership.end_date) {
            const ed = new Date(membership.end_date);
            setMemValue('end_date', ed.toISOString().split('T')[0]);
        }
        setIsEditingMembership(true);
    };

    const handleDeleteMembership = async (id: number) => {
        if (window.confirm('¿Está seguro de querer eliminar esta membresía?')) {
            try {
                await membershipsApi.delete(id);
                toast.success('Membresía eliminada correctamente');
                fetchData();
            } catch (error) {
                console.error("Error deleting membership", error);
                toast.error('Hubo un error al eliminar');
            }
        }
    };

    const onEditMembershipSubmit = async (data: any) => {
        if (!editingMembershipData) return;
        try {
            const payload = {
                ...data,
                total_sessions: parseInt(data.total_sessions),
                used_sessions: parseInt(data.used_sessions),
                // is_active might come as string boolean from form depending on input type
                is_active: data.is_active === true || data.is_active === "true",
            };
            await membershipsApi.update(editingMembershipData.id, payload);
            toast.success("Membresía actualizada");
            setIsEditingMembership(false);
            setEditingMembershipData(null);
            fetchData();
        } catch (error) {
            console.error("Error updating membership", error);
            toast.error("Error al actualizar la membresía");
        }
    };

    const chartData = ieimRecords.map(r => ({
        name: new Date(r.record_date).toLocaleDateString(undefined, { day: '2-digit', month: 'short' }),
        score: r.overall_score
    }));

    if (isLoading) {
        return <div className="p-8 text-center text-slate-500">Cargando perfil...</div>;
    }

    if (!patient) {
        return <div className="p-8 text-center text-rose-500">Paciente no encontrado</div>;
    }

    return (
        <>
            <div className="mb-6">
                <Link to="/patients" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-teal-600 mb-4 transition-colors">
                    <ArrowLeft className="w-4 h-4 mr-1" />
                    Volver a Pacientes
                </Link>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">{patient.first_name} {patient.last_name}</h1>
                        <p className="text-slate-500 text-sm mt-1">{patient.email} {patient.phone && `• ${patient.phone}`}</p>
                    </div>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="px-4 py-2 bg-teal-600 text-white text-sm font-medium rounded-lg hover:bg-teal-700 transition-colors shadow-lg shadow-teal-600/20 flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Nuevo Registro IEIM
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Evolution Chart */}
                <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-teal-600" />
                            Evolución IEIM
                        </h2>
                        <div className="text-2xl font-bold tracking-tight text-teal-600">
                            {ieimRecords.length > 0 ? ieimRecords[ieimRecords.length - 1].overall_score.toFixed(1) : '-'} <span className="text-sm font-normal text-slate-400">/ 10</span>
                        </div>
                    </div>

                    <div className="h-64 w-full">
                        {ieimRecords.length === 0 ? (
                            <div className="h-full flex items-center justify-center text-slate-400 text-sm border-2 border-dashed border-slate-100 rounded-xl">
                                No hay registros IEIM para visualizar
                            </div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData}>
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
                        )}
                    </div>
                </div>

                {/* Action Panel / Specific Info */}
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                    <h2 className="text-lg font-semibold text-slate-800 mb-4">Resumen de Variables</h2>
                    {ieimRecords.length === 0 ? (
                        <p className="text-sm text-slate-500">Añade un registro para ver el desglose.</p>
                    ) : (
                        <div className="space-y-4 text-sm mt-6">
                            {(() => {
                                const last = ieimRecords[ieimRecords.length - 1];
                                const metrics = [
                                    { label: 'Energía', val: last.energy_level },
                                    { label: 'Sueño', val: last.sleep_quality },
                                    { label: 'Estrés/Ansiedad', val: last.stress_anxiety, invert: true },
                                    { label: 'Dolor', val: last.pain_level, invert: true },
                                    { label: 'Movilidad', val: last.mobility },
                                    { label: 'Inflamación', val: last.inflammation, invert: true }
                                ];
                                return metrics.map((m, i) => (
                                    <div key={i}>
                                        <div className="flex justify-between mb-1">
                                            <span className="text-slate-600">{m.label}</span>
                                            <span className="font-medium text-slate-800">{m.val} / 10</span>
                                        </div>
                                        <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${m.invert ? (m.val > 6 ? 'bg-rose-500' : m.val > 3 ? 'bg-amber-500' : 'bg-emerald-500') : (m.val > 6 ? 'bg-emerald-500' : m.val > 3 ? 'bg-amber-500' : 'bg-rose-500')}`}
                                                style={{ width: `${(m.val / 10) * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                ));
                            })()}
                        </div>
                    )}
                </div>
            </div>

            {/* Active Memberships Section */}
            <div className="mt-6 bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                        <CreditCard className="w-5 h-5 text-teal-600" />
                        Membresías Activas
                    </h2>
                </div>
                {memberships.length === 0 ? (
                    <div className="text-center py-6 text-slate-500 text-sm border-2 border-dashed border-slate-100 rounded-xl">
                        Este paciente no cuenta con membresías o programas activos.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {memberships.map((membership) => (
                            <div key={membership.id} className="border border-slate-200 rounded-xl p-4 flex flex-col">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-semibold text-slate-800">{membership.membership_type}</h3>
                                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${membership.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                                        }`}>
                                        {membership.is_active ? 'Activa' : 'Inactiva'}
                                    </span>
                                </div>
                                <div className="mb-4">
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-slate-500">Sesiones Dispo.</span>
                                        <span className="font-medium text-slate-800">
                                            {membership.total_sessions - membership.used_sessions} / {membership.total_sessions}
                                        </span>
                                    </div>
                                    <div className="w-full bg-slate-100 rounded-full h-1.5">
                                        <div
                                            className="bg-teal-500 h-1.5 rounded-full"
                                            style={{ width: `${Math.min(100, Math.max(0, ((membership.total_sessions - membership.used_sessions) / membership.total_sessions) * 100))}%` }}
                                        ></div>
                                    </div>
                                </div>
                                <div className="text-xs text-slate-500 mt-auto flex items-center justify-between">
                                    <span>Adquirida: {new Date(membership.start_date).toLocaleDateString()}</span>
                                    <div className="flex gap-2">
                                        <button onClick={() => openEditMembership(membership)} className="text-teal-600 hover:text-teal-700 font-medium">Editar</button>
                                        <button onClick={() => handleDeleteMembership(membership.id)} className="text-rose-500 hover:text-rose-600 font-medium">Borrar</button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* IEIM Modal Form */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                            <h2 className="text-lg font-bold text-slate-800">Cuestionario IEIM</h2>
                            <button
                                onClick={() => { setIsModalOpen(false); reset(); }}
                                className="text-slate-400 hover:text-slate-600 transition-colors"
                            >
                                ✕
                            </button>
                        </div>

                        <form onSubmit={handleSubmit(async (data) => {
                            try {
                                setIsSubmitting(true);
                                await patientsApi.addIeimRecord(patientId, data);
                                toast.success("Registro IEIM guardado");
                                setIsModalOpen(false);
                                reset();
                                fetchData();
                            } catch (error) {
                                console.error("Error creating record", error);
                                toast.error("Error al guardar registro IEIM");
                            } finally {
                                setIsSubmitting(false);
                            }
                        })}>
                            <div className="p-6 space-y-6 text-sm max-h-[60vh] overflow-y-auto">
                                <p className="text-slate-500 mb-4">Evalúa del 1 al 10 el estado actual del paciente en los siguientes aspectos:</p>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {[
                                        { key: "pain_level", label: "Nivel de Dolor", help: "1: Sin dolor, 10: Dolor extremo" },
                                        { key: "sleep_quality", label: "Calidad de Sueño", help: "1: Muy mala, 10: Excelente" },
                                        { key: "energy_level", label: "Nivel de Energía", help: "1: Muy baja, 10: Muy alta" },
                                        { key: "stress_anxiety", label: "Nivel de Estrés/Ansiedad", help: "1: Relajado, 10: Muy ansioso/estresado" },
                                        { key: "mobility", label: "Movilidad", help: "1: Muy reducida, 10: Excelente/Normal" },
                                        { key: "inflammation", label: "Signos de Inflamación", help: "1: Sin signos, 10: Alta inflamación local/sistémica" }
                                    ].map(({ key, label, help }) => (
                                        <div key={key}>
                                            <label className="block text-slate-800 font-medium mb-1">{label}</label>
                                            <p className="text-xs text-slate-500 mb-2">{help}</p>
                                            <input
                                                type="number"
                                                min="1" max="10"
                                                {...register(key as keyof IeimFormData, {
                                                    required: "Requerido",
                                                    valueAsNumber: true,
                                                    min: { value: 1, message: "Min 1" },
                                                    max: { value: 10, message: "Max 10" }
                                                })}
                                                className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-teal-500/50"
                                            />
                                            {errors[key as keyof IeimFormData] && <p className="text-xs text-rose-500 mt-1">{errors[key as keyof IeimFormData]?.message}</p>}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
                                <button
                                    type="button"
                                    onClick={() => { setIsModalOpen(false); reset(); }}
                                    className="px-4 py-2 bg-white text-slate-700 border border-slate-200 rounded-lg font-medium hover:bg-slate-50 transition-colors"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-teal-600 text-white rounded-lg font-medium shadow-md shadow-teal-600/20 hover:bg-teal-700 transition-colors disabled:opacity-50"
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? 'Guardando...' : 'Guardar IEIM'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
            {/* Modal Editar Membresía */}
            {isEditingMembership && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                            <h2 className="text-lg font-bold text-slate-800">Editar Membresía</h2>
                            <button
                                type="button"
                                onClick={() => { setIsEditingMembership(false); resetMem(); }}
                                className="text-slate-400 hover:text-slate-600 transition-colors"
                            >
                                ✕
                            </button>
                        </div>
                        <form onSubmit={handleMemSubmit(onEditMembershipSubmit)} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Tipo de Plan</label>
                                <select {...regMem("membership_type")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-teal-500/50">
                                    <option value="Básica">Básica</option>
                                    <option value="Integrativa">Integrativa</option>
                                    <option value="Premium Care">Premium Care</option>
                                </select>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Sesiones Totales</label>
                                    <input type="number" {...regMem("total_sessions")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-teal-500/50" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Sesiones Usadas</label>
                                    <input type="number" {...regMem("used_sessions")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-teal-500/50" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Fecha Término</label>
                                <input type="date" {...regMem("end_date")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-teal-500/50" />
                            </div>
                            <div className="flex items-center gap-2 mt-4">
                                <input type="checkbox" id="is_active" {...regMem("is_active")} className="w-4 h-4 text-teal-600 rounded border-gray-300 focus:ring-teal-500" />
                                <label htmlFor="is_active" className="text-sm text-slate-700 font-medium">Membresía Activa</label>
                            </div>
                            <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-slate-50">
                                <button type="button" onClick={() => { setIsEditingMembership(false); resetMem(); }} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-xl transition-colors">Cancelar</button>
                                <button type="submit" className="px-5 py-2.5 bg-teal-500 hover:bg-teal-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-teal-500/20 transition-all active:scale-95">Guardar Cambios</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
