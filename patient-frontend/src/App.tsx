import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Star, MessageCircle, MapPin, Phone, Globe, Calendar, Tag, HeartHandshake } from 'lucide-react';
import axios from 'axios';

// Analytics tracking implementation
const trackVisit = async () => {
    try {
        await axios.post('http://localhost:8000/analytics/visit', {
            source: 'patient_portal',
            timestamp: new Date().toISOString()
        });
        console.log("Visit tracked successfully");
    } catch (e) {
        // Suppress errors if backend is not reachable for tracking purposes
        console.warn("Analytics service unavailable");
    }
};

const staticPlans = [
    {
        name: "Plan Básico",
        price: "$39.000",
        period: "/mes",
        description: "Equilibra tu energía y salud",
        features: [
            "2 sesiones de Acupuntura",
            "1 sesión Cama de Cuarzo Terapéutica",
            "10% de descuento en otras terapias"
        ],
        buttonColor: "bg-emerald-600 hover:bg-emerald-700",
        headerColor: "bg-emerald-50",
        popular: false
    },
    {
        name: "Plan Integrativo",
        price: "$69.000",
        period: "/mes",
        description: "Cuerpo, mente, y emociones",
        features: [
            "Tratamiento Integral (Acupuntura + Neurociencia + Alimentacion)",
            "1 sesión Cama de Cuarzo Emocional",
            "1 Reflexología o Masaje Descontracturante"
        ],
        buttonColor: "bg-amber-600 hover:bg-amber-700",
        headerColor: "bg-amber-50",
        popular: true
    },
    {
        name: "Plan Premium",
        price: "$119.000",
        period: "/mes",
        description: "Bienestar y transformación",
        features: [
            "2 Tratamientos Integrales",
            "2 sesiones Cama de Cuarzo",
            "1 Masaje Descontracturante",
            "1 Sesión de Reflexología"
        ],
        buttonColor: "bg-orange-600 hover:bg-orange-700",
        headerColor: "bg-orange-50",
        popular: false
    }
];

function App() {
    const [plans, setPlans] = React.useState<any[]>(staticPlans);

    useEffect(() => {
        trackVisit();
        
        // Fetch plans from backend
        const fetchPlans = async () => {
            try {
                // In production, this should use VITE_API_URL env variable
                const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await axios.get(`${apiUrl}/membership-plans/`);
                
                if (response.data && response.data.length > 0) {
                    // Map backend data to frontend structure
                    const activePlans = response.data.filter((p: any) => p.is_active);
                    
                    if (activePlans.length > 0) {
                        const formattedPlans = activePlans.map((p: any) => {
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
                            
                            // Parse commma separated features to array
                            const featureArray = p.features ? p.features.split(',').map((f: string) => f.trim()) : [];
                            
                            // Fill missing features to ensure at least 3 points are shown according to design, 
                            // if they exist.
                            
                            return {
                                name: p.name,
                                price: p.price, // the price text from db
                                period: `/${p.frequency}`,
                                description: p.description || "",
                                features: featureArray,
                                buttonColor,
                                headerColor,
                                popular: p.is_popular
                            };
                        });
                        
                        setPlans(formattedPlans);
                    }
                }
            } catch (error) {
                console.error("Error fetching plans from backend, using default static plans:", error);
            }
        };
        
        fetchPlans();
    }, []);

    const handleSubscribe = (planName: string) => {
        // Track the click before routing
        console.log(`User clicked subscribe on ${planName}`);
        alert(`Redirigiendo a pago/suscripción para: ${planName}`);
    };

    return (
        <div className="font-sans text-slate-800 bg-slate-50 min-h-screen">
            {/* Nav/Header */}
            <header className="bg-brand-dark text-white py-6 text-center border-b-4 border-amber-500/80">
                <h1 className="text-3xl font-serif mb-1 tracking-wide">Centro de Salud MediZen</h1>
                <p className="text-emerald-100/80 text-sm font-light uppercase tracking-[0.2em] mt-2">Membresías de Bienestar</p>
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
                
                <div className="grid md:grid-cols-3 gap-8 items-start lg:px-8">
                    {plans.map((plan, index) => (
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
                    ))}
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

            {/* Floating Chat Widget */}
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
        </div>
    );
}

export default App;
