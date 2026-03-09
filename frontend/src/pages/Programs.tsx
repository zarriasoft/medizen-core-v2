import React, { useState, useEffect } from 'react';
import { Activity, Plus, X, Search, Download } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { programsApi } from '../services/api';
import { exportToExcel } from '../utils/exportToExcel';

export default function Programs() {
    const [programsList, setProgramsList] = useState<any[]>([]);
    const [isProgramaModalOpen, setIsProgramaModalOpen] = useState(false);
    const [editingProgram, setEditingProgram] = useState<any>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const { register: regProg, handleSubmit: handleProg, reset: resetProg, setValue } = useForm();

    const loadData = async () => {
        try {
            const progs = await programsApi.getAll();
            setProgramsList(progs);
        } catch (error) {
            console.error("Error loading programs", error);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const openCreateModal = () => {
        setEditingProgram(null);
        resetProg();
        setIsProgramaModalOpen(true);
    };

    const openEditModal = (prog: any) => {
        setEditingProgram(prog);
        setValue('name', prog.name);
        setValue('description', prog.description);
        setValue('default_sessions', prog.default_sessions);
        setIsProgramaModalOpen(true);
    };

    const closeModal = () => {
        setIsProgramaModalOpen(false);
        setEditingProgram(null);
        resetProg();
    };

    const onNuevoPrograma = async (data: any) => {
        try {
            if (editingProgram) {
                await programsApi.update(editingProgram.id, {
                    name: data.name,
                    description: data.description,
                    default_sessions: parseInt(data.default_sessions)
                });
                toast.success("Programa actualizado exitosamente");
            } else {
                await programsApi.create({
                    name: data.name,
                    description: data.description,
                    default_sessions: parseInt(data.default_sessions)
                });
                toast.success("Programa creado exitosamente");
            }
            closeModal();
            loadData();
        } catch (error) {
            console.error("Error saving program", error);
            toast.error("Error al guardar el programa");
        }
    };

    const handleDelete = async (id: number) => {
        if (confirm("¿Estás seguro de eliminar este programa?")) {
            try {
                await programsApi.delete(id);
                toast.success("Programa eliminado correctamente");
                loadData();
            } catch (error) {
                console.error("Error deleting program", error);
                toast.error("Hubo un error al eliminar el programa");
            }
        }
    };

    const filteredPrograms = programsList.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (p.description && p.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const handleExport = () => {
        const dataToExport = filteredPrograms.map(p => ({
            ID: `#${p.id}`,
            Programa: p.name,
            Descripción: p.description || 'Sin descripción',
            'Sesiones Estimadas': p.default_sessions
        }));
        exportToExcel(dataToExport, 'Programas_Medizen');
    };

    return (
        <>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Programas de Especialidad</h1>
                    <p className="text-slate-500 text-sm mt-1">Administración de programas clínicos estructurados</p>
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
                        Nuevo Programa
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                    <div className="relative w-72">
                        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                        <input
                            type="text"
                            placeholder="Buscar programa..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-teal-500/50 outline-none transition-all"
                        />
                    </div>
                </div>
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-slate-50/50 text-slate-500 text-xs uppercase tracking-wider">
                            <th className="p-4 font-medium border-b border-slate-100">ID</th>
                            <th className="p-4 font-medium border-b border-slate-100">Programa</th>
                            <th className="p-4 font-medium border-b border-slate-100">Descripción</th>
                            <th className="p-4 font-medium border-b border-slate-100">Duración Estimada</th>
                            <th className="p-4 font-medium border-b border-slate-100 text-right">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm divide-y divide-slate-100">
                        {filteredPrograms.map((program) => (
                            <tr key={program.id} className="hover:bg-white hover:shadow-md transition-all hover:-translate-y-0.5 group">
                                <td className="p-4 text-slate-500">#{program.id}</td>
                                <td className="p-4 font-medium text-slate-800">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
                                            <Activity className="w-4 h-4" />
                                        </div>
                                        {program.name}
                                    </div>
                                </td>
                                <td className="p-4 text-slate-600 truncate max-w-xs">{program.description || 'Sin descripción'}</td>
                                <td className="p-4 text-slate-500">{program.default_sessions} sesiones</td>
                                <td className="p-4 text-right">
                                    <div className="flex justify-end gap-3">
                                        <button onClick={() => openEditModal(program)} className="text-teal-600 font-medium hover:text-teal-700 text-sm">Modificar</button>
                                        <button onClick={() => handleDelete(program.id)} className="text-red-500 font-medium hover:text-red-600 text-sm">Eliminar</button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                        {filteredPrograms.length === 0 && (
                            <tr>
                                <td colSpan={5} className="p-8 text-center text-slate-500">
                                    No se encontraron programas.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Modal Nuevo Programa */}
            {isProgramaModalOpen && (
                <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-md shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center justify-between p-6 border-b border-slate-100">
                            <h2 className="text-xl font-bold text-slate-800">{editingProgram ? 'Modificar Programa' : 'Crear Nuevo Programa'}</h2>
                            <button onClick={closeModal} className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-50 rounded-full transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleProg(onNuevoPrograma)} className="p-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Nombre del Programa</label>
                                    <input required type="text" {...regProg("name")} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Sesiones Estimadas</label>
                                    <input required type="number" {...regProg("default_sessions")} defaultValue="8" min="1" className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Descripción (Opcional)</label>
                                    <textarea {...regProg("description")} rows={3} className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"></textarea>
                                </div>
                            </div>
                            <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-slate-50">
                                <button type="button" onClick={closeModal} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-xl transition-colors">Cancelar</button>
                                <button type="submit" className="px-5 py-2.5 bg-teal-500 hover:bg-teal-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-teal-500/20 transition-all active:scale-95">Guardar Programa</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
