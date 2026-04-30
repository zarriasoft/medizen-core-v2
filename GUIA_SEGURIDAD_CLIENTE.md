# MediZen Core v2 — Acciones de Seguridad Pendientes
## Guía para el cliente — Abril 2026

Estas son las únicas tareas que requieren acceso a las cuentas cloud.
El resto del plan de trabajo (Fases 1-3) ya está implementado en el código.

---

## 1. REGENERAR API KEY DE GOOGLE GEMINI (URGENTE)

La key actual está visible en el código fuente. Cualquiera con acceso al repo
puede usarla y generar costos a tu nombre.

**Pasos:**
1. Entrá a https://aistudio.google.com/apikey con tu cuenta Google
2. Buscá la key que empieza con `AIzaSyBd43HX6...`
3. Clic en el ícono de recargar (Regenerate)
4. Copiá la nueva key generada

**Después:**
- **Render.com** (backend): Entrá al dashboard, Settings → Environment → agregá
  `GEMINI_API_KEY=nueva-key-aqui`
- **Vercel** (frontends): Settings → Environment Variables → agregá
  `GEMINI_API_KEY=nueva-key-aqui`
- **Eliminá** el archivo `v2/frontend/.env.local` del proyecto (ya está en .gitignore)

---

## 2. CAMBIAR CONTRASEÑA DE NEON POSTGRESQL

**Pasos:**
1. Entrá a https://console.neon.tech
2. Seleccioná el proyecto `org-bold-king-45208432`
3. Settings → Database → Reset Password
4. Copiá la nueva contraseña

**Después:**
- **Render.com** → Settings → Environment → actualizá `DATABASE_URL` con la nueva
  contraseña. El formato es:
  ```
  postgresql://neondb_owner:NUEVA_PASSWORD@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
  ```

---

## 3. VERIFICAR TOKENS DE VERCEL

**Pasos:**
1. Entrá a https://vercel.com/dashboard
2. Seleccioná cada proyecto (medizen-frontend, patient-frontend)
3. Settings → Git → Connected Git Repository
4. Si hay tokens OIDC, regeneralos con el botón correspondiente

---

## 4. CONFIGURAR SECRET_KEY EN PRODUCCIÓN

La clave JWT (para firma de tokens de sesión) necesita ser robusta en producción.

**Generar una clave segura:**
- En Windows PowerShell ejecutá: `[System.Convert]::ToBase64String((1..32 | ForEach { Get-Random -Maximum 256 }))`
- O usá un generador online como https://randomkeygen.com (504-bit WPA Key)

**Después:**
- **Render.com** → Settings → Environment → agregá `SECRET_KEY=clave-generada`
- **NO la pongas en ningún archivo del proyecto**

---

## 5. LIMPIEZA FINAL DEL REPOSITORIO

Eliminar estos archivos que contienen contraseñas de ejemplo (no son secretos
reales de producción, pero conviene quitarlos):

| Archivo | Contenido a eliminar |
|---|---|
| `v2/backend/.env` | `SECRET_KEY=dev-key-change-me-in-production` |
| `v2/frontend/.env.local` | `GEMINI_API_KEY=AIzaSy...` |
| `v2/backend/seed_neon.py` | `password="adminpassword"` (líneas 47, 51) |

> Archivos como `reset_admin.py` y `create_initial_user.py` contienen
> contraseñas de ejemplo solo para desarrollo local. Si se despliegan
> a producción, eliminarlos del servidor.

---

## RESUMEN DE CUENTAS INVOLUCRADAS

| Servicio | URL | Qué hacer |
|---|---|---|
| Google AI Studio | aistudio.google.com/apikey | Regenerar API Key Gemini |
| Neon PostgreSQL | console.neon.tech | Reset password |
| Vercel | vercel.com/dashboard | Verificar/regenerar tokens |
| Render.com | dashboard.render.com | Actualizar variables de entorno |
| GitHub | github.com/zarriasoft/medizen-core-v2 | Hacer commit de la limpieza |

---

## VERIFICACIÓN POST-CAMBIOS

Después de rotar todas las credenciales, verificar que:

1. El backend en Render arranca sin errores (revisar logs)
2. Los frontends en Vercel cargan correctamente
3. La funcionalidad de IA (Gemini) sigue operativa
4. El login de pacientes y administradores funciona
5. Las citas y membresías se crean correctamente

---

**¿Dudas?** El equipo técnico puede asistir en la ejecución de estos pasos.
