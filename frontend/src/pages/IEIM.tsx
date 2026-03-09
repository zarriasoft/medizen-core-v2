import React, { useState, useEffect } from 'react';
import { Brain, Search, TrendingUp, AlertCircle, X, Activity, Plus, Download } from 'lucide-react';
import { patientsApi } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';
import { exportToExcel } from '../utils/exportToExcel';

export default function IEIM() {
    const [patientsList, setPatientsList] = useState<any[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPatient, setSelectedPatient] = useState<any | null>(null);
    const [isAddingRecord, setIsAddingRecord] = useState(false);
    const [selectedPatientForAdd, setSelectedPatientForAdd] = useState<string>('');
    const [newRecordData, setNewRecordData] = useState({
        pain_level: 0,
        sleep_quality: 0,
        energy_level: 0,
        stress_anxiety: 0,
        mobility: 0,
        inflammation: 0
    });

    const loadPatients = async () => {
        try {
            const data = await patientsApi.getAll();
            setPatientsList(data);
        } catch (error) {
            console.error("Error loading patients", error);
        }
    };

    useEffect(() => {
        loadPatients();
    }, []);

    const filteredPatients = patientsList.filter(p =>
        (p.first_name + ' ' + p.last_name).toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getPatientIeimStats = (patient: any) => {
        if (!patient.ieim_records || patient.ieim_records.length === 0) {
            return { score: null, trendIsUp: true, trendValue: 0, lastEvalDate: null, lastEvalRecord: null };
        }

        // Sort by date descending
        const sorted = [...patient.ieim_records].sort((a, b) => new Date(b.record_date).getTime() - new Date(a.record_date).getTime());
        const latest = sorted[0];
        const previous = sorted.length > 1 ? sorted[1] : null;

        const score = Math.round(latest.overall_score);
        let trendValue = 0;
        let trendIsUp = true;

        if (previous) {
            trendValue = Math.round(score - previous.overall_score);
            trendIsUp = trendValue >= 0;
        }

        return { score, trendIsUp, trendValue: Math.abs(trendValue), lastEvalDate: new Date(latest.record_date), lastEvalRecord: latest };
    };

    const getDaysAgo = (date: Date) => {
        const diffTime = Math.abs(new Date().getTime() - date.getTime());
        return Math.floor(diffTime / (1000 * 60 * 60 * 24));
    };

    // Calculate global stats
    const patientsWithRecords = patientsList.map(p => getPatientIeimStats(p)).filter(stats => stats.score !== null);
    const globalAverage = patientsWithRecords.length > 0
        ? patientsWithRecords.reduce((acc, curr) => acc + (curr.score || 0), 0) / patientsWithRecords.length
        : 0;

    const metasAlcanzadasCount = patientsWithRecords.filter(s => (s.score || 0) >= 80).length;
    const metasAlcanzadasPercent = patientsWithRecords.length > 0
        ? Math.round((metasAlcanzadasCount / patientsWithRecords.length) * 100)
        : 0;

    const criticalCareCount = patientsWithRecords.filter(s => (s.score || 0) < 50).length;

    const handleAddRecord = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedPatientForAdd) {
            toast.error("Por favor selecciona un paciente.");
            return;
        }

        try {
            await patientsApi.addIeimRecord(parseInt(selectedPatientForAdd), newRecordData);
            toast.success("Evaluación guardada correctamente");
            setIsAddingRecord(false);
            setNewRecordData({
                pain_level: 0, sleep_quality: 0, energy_level: 0, stress_anxiety: 0, mobility: 0, inflammation: 0
            });
            // Recargar datos
            loadPatients();
        } catch (error) {
            console.error("Error guardando el registro", error);
            toast.error("Hubo un error al guardar la evaluación");
        }
    };

    const handleExport = () => {
        const dataToExport = filteredPatients.map((patient) => {
            const stats = getPatientIeimStats(patient);
            const hasScore = stats.score !== null;
            return {
                Paciente: `${patient.first_name} ${patient.last_name}`,
                Email: patient.email,
                'Última Evaluación': hasScore && stats.lastEvalDate ? `Hace ${getDaysAgo(stats.lastEvalDate)} días` : 'Sin evaluación',
                'Puntaje Global': hasScore ? stats.score : 'N/A',
                Tendencia: hasScore ? `${stats.trendIsUp ? '+' : '-'}${stats.trendValue}%` : 'N/A',
                'Nivel de Dolor': hasScore ? stats.lastEvalRecord?.pain_level || 0 : 'N/A',
                'Calidad de Sueño': hasScore ? stats.lastEvalRecord?.sleep_quality || 0 : 'N/A',
                'Nivel de Energía': hasScore ? stats.lastEvalRecord?.energy_level || 0 : 'N/A',
                'Estrés y Ansiedad': hasScore ? stats.lastEvalRecord?.stress_anxiety || 0 : 'N/A',
                Movilidad: hasScore ? stats.lastEvalRecord?.mobility || 0 : 'N/A',
                Inflamación: hasScore ? stats.lastEvalRecord?.inflammation || 0 : 'N/A',
            };
        });
        exportToExcel(dataToExport, 'Evolucion_Clinica_IEIM_Medizen');
    };

    return (
        <>
            <Toaster position="top-right" />
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">IEIM & Evolución Clínica</h1>
                    <p className="text-slate-500 text-sm mt-1">Índice de Evaluación Integral Metabólica por paciente</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="relative">
                        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                        <input
                            type="text"
                            placeholder="Buscar paciente..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-teal-500/20 outline-none transition-all shadow-sm w-64"
                        />
                    </div>
                    <button
                        onClick={handleExport}
                        className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-50 transition-colors shadow-sm flex items-center gap-2 active:scale-95 duration-200"
                    >
                        <Download className="w-4 h-4" />
                        Exportar Excel
                    </button>
                    <button
                        onClick={() => setIsAddingRecord(true)}
                        className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors shadow-sm shadow-teal-600/20 flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" /> Nueva Evaluación
                    </button>
                </div>
            </div>

            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl p-6 text-white shadow-lg shadow-indigo-500/20">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-white/20 rounded-xl">
                            <Brain className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-semibold text-white/90">Promedio Global</h3>
                    </div>
                    <div className="text-3xl font-bold mb-1">{globalAverage.toFixed(1)}<span className="text-lg font-normal text-white/80">/100</span></div>
                    <p className="text-indigo-100 text-sm flex items-center gap-1">
                        Basado en {patientsWithRecords.length} pacientes evaluados
                    </p>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110 duration-500"></div>
                    <div className="relative z-10">
                        <h3 className="text-sm font-semibold text-slate-500 mb-2 uppercase tracking-wider">Metas Alcanzadas</h3>
                        <div className="text-3xl font-bold text-slate-800 mb-2">{metasAlcanzadasPercent}%</div>
                        <div className="w-full bg-slate-100 rounded-full h-2">
                            <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${metasAlcanzadasPercent}%` }}></div>
                        </div>
                        <p className="text-slate-500 text-xs mt-2">Puntaje IEIM &ge; 80</p>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-amber-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110 duration-500"></div>
                    <div className="relative z-10">
                        <h3 className="text-sm font-semibold text-slate-500 mb-2 uppercase tracking-wider">Atención Crítica</h3>
                        <div className="flex items-end gap-3">
                            <div className="text-3xl font-bold text-slate-800">{criticalCareCount}</div>
                            <span className="text-sm font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded-md mb-1 border border-amber-100 flex items-center gap-1">
                                <AlertCircle className="w-3 h-3" /> Pacientes
                            </span>
                        </div>
                        <p className="text-slate-500 text-xs mt-2">Puntaje IEIM &lt; 50</p>
                    </div>
                </div>
            </div>

            {/* Patients List */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-slate-50/50 text-slate-500 text-xs uppercase tracking-wider">
                            <th className="p-4 font-medium border-b border-slate-100">Paciente</th>
                            <th className="p-4 font-medium border-b border-slate-100">Última Evaluación</th>
                            <th className="p-4 font-medium border-b border-slate-100">Puntaje IEIM Actual</th>
                            <th className="p-4 font-medium border-b border-slate-100">Tendencia</th>
                            <th className="p-4 font-medium border-b border-slate-100 text-right">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm divide-y divide-slate-100">
                        {filteredPatients.map((patient) => {
                            const stats = getPatientIeimStats(patient);
                            const hasScore = stats.score !== null;

                            return (
                                <tr key={patient.id} className="hover:bg-slate-50 transition-colors group">
                                    <td className="p-4">
                                        <div className="font-medium text-slate-800">{patient.first_name} {patient.last_name}</div>
                                        <div className="text-xs text-slate-500">{patient.email}</div>
                                    </td>
                                    <td className="p-4 text-slate-600">
                                        {hasScore && stats.lastEvalDate ? `Hace ${getDaysAgo(stats.lastEvalDate)} días` : 'Sin evaluación'}
                                    </td>
                                    <td className="p-4">
                                        {hasScore ? (
                                            <div className="flex items-center gap-3">
                                                <div className="flex-1 max-w-[120px] bg-slate-100 rounded-full h-2 overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${stats.score! > 80 ? 'bg-emerald-500' : stats.score! > 65 ? 'bg-teal-500' : stats.score! > 50 ? 'bg-amber-500' : 'bg-rose-500'}`}
                                                        style={{ width: `${stats.score}%` }}
                                                    ></div>
                                                </div>
                                                <span className="font-bold text-slate-700 w-8">{stats.score}</span>
                                            </div>
                                        ) : (
                                            <span className="text-slate-400 italic">No evaluado</span>
                                        )}
                                    </td>
                                    <td className="p-4">
                                        {hasScore ? (
                                            <div className={`flex items-center gap-1 text-xs font-semibold ${stats.trendIsUp ? 'text-emerald-600 bg-emerald-50 border-emerald-100' : 'text-rose-600 bg-rose-50 border-rose-100'} px-2 py-1 inline-flex rounded-full border`}>
                                                <TrendingUp className={`w-3 h-3 ${!stats.trendIsUp && 'rotate-180'}`} />
                                                {stats.trendIsUp ? '+' : '-'}{stats.trendValue}%
                                            </div>
                                        ) : (
                                            <span className="text-slate-300">-</span>
                                        )}
                                    </td>
                                    <td className="p-4 text-right">
                                        <button
                                            onClick={() => setSelectedPatient({ ...patient, ...stats })}
                                            className={`${hasScore ? 'text-indigo-600 hover:text-indigo-700' : 'text-slate-400 cursor-not-allowed'} font-medium text-sm transition-colors`}
                                            disabled={!hasScore}
                                            title={hasScore ? "Ver detalle de IEIM" : "Añade una evaluación primero"}
                                        >
                                            {hasScore ? 'Ver Detalle' : 'Sin Datos'}
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                        {filteredPatients.length === 0 && (
                            <tr>
                                <td colSpan={5} className="p-8 text-center text-slate-500">
                                    No se encontraron pacientes.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Modal de Detalles */}
            {selectedPatient && (
                <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
                        <div className="flex justify-between items-center p-6 border-b border-slate-100">
                            <div>
                                <h3 className="text-xl font-bold text-slate-800">
                                    Evolución de {selectedPatient.first_name} {selectedPatient.last_name}
                                </h3>
                                <p className="text-sm text-slate-500 mt-1">Detalle de métricas IEIM (Evaluación Reciente)</p>
                            </div>
                            <button
                                onClick={() => setSelectedPatient(null)}
                                className="text-slate-400 hover:text-slate-600 hover:bg-slate-100 p-2 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto">
                            <div className="flex items-center gap-6 mb-8 bg-slate-50 p-6 rounded-xl border border-slate-100">
                                <div className="text-center">
                                    <div className="text-sm font-semibold text-slate-500 mb-1 uppercase tracking-wide">Puntaje Global</div>
                                    <div className={`text-4xl font-black ${selectedPatient.score > 80 ? 'text-emerald-500' : selectedPatient.score > 65 ? 'text-teal-500' : selectedPatient.score > 50 ? 'text-amber-500' : 'text-rose-500'}`}>
                                        {selectedPatient.score}<span className="text-lg text-slate-400 font-normal">/100</span>
                                    </div>
                                </div>
                                <div className="h-16 w-px bg-slate-200"></div>
                                <div>
                                    <div className="text-sm font-semibold text-slate-500 mb-2 uppercase tracking-wide">Estado Metabólico</div>
                                    <div className="flex items-center gap-2">
                                        <Activity className={`w-5 h-5 ${selectedPatient.score > 65 ? 'text-emerald-500' : 'text-amber-500'}`} />
                                        <span className="font-medium text-slate-700">
                                            {selectedPatient.score > 80 ? 'Óptimo' : selectedPatient.score > 65 ? 'Favorable' : selectedPatient.score > 50 ? 'Requiere Atención' : 'Crítico'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <h4 className="font-semibold text-slate-800 mb-4">Desglose de Factores IEIM</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {[
                                    { label: 'Nivel de Dolor', val: (selectedPatient.lastEvalRecord?.pain_level || 0) * 10, color: 'bg-rose-500' },
                                    { label: 'Calidad de Sueño', val: (selectedPatient.lastEvalRecord?.sleep_quality || 0) * 10, color: 'bg-indigo-500' },
                                    { label: 'Energía Diaria', val: (selectedPatient.lastEvalRecord?.energy_level || 0) * 10, color: 'bg-amber-500' },
                                    { label: 'Estrés y Ansiedad', val: (selectedPatient.lastEvalRecord?.stress_anxiety || 0) * 10, color: 'bg-blue-500' },
                                    { label: 'Movilidad', val: (selectedPatient.lastEvalRecord?.mobility || 0) * 10, color: 'bg-emerald-500' },
                                    { label: 'Inflamación', val: (selectedPatient.lastEvalRecord?.inflammation || 0) * 10, color: 'bg-red-500' },
                                ].map((stat, idx) => (
                                    <div key={idx} className="bg-white border text-sm rounded-lg p-4 shadow-sm relative overflow-hidden">
                                        <div className="flex justify-between font-medium text-slate-700 mb-2">
                                            <span>{stat.label}</span>
                                            <span>{(stat.val / 10).toFixed(1)}/10</span>
                                        </div>
                                        <div className="w-full bg-slate-100 rounded-full h-1.5 object-cover">
                                            <div className={`h-full rounded-full ${stat.color}`} style={{ width: `${stat.val}%` }}></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
                            <button
                                onClick={() => setSelectedPatient(null)}
                                className="px-5 py-2 bg-white border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal para Nueva Evaluación */}
            {isAddingRecord && (
                <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
                        <div className="flex justify-between items-center p-6 border-b border-slate-100">
                            <div>
                                <h3 className="text-xl font-bold text-slate-800">Registrar Evaluación IEIM</h3>
                                <p className="text-sm text-slate-500 mt-1">Ingresa las variables metabólicas del paciente (0 a 10)</p>
                            </div>
                            <button
                                onClick={() => setIsAddingRecord(false)}
                                className="text-slate-400 hover:text-slate-600 hover:bg-slate-100 p-2 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto">
                            <form id="ieim-form" onSubmit={handleAddRecord} className="space-y-6">

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">Seleccionar Paciente</label>
                                    <select
                                        className="w-full border border-slate-200 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-teal-500/20 outline-none"
                                        required
                                        value={selectedPatientForAdd}
                                        onChange={(e) => setSelectedPatientForAdd(e.target.value)}
                                    >
                                        <option value="" disabled>-- Elige un paciente --</option>
                                        {patientsList.map(p => (
                                            <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-slate-50 rounded-xl border border-slate-100">
                                    {[
                                        { id: 'pain_level', label: 'Nivel de Dolor', min: 0, max: 10 },
                                        { id: 'sleep_quality', label: 'Calidad de Sueño', min: 0, max: 10 },
                                        { id: 'energy_level', label: 'Nivel de Energía', min: 0, max: 10 },
                                        { id: 'stress_anxiety', label: 'Estrés y Ansiedad', min: 0, max: 10 },
                                        { id: 'mobility', label: 'Movilidad', min: 0, max: 10 },
                                        { id: 'inflammation', label: 'Nivel de Inflamación', min: 0, max: 10 },
                                    ].map(field => (
                                        <div key={field.id}>
                                            <label className="block text-sm font-medium text-slate-700 mb-2 flex justify-between">
                                                <span>{field.label}</span>
                                                <span className="text-teal-600 font-bold">{newRecordData[field.id as keyof typeof newRecordData]}</span>
                                            </label>
                                            <input
                                                type="range"
                                                min={field.min}
                                                max={field.max}
                                                step="0.5"
                                                value={newRecordData[field.id as keyof typeof newRecordData]}
                                                onChange={(e) => setNewRecordData({ ...newRecordData, [field.id]: parseFloat(e.target.value) })}
                                                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
                                            />
                                            <div className="flex justify-between text-xs text-slate-400 mt-1">
                                                <span>Mínimo ({field.min})</span>
                                                <span>Máximo ({field.max})</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </form>
                        </div>

                        <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => setIsAddingRecord(false)}
                                className="px-5 py-2 bg-white border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                form="ieim-form"
                                className="px-5 py-2 bg-teal-600 rounded-lg text-white font-medium hover:bg-teal-700 transition-colors shadow-sm shadow-teal-600/20"
                            >
                                Guardar Evaluación
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
