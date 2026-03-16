import React, { useState, useEffect } from 'react';
import { Calendar, Plus, X, Clock, User, ChevronLeft, ChevronRight, Search, Download, CheckCircle, Edit, Trash2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { appointmentsApi, patientsApi, Appointment } from '../services/api';
import { exportToExcel } from '../utils/exportToExcel';

export default function Appointments() {
    const [appointmentsList, setAppointmentsList] = useState<Appointment[]>([]);
    const [patientsList, setPatientsList] = useState<any[]>([]);
    const [isApptModalOpen, setIsApptModalOpen] = useState(false);
    const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false);
    const [completingTarget, setCompletingTarget] = useState<Appointment | null>(null);
    const [completeNotes, setCompleteNotes] = useState('');
    const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);
    const [selectedDate, setSelectedDate] = useState<Date>(new Date());
    const [searchQuery, setSearchQuery] = useState('');
    const { register: regAppt, handleSubmit: handleAppt, reset: resetAppt, setValue } = useForm();

    const loadData = async () => {
        try {
            const [appts, pats] = await Promise.all([
                appointmentsApi.getAll(),
                patientsApi.getAll()
            ]);
            setAppointmentsList(appts);
            setPatientsList(pats);
        } catch (error) {
            console.error("Error loading appointments/patients", error);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const onNuevaCita = async (data: any) => {
        try {
            if (editingAppointment) {
                await appointmentsApi.update(editingAppointment.id, {
                    appointment_date: data.appointment_date,
                    notes: data.notes,
                    status: data.status
                });
                toast.success("Cita actualizada correctamente");
            } else {
                await appointmentsApi.create({
                    patient_id: parseInt(data.patient_id),
                    appointment_date: data.appointment_date,
                    notes: data.notes,
                    status: 'Scheduled'
                });
                toast.success("Cita agendada correctamente");
            }
            closeModal();
            loadData();
        } catch (error) {
            console.error("Error creating/updating appointment", error);
            toast.error("Hubo un error al guardar la cita");
        }
    };

    const handleDelete = async (id: number) => {
        if (confirm("¿Estás seguro de eliminar esta cita?")) {
            try {
                await appointmentsApi.delete(id);
                toast.success("Cita eliminada correctamente");
                loadData();
            } catch (error) {
                console.error("Error deleting appointment", error);
                toast.error("Hubo un error al eliminar la cita");
            }
        }
    };

    const openEditModal = (appt: Appointment) => {
        setEditingAppointment(appt);
        setValue('patient_id', appt.patient_id);
        // format date for datetime-local input
        const d = new Date(appt.appointment_date);
        const pad = (n: number) => n.toString().padStart(2, '0');
        const formattedDate = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
        setValue('appointment_date', formattedDate);
        setValue('notes', appt.notes);
        setValue('status', appt.status);
        setIsApptModalOpen(true);
    };

    const openCreateModal = () => {
        setEditingAppointment(null);
        resetAppt();
        setIsApptModalOpen(true);
    };

    const closeModal = () => {
        setIsApptModalOpen(false);
        setEditingAppointment(null);
        resetAppt();
    };

    const openCompleteModal = (appt: Appointment) => {
        setCompletingTarget(appt);
        setCompleteNotes(appt.notes || '');
        setIsCompleteModalOpen(true);
    };

    const closeCompleteModal = () => {
        setIsCompleteModalOpen(false);
        setCompletingTarget(null);
        setCompleteNotes('');
    };

    const handleCompleteSession = async () => {
        if (!completingTarget) return;
        try {
            await appointmentsApi.complete(completingTarget.id, completeNotes);
            toast.success("Sesión completada y enviada al historial clínico");
            closeCompleteModal();
            loadData();
        } catch (error) {
            console.error("Error completing session", error);
            toast.error("Hubo un error al completar la sesión");
        }
    };

    const getPatientName = (id: number) => {
        const p = patientsList.find(pat => pat.id === id);
        return p ? `${p.first_name} ${p.last_name}` : `Paciente #${id}`;
    };

    const nextDay = () => {
        const next = new Date(selectedDate);
        next.setDate(next.getDate() + 1);
        setSelectedDate(next);
    };

    const prevDay = () => {
        const prev = new Date(selectedDate);
        prev.setDate(prev.getDate() - 1);
        setSelectedDate(prev);
    };

    const setToday = () => {
        setSelectedDate(new Date());
    };

    const isToday = selectedDate.getDate() === new Date().getDate() && selectedDate.getMonth() === new Date().getMonth() && selectedDate.getFullYear() === new Date().getFullYear();

    const handleExport = () => {
        const dataToExport = appointmentsList.map(a => ({
            ID: a.id,
            'Fecha y Hora': new Date(a.appointment_date).toLocaleString(),
            Paciente: getPatientName(a.patient_id),
            Estado: a.status,
            Notas: a.notes || ''
        }));
        exportToExcel(dataToExport, 'Citas_Medizen');
    };

    return (
        <>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Agenda Clínica</h1>
                    <p className="text-slate-500 text-sm mt-1">Gestión integral de citas y sesiones de pacientes</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleExport}
                        className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2 active:scale-95 duration-200"
                    >
                        <Download className="w-4 h-4" />
                        Exportar Excel
                    </button>
                    <button onClick={openCreateModal} className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors shadow-lg shadow-slate-900/20 active:scale-95 duration-200 flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Agendar Cita
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                        <h2 className="font-semibold text-slate-800">Todas las Citas</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse whitespace-nowrap">
                            <thead>
                                <tr className="bg-slate-50/50 text-slate-500 text-xs uppercase tracking-wider">
                                    <th className="p-4 font-medium border-b border-slate-100">Fecha y Hora</th>
                                    <th className="p-4 font-medium border-b border-slate-100">Paciente</th>
                                    <th className="p-4 font-medium border-b border-slate-100">Estado</th>
                                    <th className="p-4 font-medium border-b border-slate-100">Notas</th>
                                    <th className="p-4 font-medium border-b border-slate-100 text-right min-w-[120px]">Acciones</th>
                                </tr>
                        </thead>
                        <tbody className="text-sm divide-y divide-slate-100">
                            {appointmentsList.map((appt) => (
                                <tr key={appt.id} className="hover:bg-white hover:shadow-md transition-all hover:-translate-y-0.5 group">
                                    <td className="p-4 text-slate-800">
                                        <div className="flex items-center gap-2">
                                            <Clock className="w-4 h-4 text-teal-500" />
                                            <span className="font-medium">{new Date(appt.appointment_date).toLocaleString()}</span>
                                        </div>
                                    </td>
                                    <td className="p-4 font-medium text-slate-800">
                                        <div className="flex items-center gap-2">
                                            <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center">
                                                <User className="w-3 h-3 text-slate-500" />
                                            </div>
                                            {getPatientName(appt.patient_id)}
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <span className="bg-emerald-50 text-emerald-600 text-xs font-semibold px-2 py-1 rounded-full">{appt.status}</span>
                                    </td>
                                    <td className="p-4 text-slate-500 truncate max-w-xs">{appt.notes || '--'}</td>
                                    <td className="p-4 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            {appt.status !== 'Completed' && (
                                                <button onClick={() => openCompleteModal(appt)} title="Completar cita" className="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors">
                                                    <CheckCircle className="w-4 h-4" />
                                                </button>
                                            )}
                                            <button onClick={() => openEditModal(appt)} title="Modificar cita" className="p-1.5 text-teal-600 hover:bg-teal-50 rounded-lg transition-colors">
                                                <Edit className="w-4 h-4" />
                                            </button>
                                            <button onClick={() => handleDelete(appt.id)} title="Eliminar cita" className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                            {appointmentsList.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="p-8 text-center text-slate-500">
                                        No hay citas programadas.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                    </div>
                </div>

                {/* Today's Schedule Sidebar */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 flex flex-col h-[600px]">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="font-semibold text-slate-800 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-teal-500" />
                            {isToday ? 'Agenda de Hoy' : selectedDate.toLocaleDateString()}
                        </h2>
                        <div className="flex items-center gap-1">
                            <button onClick={prevDay} className="p-1 text-slate-400 hover:bg-slate-50 hover:text-slate-600 rounded">
                                <ChevronLeft className="w-4 h-4" />
                            </button>
                            <button onClick={setToday} className="text-[10px] uppercase font-bold text-teal-600 px-2 py-1 hover:bg-teal-50 rounded">Hoy</button>
                            <button onClick={nextDay} className="p-1 text-slate-400 hover:bg-slate-50 hover:text-slate-600 rounded">
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <div className="relative mb-4">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Buscar paciente..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 text-slate-800 transition-all"
                        />
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2 space-y-4 pt-2">
                        {appointmentsList
                            .filter(a => {
                                const d = new Date(a.appointment_date);
                                const dateMatch = d.getDate() === selectedDate.getDate() && d.getMonth() === selectedDate.getMonth() && d.getFullYear() === selectedDate.getFullYear();
                                const patientName = getPatientName(a.patient_id).toLowerCase();
                                const searchMatch = patientName.includes(searchQuery.toLowerCase());
                                return dateMatch && searchMatch;
                            })
                            .sort((a, b) => new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime())
                            .map((appt) => {
                                const t = new Date(appt.appointment_date);
                                const isPast = t.getTime() < new Date().getTime() && isToday;
                                return (
                                    <div key={appt.id} className={`p-4 rounded-xl border ${isPast ? 'bg-slate-50 border-slate-100 opacity-70' : 'bg-white border-slate-200 shadow-sm border-l-4 border-l-teal-500'}`}>
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="font-bold text-slate-700">{t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                            <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full ${appt.status === 'Completed' ? 'bg-emerald-100 text-emerald-700' : isPast ? 'bg-slate-200 text-slate-600' : 'bg-teal-50 text-teal-600'}`}>
                                                {appt.status}
                                            </span>
                                        </div>
                                        <div className="text-sm font-medium text-slate-800">{getPatientName(appt.patient_id)}</div>
                                        {appt.notes && <div className="text-xs text-slate-500 mt-1 line-clamp-2">{appt.notes}</div>}
                                    </div>
                                );
                            })
                        }
                        {appointmentsList.filter(a => {
                            const d = new Date(a.appointment_date);
                            const dateMatch = d.getDate() === selectedDate.getDate() && d.getMonth() === selectedDate.getMonth() && d.getFullYear() === selectedDate.getFullYear();
                            const patientName = getPatientName(a.patient_id).toLowerCase();
                            return dateMatch && patientName.includes(searchQuery.toLowerCase());
                        }).length === 0 && (
                                <div className="text-center text-slate-500 text-sm mt-10">
                                    No hay citas programadas para este día.
                                </div>
                            )}
                    </div>
                </div>
            </div>

            {/* Modal Nueva Cita */}
            {isApptModalOpen && (
                <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-md shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center justify-between p-6 border-b border-slate-100">
                            <h2 className="text-xl font-bold text-slate-800">{editingAppointment ? 'Modificar Cita' : 'Agendar Cita'}</h2>
                            <button onClick={closeModal} className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-50 rounded-full transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleAppt(onNuevaCita)} className="p-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Paciente</label>
                                    <select required {...regAppt("patient_id")} disabled={!!editingAppointment} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all disabled:opacity-50">
                                        <option value="">Seleccione un paciente</option>
                                        {patientsList.map(p => (
                                            <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Fecha y Hora</label>
                                    <input required type="datetime-local" {...regAppt("appointment_date")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                </div>
                                {editingAppointment && (
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Estado</label>
                                        <select {...regAppt("status")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all">
                                            <option value="Scheduled">Scheduled</option>
                                            <option value="Completed">Completed</option>
                                            <option value="Cancelled">Cancelled</option>
                                        </select>
                                    </div>
                                )}
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Notas / Motivo de Consulta</label>
                                    <textarea {...regAppt("notes")} rows={3} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"></textarea>
                                </div>
                            </div>
                            <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-slate-50">
                                <button type="button" onClick={closeModal} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-xl transition-colors">Cancelar</button>
                                <button type="submit" className="px-5 py-2.5 bg-teal-500 hover:bg-teal-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-teal-500/20 transition-all active:scale-95">Guardar Cita</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal Completar Sesión */}
            {isCompleteModalOpen && completingTarget && (
                <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-md shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center justify-between p-6 border-b border-slate-100">
                            <h2 className="text-xl font-bold text-slate-800">Completar Sesión</h2>
                            <button onClick={closeCompleteModal} className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-50 rounded-full transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-6">
                            <p className="text-sm text-slate-500 mb-4">
                                Estás completando la cita con <span className="font-bold text-slate-700">{getPatientName(completingTarget.patient_id)}</span>.
                                La acción registrará la información en el Historial Clínico y descontará una sesión si hay una membresía activa.
                            </p>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Notas Clínicas</label>
                            <textarea
                                value={completeNotes}
                                onChange={(e) => setCompleteNotes(e.target.value)}
                                placeholder="Escribe aquí las observaciones de la sesión..."
                                rows={4}
                                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
                            />
                            <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-slate-50">
                                <button type="button" onClick={closeCompleteModal} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-xl transition-colors">Cancelar</button>
                                <button type="button" onClick={handleCompleteSession} className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition-all active:scale-95">Completar Sesión</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
