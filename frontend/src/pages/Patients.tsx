import React, { useEffect, useState } from 'react';
import { UserPlus, Search, SearchSlash, AlertCircle, Download } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { patientsApi, Patient } from '../services/api';
import { exportToExcel } from '../utils/exportToExcel';

type PatientFormData = Omit<Patient, 'id' | 'created_at' | 'is_active'>;

export default function Patients() {
    const [patients, setPatients] = useState<Patient[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    const { register, handleSubmit, reset, formState: { errors } } = useForm<PatientFormData>();

    useEffect(() => {
        fetchPatients();
    }, []);

    const fetchPatients = async () => {
        try {
            setIsLoading(true);
            const data = await patientsApi.getAll();
            setPatients(data);
        } catch (error) {
            console.error("Error fetching patients", error);
        } finally {
            setIsLoading(false);
        }
    };

    const filteredPatients = patients.filter(p =>
        (p.first_name + ' ' + p.last_name).toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleExport = () => {
        const dataToExport = filteredPatients.map(p => ({
            ID: p.id,
            Nombre: p.first_name,
            Apellido: p.last_name,
            Email: p.email,
            Teléfono: p.phone || '',
            'Fecha Nacimiento': p.date_of_birth || '',
            'Fecha Registro': new Date(p.created_at).toLocaleDateString(),
            Estado: p.is_active ? 'Activo' : 'Inactivo'
        }));
        exportToExcel(dataToExport, 'Pacientes_Medizen');
    };

    return (
        <>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Gestión de Pacientes</h1>
                    <p className="text-slate-500 text-sm mt-1">Directorio e historial clínico integrativo</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleExport}
                        className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2 active:scale-95 duration-200"
                    >
                        <Download className="w-4 h-4" />
                        Exportar Excel
                    </button>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="px-4 py-2 bg-teal-600 outline-none text-white text-sm font-medium rounded-lg hover:bg-teal-700 transition-colors shadow-lg shadow-teal-600/20 flex items-center gap-2 active:scale-95 duration-200"
                    >
                        <UserPlus className="w-4 h-4" />
                        Registrar Paciente
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                    <div className="relative w-72">
                        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                        <input
                            type="text"
                            placeholder="Buscar por nombre o email..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-teal-500/50 outline-none transition-all"
                        />
                    </div>
                </div>

                {/* Patients Table */}
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-50/50 text-slate-500 text-xs uppercase tracking-wider">
                                <th className="p-4 font-medium border-b border-slate-100">Paciente</th>
                                <th className="p-4 font-medium border-b border-slate-100">Contacto</th>
                                <th className="p-4 font-medium border-b border-slate-100">Fecha de Alta</th>
                                <th className="p-4 font-medium border-b border-slate-100">Estado</th>
                                <th className="p-4 font-medium border-b border-slate-100 text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm divide-y divide-slate-100">
                            {isLoading ? (
                                <tr>
                                    <td colSpan={5} className="p-8 text-center text-slate-500">Cargando pacientes...</td>
                                </tr>
                            ) : patients.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="p-8 text-center text-slate-500 flex flex-col items-center justify-center">
                                        <SearchSlash className="w-8 h-8 text-slate-300 mb-2" />
                                        No se encontraron pacientes
                                    </td>
                                </tr>
                            ) : (
                                filteredPatients.map((patient) => (
                                    <tr key={patient.id} className="hover:bg-white hover:shadow-md transition-all hover:-translate-y-0.5 group">
                                        <td className="p-4 font-medium text-slate-800">
                                            {patient.first_name} {patient.last_name}
                                        </td>
                                        <td className="p-4 text-slate-500">{patient.email}</td>
                                        <td className="p-4 text-slate-500">{new Date(patient.created_at).toLocaleDateString()}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${patient.is_active ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'}`}>
                                                {patient.is_active ? 'Activo' : 'Inactivo'}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right">
                                            <Link to={`/patients/${patient.id}`} className="text-teal-600 font-medium hover:text-teal-700 text-sm">Ver Perfil</Link>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Form Modal for new patient */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                            <h2 className="text-lg font-bold text-slate-800">Registrar Nuevo Paciente</h2>
                            <button
                                onClick={() => { setIsModalOpen(false); reset(); }}
                                className="text-slate-400 hover:text-slate-600 transition-colors"
                                disabled={isSubmitting}
                            >
                                ✕
                            </button>
                        </div>

                        <form onSubmit={handleSubmit(async (data) => {
                            try {
                                setIsSubmitting(true);
                                const payload = { ...data };
                                if (!payload.phone) delete payload.phone;
                                if (!payload.date_of_birth) delete payload.date_of_birth;

                                await patientsApi.create(payload);
                                toast.success("Paciente registrado exitosamente");
                                setIsModalOpen(false);
                                reset();
                                fetchPatients();
                            } catch (error: any) {
                                console.error("Error creating patient", error);
                                toast.error("Error al registrar: " + (error.response?.data?.detail || "Datos inválidos"));
                            } finally {
                                setIsSubmitting(false);
                            }
                        })}>
                            <div className="p-6 space-y-4 text-sm">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-slate-700 font-medium mb-1">Nombre</label>
                                        <input
                                            {...register("first_name", { required: "El nombre es obligatorio" })}
                                            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-teal-500/50"
                                            placeholder="Juan"
                                        />
                                        {errors.first_name && <p className="text-xs text-rose-500 mt-1">{errors.first_name.message}</p>}
                                    </div>
                                    <div>
                                        <label className="block text-slate-700 font-medium mb-1">Apellido</label>
                                        <input
                                            {...register("last_name", { required: "El apellido es obligatorio" })}
                                            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-teal-500/50"
                                            placeholder="Pérez"
                                        />
                                        {errors.last_name && <p className="text-xs text-rose-500 mt-1">{errors.last_name.message}</p>}
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-slate-700 font-medium mb-1">Correo Electrónico</label>
                                    <input
                                        type="email"
                                        {...register("email", { required: "El correo es obligatorio", pattern: { value: /^\S+@\S+$/i, message: "Correo inválido" } })}
                                        className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-teal-500/50"
                                        placeholder="juan.perez@email.com"
                                    />
                                    {errors.email && <p className="text-xs text-rose-500 mt-1">{errors.email.message}</p>}
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-slate-700 font-medium mb-1">Teléfono</label>
                                        <input
                                            {...register("phone")}
                                            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-teal-500/50"
                                            placeholder="+56 9 1234 5678"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-slate-700 font-medium mb-1">Fecha de Nacimiento</label>
                                        <input
                                            type="date"
                                            {...register("date_of_birth")}
                                            className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-teal-500/50 text-slate-600"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
                                <button
                                    type="button"
                                    onClick={() => { setIsModalOpen(false); reset(); }}
                                    className="px-4 py-2 bg-white text-slate-700 border border-slate-200 rounded-lg font-medium hover:bg-slate-50 transition-colors"
                                    disabled={isSubmitting}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-teal-600 text-white rounded-lg font-medium shadow-md shadow-teal-600/20 hover:bg-teal-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? 'Guardando...' : 'Guardar Paciente'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
