import { ConsultationData } from "./services/aiService";
export interface SyndromeResult {
    sindromePrincipal: string;
    explicacionFisiopatologica: string;
    propuestaTerapeutica: any;
}
export const initialConsultationData: ConsultationData = {
    wang: { tez: "", lenguaCuerpo: "", saburra: "" },
    wenA: { voz: "", respiracion: "", olores: "" },
    wenI: { temperatura: "", sudoracion: "", apetitoSed: "", digestion: "", sueno: "", dolor: "" },
    qie: { puntosAshi: "", pulso: "" }
};
