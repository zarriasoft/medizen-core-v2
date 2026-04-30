from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Assistant (Local)"]
)

# Configuramos el cliente de OpenAI para que se comunique con Ollama localmente
# Usamos un valor ficticio en api_key porque la libreria lo exige, pero Ollama lo ignora.
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # pragma: allowlist secret
)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_with_ai(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="llama3", # Este es el modelo que instalarás con `ollama run llama3`
            messages=[
                {"role": "system", "content": "Eres un amable y experto asistente médico para la plataforma Medizen."},
                {"role": "user", "content": request.message}
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        # Mostramos un error util si Ollama no esta encendido
        error_msg = str(e)
        if "Connection" in error_msg or "Connect" in error_msg:
            detail = "Ollama no está funcionando o no has descargado el modelo. Asegúrate de ejecutar Ollama e instalar llama3. Detalles: " + error_msg
        else:
            detail = error_msg
        raise HTTPException(status_code=500, detail=detail)
