import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { patientApi } from '../services/api';
import { Calendar, Clock, CheckCircle, LogOut, User } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Portal() {
    const { patient, logout } = useAuth();
    const [appointments, setAppointments] = useState<any[]>([]);
    const [memberships, setMemberships] = useState<any[]>([]);
    const [availability, setAvailability] = useState<any[]>([]);
    const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
    const [selectedMembershipId, setSelectedMembershipId] = useState<number | ''>('');
    const [isBooking, setIsBooking] = useState(false);
    const [bookingError, setBookingError] = useState('');
    const [bookingSuccess, setBookingSuccess] = useState(false);

    useEffect(() => {
        loadDashboardData();
    }, []);

    useEffect(() => {
        if (selectedDate) {
            loadAvailability(selectedDate);
        }
    }, [selectedDate]);

    const loadDashboardData = async () => {
        try {
            const [apptsRes, memsRes] = await Promise.all([
                patientApi.getAppointments(),
                patientApi.getMemberships()
            ]);
            setAppointments(apptsRes.data);
            setMemberships(memsRes.data);
            
            // Auto-select first active membership
            const activeMems = memsRes.data.filter((m: any) => m.is_active && m.used_sessions < m.total_sessions);
            if (activeMems.length > 0) {
                setSelectedMembershipId(activeMems[0].id);
            }
        } catch (error) {
            console.error("Error loading dashboard data", error);
        }
    };

    const loadAvailability = async (date: string) => {
        try {
            const res = await patientApi.getAvailability(date);
            // The backend returns a direct array of TimeSlot objects
            setAvailability(Array.isArray(res.data) ? res.data : (res.data.available_slots || []));
        } catch (error) {
            console.error("Error loading availability", error);
            setAvailability([]);
        }
    };

    const handleBook = async (timeSlot: string) => {
        setIsBooking(true);
        setBookingError('');
        setBookingSuccess(false);
        try {
            const dateTime = `${selectedDate}T${timeSlot}`;
            await patientApi.bookAppointment({ 
                appointment_date: dateTime,
                membership_id: selectedMembershipId !== '' ? selectedMembershipId : undefined
            });
            setBookingSuccess(true);
            loadDashboardData();
            loadAvailability(selectedDate);
        } catch (error: any) {
            setBookingError(error.response?.data?.detail || 'Error al agendar la cita.');
        } finally {
            setIsBooking(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-800">
            {/* Header */}
            <header className="bg-brand-dark text-white py-4 px-6 flex justify-between items-center shadow-md">
                <div className="flex items-center gap-3">
                    <User className="w-6 h-6 text-amber-400" />
                    <div>
                        <h1 className="text-xl font-serif">Mi Portal MediZen</h1>
                        <p className="text-xs text-emerald-100/80">Bienvenido, {patient?.first_name}</p>
                    </div>
                </div>
                <button 
                    onClick={logout}
                    className="flex items-center gap-2 text-sm bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
                >
                    <LogOut className="w-4 h-4" />
                    Cerrar Sesión
                </button>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                {/* Left Column: Profile & Dashboard */}
                <div className="lg:col-span-1 space-y-8">
                    {/* Memberships */}
                    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                        <h2 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-3 mb-4 flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-emerald-500" />
                            Mis Membresías Activas
                        </h2>
                        {memberships.length === 0 ? (
                            <p className="text-sm text-slate-500 italic">No tienes membresías activas.</p>
                        ) : (
                            <div className="space-y-3">
                                {memberships.map((m: any) => (
                                    <div key={m.id} className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl">
                                        <div className="font-bold text-emerald-900">{m.plan?.name || m.membership_type || 'Membresía'}</div>
                                        <div className="text-xs text-emerald-700 mt-1">
                                            Sesiones restantes en este ciclo: <span className="font-bold text-lg">{m.sessions_remaining}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>

                    {/* Upcoming Appointments */}
                    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                        <h2 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-3 mb-4 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-amber-500" />
                            Mis Próximas Citas
                        </h2>
                        {appointments.filter(a => new Date(a.appointment_date) >= new Date() && a.status !== 'cancelled').length === 0 ? (
                            <p className="text-sm text-slate-500 italic">No tienes citas programadas.</p>
                        ) : (
                            <div className="space-y-3">
                                {appointments
                                    .filter(a => new Date(a.appointment_date) >= new Date() && a.status !== 'cancelled')
                                    .map((a: any) => (
                                    <div key={a.id} className="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-100">
                                        <div>
                                            <div className="font-bold text-slate-700">
                                                {new Date(a.appointment_date).toLocaleDateString('es-CL', { weekday: 'short', month: 'short', day: 'numeric' })}
                                            </div>
                                            <div className="text-sm text-slate-500">
                                                {new Date(a.appointment_date).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })}
                                            </div>
                                            <div className="text-xs text-brand-dark mt-1 px-2 py-0.5 bg-emerald-100 rounded-full inline-block">
                                                {a.status === 'scheduled' ? 'Confirmada' : a.status}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                </div>

                {/* Right Column: Calendar & Booking */}
                <div className="lg:col-span-2">
                    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 h-full">
                        <h2 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-3 mb-6 flex items-center gap-2">
                            <Calendar className="w-5 h-5 text-blue-500" />
                            Agendar Nueva Cita
                        </h2>
                        
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-slate-700 mb-2">Selecciona la Fecha:</label>
                            <input 
                                type="date" 
                                min={new Date().toISOString().split('T')[0]}
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                className="w-full md:w-auto px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                            />
                        </div>

                        {bookingSuccess && (
                            <motion.div initial={{opacity:0}} animate={{opacity:1}} className="mb-6 p-4 bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-100 flex items-start gap-3">
                                <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
                                <div>
                                    <h4 className="font-bold">¡Cita agendada con éxito!</h4>
                                    <p className="text-sm">Te hemos enviado un correo de confirmación. Te esperamos en el centro.</p>
                                </div>
                            </motion.div>
                        )}

                        {bookingError && (
                            <div className="mb-6 p-3 bg-red-50 text-red-600 rounded-lg text-sm border border-red-100">
                                {bookingError}
                            </div>
                        )}

                        <div>
                            <div className="flex flex-col mb-4">
                                <h3 className="text-sm font-medium text-slate-700 mb-2">Membresía a utilizar:</h3>
                                {memberships.filter((m: any) => m.is_active && m.used_sessions < m.total_sessions).length === 0 ? (
                                    <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded border border-amber-200">
                                        No tienes membresías activas con saldo. Puedes agendar igual, pero deberás gestionar el pago en clínica.
                                    </p>
                                ) : (
                                    <select 
                                        value={selectedMembershipId}
                                        onChange={(e) => setSelectedMembershipId(Number(e.target.value))}
                                        className="w-full md:w-auto px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500/20"
                                    >
                                        {memberships.filter((m: any) => m.is_active && m.used_sessions < m.total_sessions).map((m: any) => (
                                            <option key={m.id} value={m.id}>
                                                {m.plan?.name || m.membership_type} (Quedan {m.total_sessions - m.used_sessions} sesiones)
                                            </option>
                                        ))}
                                    </select>
                                )}
                                <p className="text-xs text-slate-500 mt-2">
                                    Nota: La sesión se descontará de la membresía seleccionada una vez que la cita sea completada en clínica.
                                </p>
                            </div>
                            <h3 className="text-sm font-medium text-slate-700 mb-2">Horarios Disponibles:</h3>
                            {availability.length === 0 ? (
                                <div className="text-center py-8 bg-slate-50 rounded-xl border border-slate-100 border-dashed">
                                    <p className="text-slate-500">No hay horarios disponibles para esta fecha.</p>
                                    <p className="text-xs text-slate-400 mt-1">Intenta seleccionando un día diferente.</p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                                    {availability
                                        .filter((slot: any) => slot.is_available !== false)
                                        .map((slot: any, idx) => {
                                            const timeStr = typeof slot === 'string' ? slot : slot.start_time;
                                            return (
                                                <button
                                                    key={idx}
                                                    onClick={() => handleBook(timeStr)}
                                                    disabled={isBooking}
                                                    className="py-2 px-3 text-sm font-medium rounded-lg border border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:border-emerald-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                >
                                                    {timeStr ? timeStr.substring(0, 5) : ''}
                                                </button>
                                            );
                                        })}
                                </div>
                            )}
                        </div>
                    </section>
                </div>

            </main>
        </div>
    );
}
