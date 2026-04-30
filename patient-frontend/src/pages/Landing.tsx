import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Star, MapPin, Phone, Globe, Calendar, Tag, HeartHandshake } from 'lucide-react';
import axios from 'axios';

interface Plan {
    name: string;
    price: string;
    period: string;
    description: string;
    features: string[];
    buttonColor: string;
    headerColor: string;
    popular: boolean;
}


function App() {
    const [plans, setPlans] = React.useState<Plan[]>([]);
    const [isLoadingPlans, setIsLoadingPlans] = React.useState(true);
    const [isEnrollModalOpen, setIsEnrollModalOpen] = React.useState(false);
    const [selectedPlan, setSelectedPlan] = React.useState('');
    const [enrollForm, setEnrollForm] = React.useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        phone: '',
        date_of_birth: ''
    });
    const [enrollStatus, setEnrollStatus] = React.useState<'idle' | 'loading' | 'success' | 'error'>('idle');

    useEffect(() => {
        // Fetch plans from backend
        const fetchPlans = async () => {
            try {
                // In production, this should use VITE_API_URL env variable
                const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                // Add a timeout of 10s to avoid hanging forever on sleeping backends
                const response = await axios.get(`${apiUrl}/membership-plans/`, { timeout: 10000 });

                if (response.data && response.data.length > 0) {
                    // Map backend data to frontend structure
                    const activePlans = response.data.filter((p: { is_active: boolean }) => p.is_active);

                    if (activePlans.length > 0) {
                        const formattedPlans = activePlans.map((p: { color: string; features: string; price: string | number; name: string; frequency: string; description: string; is_popular: boolean; }) => {
                            // Determine colors based on db color string
                            let buttonColor = "bg-slate-600 hover:bg-slate-700";
                            let headerColor = "bg-slate-50";

                            if (p.color === 'emerald' || p.color === 'teal') {
                                buttonColor = "bg-emerald-600 hover:bg-emerald-700";
                                headerColor = "bg-emerald-50";
                            } else if (p.color === 'amber' || p.color === 'yellow') {
                                buttonColor = "bg-amber-600 hover:bg-amber-700";
                                headerColor = "bg-amber-50";
                            } else if (p.color === 'orange') {
                                buttonColor = "bg-orange-600 hover:bg-orange-700";
                                headerColor = "bg-orange-50";
                            } else if (p.color === 'indigo') {
                                buttonColor = "bg-indigo-600 hover:bg-indigo-700";
                                headerColor = "bg-indigo-50";
                            }

                            // Parse comma or newline separated features to array
                            const rawFeatures = p.features ? p.features.split(/[\n,]+/) : [];
                            const featureArray = rawFeatures
                                .map((f: string) => f.replace(/^-\s*/, '').trim())
                                .filter(Boolean);

                            // Format price (allow for text like "$45,000")
                            const numericString = String(p.price).replace(/[^0-9]/g, '');
                            const numericPrice = Number(numericString);
                            // If it parsed to a valid number and isn't empty, format it. Otherwise keep the original text.
                            const formattedPrice = (numericString && !isNaN(numericPrice))
                                ? "$" + numericPrice.toLocaleString('es-CL')
                                : p.price;

                            return {
                                name: p.name,
                                price: formattedPrice,
                                period: `/${p.frequency}`,
                                description: p.description || "",
                                features: featureArray,
                                buttonColor,
                                headerColor,
                                popular: p.is_popular
                            };
                        });

                        setPlans(formattedPlans);
                    } else {
                        setPlans([]); // Fallback to empty if no active plans found
                    }
                } else {
                    setPlans([]); // Fallback to empty if no plans exist
                }
            } catch (error) {
                console.error("Error fetching plans from backend:", error);
            } finally {
                setIsLoadingPlans(false);
            }
        };

        fetchPlans();
    }, []);

    const handleSubscribe = (planName: string) => {
        // Track the click before routing
        console.log(`User clicked subscribe on ${planName}`);
        setSelectedPlan(planName);
        setIsEnrollModalOpen(true);
        setEnrollStatus('idle');
        setEnrollForm({
            first_name: '',
            last_name: '',
            email: '',
            password: '',
            phone: '',
            date_of_birth: ''
        });
    };

    const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setEnrollForm({ ...enrollForm, [e.target.name]: e.target.value });
    };

    const handleEnrollSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setEnrollStatus('loading');
        try {
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            await axios.post(`${apiUrl}/public/enroll`, {
                ...enrollForm,
                plan_name: selectedPlan
            });
            setEnrollStatus('success');
        } catch (error) {
            console.error(error);
            setEnrollStatus('error');
        }
    };

    return (
        <div className="font-sans text-slate-800 bg-slate-50 min-h-screen">
            {/* Nav/Header */}
            <header className="bg-brand-dark text-white py-6 text-center border-b-4 border-amber-500/80 relative">
                <h1 className="text-3xl font-serif mb-1 tracking-wide">Centro de Salud MediZen</h1>
                <p className="text-emerald-100/80 text-sm font-light uppercase tracking-[0.2em] mt-2">Membresías de Bienestar</p>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 hidden sm:block">
                    <button onClick={() => window.location.href='/login'} className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-white/20">Portal de Pacientes</button>
                </div>
            </header>

            {/* Hero Section */}
            <section className="py-16 md:py-24 bg-brand-light text-center px-4 relative overflow-hidden shadow-inner">
                <div className="absolute inset-0 opacity-10 bg-[url('https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-overlay"></div>

                <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8 }}
                    className="relative z-10 max-w-4xl mx-auto"
                >
                    <h2 className="text-4xl md:text-5xl lg:text-6xl font-serif text-white mb-6 leading-tight text-balance">
                        Equilibra tu cuerpo, mente y emociones cada mes.
                    </h2>
                    <p className="text-emerald-50 text-lg md:text-xl font-light mb-8 max-w-2xl mx-auto opacity-90">
                        Planes diseñados a tu medida para sanar progresivamente y mantener tu energía vital en su máximo nivel.
                    </p>
                </motion.div>
            </section>

            {/* Prestige / Reviews */}
            <section className="py-10 bg-white border-b border-slate-200">
                <div className="max-w-5xl mx-auto px-4 flex flex-col md:flex-row items-center justify-center gap-8">
                    <div className="text-center md:text-right">
                        <p className="font-bold text-slate-800 text-lg mb-1">Profesionales de Alta Excelencia</p>
                        <div className="flex justify-center md:justify-end text-amber-400 mb-1 gap-1">
                            <Star className="fill-current w-5 h-5" />
                            <Star className="fill-current w-5 h-5" />
                            <Star className="fill-current w-5 h-5" />
                            <Star className="fill-current w-5 h-5" />
                            <Star className="fill-current w-5 h-5" />
                        </div>
                        <p className="text-sm text-slate-500 font-medium">Avalados por pacientes reales</p>
                    </div>

                    <div className="hidden md:block w-px h-16 bg-slate-200"></div>

                    {/*
                    <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto px-4 md:px-0">
                        <a href="https://google.com" target="_blank" rel="noreferrer" className="flex-1 md:flex-none flex items-center justify-center gap-3 bg-white px-6 py-3 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-200 transition-all group">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/1024px-Google_%22G%22_logo.svg.png" alt="Google" className="w-6 h-6 group-hover:scale-110 transition-transform" />
                            <div className="text-left">
                                <span className="block text-xs text-slate-500 line-height-1">Reseñas en</span>
                                <span className="block text-sm font-bold text-slate-700">Google (5.0)</span>
                            </div>
                        </a>
                        <a href="https://doctoralia.cl" target="_blank" rel="noreferrer" className="flex-1 md:flex-none flex items-center justify-center gap-3 bg-white px-6 py-3 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-emerald-200 transition-all group">
                            <div className="bg-emerald-500 p-1.5 rounded-full text-white group-hover:scale-110 transition-transform">
                                <HeartHandshake className="w-4 h-4" />
                            </div>
                            <div className="text-left">
                                <span className="block text-xs text-slate-500 line-height-1">Perfil verificado</span>
                                <span className="block text-sm font-bold text-emerald-700">Doctoralia</span>
                            </div>
                        </a>
                    </div>
                    */}
                </div>
            </section>

            {/* Plans Section */}
            <section className="py-20 px-4 max-w-7xl mx-auto relative relative">
                <div className="text-center mb-16">
                     <span className="inline-flex items-center gap-2 bg-amber-100 text-amber-800 text-sm font-bold px-5 py-2 rounded-full uppercase tracking-wider border border-amber-200 shadow-sm">
                         <Tag className="w-4 h-4" />
                         ¡Cupos Limitados!
                     </span>
                </div>

                <div className={`grid gap-8 items-start lg:px-8 ${
                    isLoadingPlans ? 'md:grid-cols-3' :
                    plans.length === 1 ? 'md:grid-cols-1 max-w-sm mx-auto' :
                    plans.length === 2 ? 'md:grid-cols-2 max-w-4xl mx-auto' :
                    'md:grid-cols-3'
                }`}>
                    {isLoadingPlans ? (
                        <div className="col-span-full text-center py-20">
                            <p className="text-slate-500">Cargando planes de membresía...</p>
                        </div>
                    ) : plans.length === 0 ? (
                        <div className="col-span-full text-center py-20">
                            <p className="text-slate-500">Actualmente no hay planes de membresía disponibles.</p>
                        </div>
                    ) : (
                        plans.map((plan, index) => (
                        <motion.div
                            initial={{ y: 50, opacity: 0 }}
                            whileInView={{ y: 0, opacity: 1 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ delay: index * 0.15, duration: 0.5 }}
                            key={plan.name}
                            className={`bg-white rounded-3xl overflow-hidden shadow-xl border-2 flex flex-col h-full
                                ${plan.popular ? 'border-amber-400 ring-4 ring-amber-400/20 scale-100 md:scale-105 z-10' : 'border-slate-100'}`}
                        >
                            {plan.popular && (
                                <div className="bg-amber-400 text-amber-900 text-center text-xs font-bold py-1.5 uppercase tracking-widest">
                                    El Más Elegido
                                </div>
                            )}
                            <div className={`${plan.headerColor} p-8 text-center border-b border-black/5 flex-none`}>
                                <h3 className="text-2xl font-bold text-brand-dark mb-3 tracking-tight">{plan.name}</h3>
                                <div className="flex justify-center items-center gap-1 mb-1 relative">
                                    <span className="text-5xl font-extrabold text-brand-dark">{plan.price}</span>
                                    <span className="text-slate-500 font-medium absolute -right-12 bottom-2">{plan.period}</span>
                                </div>
                            </div>

                            <div className="p-8 flex flex-col flex-grow">
                                <ul className="space-y-5 mb-8 flex-grow">
                                    {plan.features.map((feature: string, i: number) => (
                                        <li key={i} className="flex items-start gap-4">
                                            <div className="bg-emerald-100 rounded-full p-1 mt-0.5 shrink-0">
                                                <Check className="w-4 h-4 text-emerald-600" />
                                            </div>
                                            <span className="text-slate-700 font-medium leading-tight">{feature}</span>
                                        </li>
                                    ))}
                                </ul>

                                <div className="text-center italic text-slate-500 mb-8 font-serif px-4">
                                    "{plan.description}"
                                </div>

                                <button
                                    onClick={() => handleSubscribe(plan.name)}
                                    className={`w-full py-4 px-6 rounded-2xl text-white font-bold text-lg transition-all active:scale-95 shadow-lg ${plan.buttonColor}`}
                                >
                                    Inscribirme Ahora
                                </button>
                            </div>
                        </motion.div>
                    )))}
                </div>
            </section>

            {/* Features Footer */}
            <section className="bg-white py-16 border-t border-slate-200">
                <div className="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-12 text-center divide-y md:divide-y-0 md:divide-x divide-slate-100">
                    <div className="flex flex-col items-center pt-8 md:pt-0 px-4">
                        <div className="bg-emerald-50 w-16 h-16 rounded-2xl flex items-center justify-center mb-4 text-emerald-600">
                            <Calendar className="w-8 h-8" />
                        </div>
                        <h4 className="font-bold text-slate-800 text-lg">Prioridad en agenda</h4>
                        <p className="text-slate-500 mt-2">Asegura tu horario preferido cada mes sin esperas innecesarias.</p>
                    </div>
                    <div className="flex flex-col items-center pt-8 md:pt-0 px-4">
                        <div className="bg-amber-50 w-16 h-16 rounded-2xl flex items-center justify-center mb-4 text-amber-500">
                            <Tag className="w-8 h-8" />
                        </div>
                        <h4 className="font-bold text-slate-800 text-lg">Descuentos especiales</h4>
                        <p className="text-slate-500 mt-2">Accede a precios preferenciales en terapias complementarias exclusivas.</p>
                    </div>
                    <div className="flex flex-col items-center pt-8 md:pt-0 px-4">
                        <div className="bg-blue-50 w-16 h-16 rounded-2xl flex items-center justify-center mb-4 text-blue-500">
                            <HeartHandshake className="w-8 h-8" />
                        </div>
                        <h4 className="font-bold text-slate-800 text-lg">Acompañamiento continuo</h4>
                        <p className="text-slate-500 mt-2">Seguimiento constante de tu evolución con atención personalizada.</p>
                    </div>
                </div>
            </section>

            {/* Contact Footer */}
            <footer className="bg-brand-dark text-emerald-50/80 py-12">
                <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-6 text-sm">
                    <div className="flex items-center gap-3">
                        <MapPin className="w-5 h-5 text-amber-400" />
                        <span className="font-medium">Centro de Salud MediZen</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <Phone className="w-5 h-5 text-amber-400" />
                        <span className="font-medium">+56 9 6358 1696</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <Globe className="w-5 h-5 text-amber-400" />
                        <span className="font-medium">www.mediZen.cl</span>
                    </div>
                </div>
            </footer>

            {/* Floating Chat Widget (Hidden for production until ready) */}
            {/*
            <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
                <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ delay: 2 }}
                    className="bg-white px-4 py-3 rounded-2xl shadow-xl border border-slate-100 text-sm font-medium text-slate-700"
                >
                    ¡Hola! ¿Tienes dudas sobre los planes? 👋
                </motion.div>
                <button
                    className="bg-emerald-500 hover:bg-emerald-600 text-white w-16 h-16 rounded-full shadow-2xl flex items-center justify-center transition-transform hover:scale-110"
                    onClick={() => alert('Abriendo chat integrado en vivo con el equipo de MediZen...')}
                >
                    <MessageCircle className="w-7 h-7" />
                </button>
            </div>
            */}

            {/* Enrollment Modal */}
            {isEnrollModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden relative"
                    >
                        {/* Close button */}
                        <button
                            onClick={() => setIsEnrollModalOpen(false)}
                            className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 transition-colors z-10"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </button>

                        <div className="p-6 md:p-8">
                            {enrollStatus === 'success' ? (
                                <div className="text-center py-6">
                                    <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <Check className="w-8 h-8 text-emerald-600" />
                                    </div>
                                    <h3 className="text-2xl font-bold text-slate-800 mb-2">¡Inscripción Exitosa!</h3>
                                    <p className="text-slate-600 mb-6">
                                        Tus datos se han registrado correctamente. Muy pronto nuestro equipo se contactará contigo para coordinar el pago y activar tu plan <strong>{selectedPlan}</strong>.
                                    </p>
                                    <button
                                        onClick={() => setIsEnrollModalOpen(false)}
                                        className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-3 px-4 rounded-xl transition-colors"
                                    >
                                        Cerrar
                                    </button>
                                </div>
                            ) : (
                                <>
                                    <div className="mb-6">
                                        <h3 className="text-2xl font-bold text-brand-dark mb-1">Únete a MediZen</h3>
                                        <p className="text-slate-500 text-sm">Estás a un paso de acceder al plan <strong>{selectedPlan}</strong>. Ingresa tus datos a continuación.</p>
                                    </div>

                                    {enrollStatus === 'error' && (
                                        <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                                            Ocurrió un error al enviar tu solicitud. Por favor intenta de nuevo.
                                        </div>
                                    )}

                                    <form onSubmit={handleEnrollSubmit} className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 mb-1">Nombre</label>
                                                <input required type="text" name="first_name" value={enrollForm.first_name} onChange={handleFormChange} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500" placeholder="Ej: Juan" />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 mb-1">Apellido</label>
                                                <input required type="text" name="last_name" value={enrollForm.last_name} onChange={handleFormChange} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500" placeholder="Ej: Perez" />
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 mb-1">Correo Electrónico</label>
                                                <input required type="email" name="email" value={enrollForm.email} onChange={handleFormChange} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500" placeholder="tucorreo@ejemplo.com" />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 mb-1">Contraseña (Portal Paciente)</label>
                                                <input required type="password" name="password" value={enrollForm.password} onChange={handleFormChange} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500" placeholder="Crea tu contraseña" />
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 mb-1">Teléfono</label>
                                                <input required type="tel" name="phone" value={enrollForm.phone} onChange={handleFormChange} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500" placeholder="+56 9 XXXXXXXX" />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 mb-1">Fecha de Nac. (Opcional)</label>
                                                <input type="date" name="date_of_birth" value={enrollForm.date_of_birth} onChange={handleFormChange} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500" />
                                            </div>
                                        </div>
                                        <div className="pt-4">
                                            <button
                                                type="submit"
                                                disabled={enrollStatus === 'loading'}
                                                className={`w-full py-3 px-4 rounded-xl text-white font-bold flex justify-center items-center transition-all ${enrollStatus === 'loading' ? 'bg-slate-400 cursor-not-allowed' : 'bg-brand-dark hover:bg-slate-800 active:scale-95 shadow-lg'}`}
                                            >
                                                {enrollStatus === 'loading' ? 'Enviando...' : 'Confirmar Datos e Inscribirme'}
                                            </button>
                                        </div>
                                    </form>
                                </>
                            )}
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    );
}

export default App;
