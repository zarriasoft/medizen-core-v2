import { GoogleGenAI, ThinkingLevel, Modality } from "@google/genai";
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export interface ConsultationData {
    wang: { tez: string; lenguaCuerpo: string; saburra: string; };
    wenA: { voz: string; respiracion: string; olores: string; };
    wenI: { temperatura: string; sudoracion: string; apetitoSed: string; digestion: string; sueno: string; dolor: string; };
    qie: { puntosAshi: string; pulso: string; };
}

export const differentiateSyndrome = async (data: ConsultationData, useThinking: boolean = true) => {
    const prompt = `Realiza una Diferenciación de Síndromes (Bian Zheng) de MTC para: ${JSON.stringify(data)}. Responde en JSON con sindromePrincipal, explicacionFisiopatologica, propuestaTerapeutica.`;
    const response = await ai.models.generateContent({
        model: "gemini-3.1-pro-preview",
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        config: { thinkingConfig: useThinking ? { thinkingLevel: ThinkingLevel.HIGH } : undefined, responseMimeType: "application/json" },
    });
    return JSON.parse(response.text || "{}");
};

export const chatWithGemini = async (message: string, history: any[], useThinking: boolean = true) => {
    const chat = ai.chats.create({ model: "gemini-3.1-pro-preview", config: { systemInstruction: "Eres un asistente experto en MTC." } });
    const response = await chat.sendMessage({ message });
    return response.text;
};

export const generateSpeech = async (text: string) => {
    const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-tts",
        contents: [{ parts: [{ text }] }],
        config: { responseModalities: [Modality.AUDIO] },
    });
    const data = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
    return data ? new Audio(`data:audio/mp3;base64,${data}`) : null;
};
