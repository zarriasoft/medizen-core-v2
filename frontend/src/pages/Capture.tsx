import React, { useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface FormData {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    pain_level: number;
    sleep_quality: number;
    energy_level: number;
    stress_anxiety: number;
    mobility: number;
    inflammation: number;
}

interface Result {
    message: string;
    overall_score: number;
    classification: string;
    recommendation: string;
}

const questions = [
    { key: 'pain_level', label: '¿Cuánto dolor físico has sentido esta semana?', icon: '🩹', hint: '1 = Dolor intenso / 10 = Sin dolor' },
    { key: 'sleep_quality', label: '¿Cómo calificarías la calidad de tu sueño?', icon: '😴', hint: '1 = Muy malo / 10 = Excelente' },
    { key: 'energy_level', label: '¿Cuál es tu nivel de energía general?', icon: '⚡', hint: '1 = Sin energía / 10 = Muy alta' },
    { key: 'stress_anxiety', label: '¿Cómo está tu nivel de estrés y ansiedad?', icon: '🧠', hint: '1 = Muy estresado / 10 = Muy tranquilo' },
    { key: 'mobility', label: '¿Cómo es tu movilidad y flexibilidad?', icon: '🏃', hint: '1 = Muy limitada / 10 = Total libertad' },
    { key: 'inflammation', label: '¿Sientes inflamación o tensión en tu cuerpo?', icon: '🔥', hint: '1 = Mucha inflamación / 10 = Sin inflamación' },
];

function ScoreBar({ value, onChange }: { value: number; onChange: (v: number) => void }) {
    return (
        <div className="score-bar-container">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                <button
                    key={n}
                    type="button"
                    className={`score-btn ${value === n ? 'selected' : ''} ${value >= n ? 'filled' : ''}`}
                    onClick={() => onChange(n)}
                >
                    {n}
                </button>
            ))}
        </div>
    );
}

export default function Capture() {
    const [step, setStep] = useState<'info' | 'questions' | 'result'>('info');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<Result | null>(null);
    const [form, setForm] = useState<FormData>({
        first_name: '', last_name: '', email: '', phone: '',
        pain_level: 0, sleep_quality: 0, energy_level: 0,
        stress_anxiety: 0, mobility: 0, inflammation: 0,
    });

    const updateField = (key: string, value: string | number) => {
        setForm(prev => ({ ...prev, [key]: value }));
    };

    const canProceedToQuestions = form.first_name && form.last_name && form.email;
    const allQuestionsAnswered = questions.every(q => (form as any)[q.key] > 0);

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/public/capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form),
            });
            const data = await res.json();
            setResult(data);
            setStep('result');
        } catch {
            alert('Error al enviar el formulario. Por favor intenta de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 8) return '#10b981';
        if (score >= 6) return '#f59e0b';
        if (score >= 4) return '#f97316';
        return '#ef4444';
    };

    return (
        <div className="capture-root">
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
                * { box-sizing: border-box; margin: 0; padding: 0; }
                .capture-root {
                    font-family: 'Inter', sans-serif;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
                    display: flex; align-items: center; justify-content: center;
                    padding: 24px;
                }
                .capture-card {
                    background: rgba(255,255,255,0.05);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 24px;
                    padding: 48px;
                    max-width: 640px;
                    width: 100%;
                    box-shadow: 0 25px 50px rgba(0,0,0,0.4);
                }
                .logo { text-align: center; margin-bottom: 8px; }
                .logo-text { font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #14b8a6, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .subtitle { text-align: center; color: #94a3b8; font-size: 0.95rem; margin-bottom: 36px; }
                h2 { color: #f1f5f9; font-size: 1.4rem; font-weight: 700; margin-bottom: 6px; }
                .section-desc { color: #94a3b8; font-size: 0.9rem; margin-bottom: 28px; }
                .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
                .form-field { display: flex; flex-direction: column; gap: 6px; }
                .form-field.full { grid-column: 1 / -1; }
                label { color: #cbd5e1; font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
                input {
                    background: rgba(255,255,255,0.07);
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 10px;
                    padding: 12px 16px;
                    color: #f1f5f9;
                    font-size: 0.95rem;
                    font-family: 'Inter', sans-serif;
                    outline: none;
                    transition: border-color 0.2s;
                }
                input:focus { border-color: #14b8a6; }
                input::placeholder { color: #475569; }
                .btn-primary {
                    width: 100%;
                    padding: 14px;
                    background: linear-gradient(135deg, #14b8a6, #6366f1);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 1rem;
                    font-weight: 700;
                    cursor: pointer;
                    margin-top: 20px;
                    transition: opacity 0.2s, transform 0.1s;
                    font-family: 'Inter', sans-serif;
                }
                .btn-primary:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
                .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
                .question-block { margin-bottom: 28px; }
                .q-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
                .q-icon { font-size: 1.5rem; }
                .q-label { color: #f1f5f9; font-size: 1rem; font-weight: 600; }
                .q-hint { color: #64748b; font-size: 0.78rem; margin-bottom: 12px; }
                .score-bar-container { display: flex; gap: 6px; flex-wrap: wrap; }
                .score-btn {
                    width: 44px; height: 44px;
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.15);
                    background: rgba(255,255,255,0.05);
                    color: #94a3b8;
                    font-size: 0.9rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.15s;
                    font-family: 'Inter', sans-serif;
                }
                .score-btn.selected { background: linear-gradient(135deg,#14b8a6,#6366f1); color: white; border-color: transparent; transform: scale(1.1); }
                .score-btn.filled:not(.selected) { background: rgba(20,184,166,0.2); color: #14b8a6; border-color: rgba(20,184,166,0.3); }
                .score-btn:hover:not(.selected) { border-color: #14b8a6; color: #14b8a6; }
                .result-score {
                    text-align: center;
                    padding: 32px;
                    background: rgba(255,255,255,0.04);
                    border-radius: 20px;
                    margin-bottom: 24px;
                    border: 1px solid rgba(255,255,255,0.08);
                }
                .result-score-number { font-size: 5rem; font-weight: 800; line-height: 1; }
                .result-score-label { color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }
                .result-classification { font-size: 1.3rem; font-weight: 700; margin-top: 16px; color: #f1f5f9; }
                .result-recommendation {
                    background: rgba(255,255,255,0.05);
                    border-left: 3px solid #14b8a6;
                    padding: 16px 20px;
                    border-radius: 0 12px 12px 0;
                    color: #cbd5e1;
                    font-size: 0.95rem;
                    line-height: 1.6;
                    margin-bottom: 24px;
                }
                .cta-text { text-align: center; color: #94a3b8; font-size: 0.9rem; }
                .cta-text strong { color: #14b8a6; }
                .progress-dots { display: flex; justify-content: center; gap: 8px; margin-bottom: 32px; }
                .dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.15); transition: all 0.3s; }
                .dot.active { background: #14b8a6; width: 24px; border-radius: 4px; }
                .dot.done { background: #6366f1; }
            `}</style>

            <div className="capture-card">
                <div className="logo"><span className="logo-text">MediZen</span></div>
                <p className="subtitle">Test de Equilibrio Integral de Salud · IEIM 2.0</p>

                <div className="progress-dots">
                    <div className={`dot ${step === 'info' ? 'active' : 'done'}`} />
                    <div className={`dot ${step === 'questions' ? 'active' : step === 'result' ? 'done' : ''}`} />
                    <div className={`dot ${step === 'result' ? 'active' : ''}`} />
                </div>

                {step === 'info' && (
                    <>
                        <h2>¡Hola! Cuéntanos sobre ti</h2>
                        <p className="section-desc">Comenzaremos con tus datos para personalizar tu evaluación.</p>
                        <div className="form-grid">
                            <div className="form-field">
                                <label>Nombre</label>
                                <input type="text" placeholder="Ej: María" value={form.first_name} onChange={e => updateField('first_name', e.target.value)} />
                            </div>
                            <div className="form-field">
                                <label>Apellido</label>
                                <input type="text" placeholder="Ej: García" value={form.last_name} onChange={e => updateField('last_name', e.target.value)} />
                            </div>
                            <div className="form-field full">
                                <label>Email</label>
                                <input type="email" placeholder="tu@email.com" value={form.email} onChange={e => updateField('email', e.target.value)} />
                            </div>
                            <div className="form-field full">
                                <label>Teléfono (opcional)</label>
                                <input type="tel" placeholder="+54 11 1234-5678" value={form.phone} onChange={e => updateField('phone', e.target.value)} />
                            </div>
                        </div>
                        <button className="btn-primary" disabled={!canProceedToQuestions} onClick={() => setStep('questions')}>
                            Comenzar Evaluación →
                        </button>
                    </>
                )}

                {step === 'questions' && (
                    <>
                        <h2>Tu Índice de Equilibrio IEIM</h2>
                        <p className="section-desc">Califica del 1 al 10 cada aspecto de tu salud esta semana.</p>
                        {questions.map(q => (
                            <div className="question-block" key={q.key}>
                                <div className="q-header">
                                    <span className="q-icon">{q.icon}</span>
                                    <span className="q-label">{q.label}</span>
                                </div>
                                <p className="q-hint">{q.hint}</p>
                                <ScoreBar
                                    value={(form as any)[q.key]}
                                    onChange={v => updateField(q.key, v)}
                                />
                            </div>
                        ))}
                        <button className="btn-primary" disabled={!allQuestionsAnswered || loading} onClick={handleSubmit}>
                            {loading ? 'Calculando tu resultado...' : 'Ver mi Resultado IEIM →'}
                        </button>
                    </>
                )}

                {step === 'result' && result && (
                    <>
                        <h2>Tu Resultado</h2>
                        <p className="section-desc">{result.message}</p>
                        <div className="result-score">
                            <div className="result-score-number" style={{ color: getScoreColor(result.overall_score) }}>
                                {result.overall_score}
                            </div>
                            <div className="result-score-label">Índice IEIM / 10</div>
                            <div className="result-classification">{result.classification}</div>
                        </div>
                        <div className="result-recommendation">{result.recommendation}</div>
                        <div className="cta-text">
                            Un especialista de <strong>MediZen</strong> se pondrá en contacto contigo para coordinar tu primera sesión personalizada.
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
