# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Constitución de seglobal360_frontend

> **Versión:** 1.0.0 · **Ratificada:** 2026-11-06 · **Última enmienda:** 2026-11-06

Frontend web de **SEGlobal 360**, la plataforma B2B que conecta empresas mayoristas con proveedores de logística internacional; el primer corredor es Colombia ↔ Costa Rica. Es una aplicación **Next.js 16 (App Router)** en TypeScript que hace de **BFF** (*backend for frontend*) de la API REST de [`global360_backend`](../global360_backend/CLAUDE.md): el servidor de Next guarda la sesión en cookies `httpOnly`, llama a la API y entrega HTML. El navegador nunca ve un token ni llama a la API directamente.

Este archivo es la **constitución**: las reglas no negociables del proyecto. Toda spec, tarea y PR la cumple. Si una regla estorba, primero se enmienda (§18); no se ignora.

- **DEBE** / **NO DEBE** = obligatorio; si no se cumple, el PR no se mergea. **DEBERÍA** = recomendado; si se omite, hay que justificarlo en el PR. **PUEDE** = opcional.
- **Precedencia:** constitución > specs (`docs/specs/`) > código. El código que contradice una regla es deuda (Apéndice A) y no sienta precedente.
- **El contrato de la API lo fijan las specs del backend** (la §4 de cada una). Si el front necesita algo que la API no da, se pide como enmienda de la spec del backend y se registra en la §11 de la spec del front (`- **Backend/NN** — …`); **NO DEBE** rodearse en el front (consultas de más, datos inventados, campos que la API no envía).
- Una regla se cita por su sección: *"esto viola §6"*. Una referencia al backend se escribe `backend/07 §4` (sección de una spec), `backend/RF-07.1` o `backend/§9` (sección de su constitución).

## Mapa de la documentación

| Ruta | Qué es |
|---|---|
| `CLAUDE.md` | Esta constitución: las reglas para desarrollar el front, las fases y el glosario de la interfaz. |
| `docs/specs/NN-<nombre>.spec.md` | Una spec por área funcional: RF, rutas y pantallas, contrato consumido, estados de la UI, CA, tareas y preguntas abiertas. |
| `docs/tasks.md` | Tareas por fase, matriz de trazabilidad, épicas post-MVP y **pendientes con el backend**. **Archivo generado** por `docs/tools/gen_tasks.py` (§17): a mano solo se marcan las casillas. |
| `README.md` | Descripción del proyecto en términos simples. Se amplía a medida que hay funcionalidades (§17). |
| Maqueta | Canvas de diseño *SEGlobal 360 — Landing y rutas* (claude.ai/code/artifact/d95e052c-8cf5-4f8b-9ff2-57dab34e2bf5), con las páginas «Sitio actual», «MVP» y «Portal cliente». Es la **referencia visual**; si difiere de una spec, manda la spec. |
| `../global360_backend/` | El backend. Sus specs son la fuente del contrato de la API; `docs/admin` allí es la fuente de los requisitos de negocio. Los dos repositorios viven en la misma carpeta. |
| `../global360_frontend/` | La landing publicada hoy en www.seglobal360.com. Se migra a este repositorio (spec 03) y se archiva tras el go-live (spec 12). |

### Rutas que fija el backend

Los emails del backend enlazan a `APP_PUBLIC_URL` + estas rutas (`backend/06`, `backend/07 §5`, `backend/11`, `backend/12`). Son **contrato**: cambiarlas exige enmendar el backend.

| Ruta | Email | Spec |
|---|---|---|
| `/verify-email?token=` | `email_verification` | 04 |
| `/reset-password?token=` | `password_reset` | 04 |
| `/accept-invitation?token=` | `user_invitation` | 04 |
| `/inquiries/[id]` | `inquiry_message_to_client` | 06 |
| `/quotes/[id]` | `quote_sent` | 06 |
| `/backoffice/companies/[id]` | `company_registered` | 09 |
| `/backoffice/inquiries/[id]` | `inquiry_received`, `inquiry_assigned`, `inquiry_message_to_advisor` | 10 |
| `/backoffice/quotes/[id]` | `quote_accepted`, `quote_rejected` | 10 |

## Alcance y fases

El front tiene cuatro superficies:

| Superficie | Rutas | Quién | Specs |
|---|---|---|---|
| **Sitio público** | `/`, `/marketplace/**`, `/legal/**` | Cualquiera, sin sesión | 02, 03 |
| **Acceso** | `/login`, `/register`, `/verify-email`, `/forgot-password`, `/reset-password`, `/accept-invitation` | Cualquiera | 04 |
| **Portal de empresa** | `/portal`, `/account`, `/company/**`, `/inquiries/**`, `/quotes/**`, `/provider/**` | Usuarios de una empresa `client`, `provider` o `both`; el menú sale de sus permisos | 05, 06, 07 |
| **Backoffice** | `/backoffice/**` | Personal interno de Global 360 (usuarios sin empresa) | 08, 09, 10, 11 |

**MVP:** el mismo del backend (`backend/CLAUDE.md`, *Alcance y fases*): marketplace público → registro y validación → solicitud → asesor y conversación → cotización versionada → aceptación → cliente consolidado. Pagos, órdenes, envíos y documentos quedan fuera.

Las fases usan **los mismos códigos y nombres que las del backend**: la fase N del front se desbloquea cuando la fase N del backend tiene mergeadas las rutas que consume. Las tareas de cada fase están en `docs/tasks.md`.

| Fase | Specs | Criterio de salida | Backend que la desbloquea | Bloqueante |
|---|---|---|---|---|
| F0 Preparación del repositorio | 00 | El esqueleto de Next compila y pasan `pnpm lint`, `pnpm typecheck`, `pnpm test` y `pnpm build`. | — | — |
| F1 Plataforma base | 00, 01, 03 | El front arranca con la configuración validada, llama a la API de desarrollo con request-id y errores uniformes, el kit y los layouts existen y la landing actual está migrada. | F1 | — |
| F2 Fundación | 04, 05, 08, 09 | **Login funcional con roles**: un usuario entra, ve el menú según sus permisos, la sesión se renueva sin que lo note y sale; el superadmin gestiona catálogos, roles, empresas y usuarios desde el backoffice. | F2 | — |
| F3 Clientes y proveedores | 04, 05, 07, 08, 09 | Una empresa se registra, verifica su correo y Global 360 la valida desde el backoffice; un proveedor completa su perfil, es aprobado y publicado y publica un servicio; el administrador de la empresa gestiona sus datos y sus usuarios. | F3 | — |
| F4 Corredor y marketplace | 02, 03, 09 | La landing muestra rutas y proveedores reales, el marketplace lista y filtra, y el backoffice activa CO↔CR con su regla de comisión. | F4 | Política de comisión (para activar el corredor) |
| F5 Solicitud y cotización | 06, 10 | Un cliente crea una solicitud desde el marketplace, el asesor la toma y conversa con él, le envía la cotización y el cliente la acepta en línea. | F5 | **Política de comisión** (quién la ve) |
| F6 Backoffice y salida a producción | 11, 12 | Bandeja y reportes del backoffice, E2E de interfaz y axe en verde, presupuestos de rendimiento cumplidos y dominio migrado: **MVP en producción**. | F6 | Consentimiento de datos en el registro (`backend/07`) y responsable de Operaciones |
| **Corte del MVP** | | | | |
| F7–F12 | por escribir | Seguimiento de órdenes y envíos, documentos, pagos, leads, MFA y backoffice ampliado, i18n e integraciones. | F7–F12 | Las épicas de cada fase del backend |

Las fases post-MVP tienen sus épicas (`epic`) en `docs/tasks.md`, y cada una exige escribir y aprobar su spec antes del código (§17).

## Comandos

El proyecto usa **solo pnpm** (nunca `npm` ni `npx`; para ejecutar un paquete, `pnpm dlx`). Los comandos existen desde F0 (spec 00).

```bash
pnpm install
pnpm dev                       # http://localhost:3000 contra API_BASE_URL (backend en :5050)
pnpm build && pnpm start       # build de producción (output standalone)
pnpm lint                      # ESLint, incluidas las fronteras de §2
pnpm typecheck                 # tsc --noEmit
pnpm format:check              # Prettier
pnpm test                      # Vitest: puros, contratos, actions y componentes
pnpm test src/features/quote/model.test.ts   # un solo archivo
pnpm test:e2e                  # Playwright + axe contra el backend de desarrollo con la semilla
python3 docs/tools/gen_tasks.py docs              # regenera y valida docs/tasks.md; muestra el siguiente ID libre
python3 docs/tools/gen_tasks.py docs --renumber   # compacta los IDs; solo antes de cerrar la primera tarea
```

---

## §1. Stack

| Regla | Justificación |
|---|---|
| **DEBEN** usarse Node.js 22 LTS, pnpm 11, TypeScript 5 en modo `strict` (con `noUncheckedIndexedAccess`), **Next.js 16** (App Router, `cacheComponents`) y **React 19**. Las versiones exactas se fijan en `package.json` y `packageManager`. | Es el stack de la landing actual; el render en servidor da SEO al sitio público y permite el BFF. |
| **DEBE** leerse la guía correspondiente de `node_modules/next/dist/docs/` antes de usar una API de Next. Next 16 cambió APIs (`proxy.ts` en lugar de `middleware.ts`, `cookies()` asíncrono, `use cache`, `updateTag`, `refresh`). | El conocimiento previo de Next no es fiable para esta versión. |
| **DEBE** usarse **Tailwind CSS 4** con los tokens de §8. **NO DEBEN** usarse kits de componentes (MUI, Chakra, Ant, Radix, shadcn/ui, Headless UI) ni CSS-in-JS: el kit es propio (`shared/ui`) y se construye sobre HTML nativo. | La marca tiene un look propio y el HTML nativo (`<dialog>`, `<select>`, `<details>`) ya es accesible. |
| Dependencias aprobadas de runtime: `next`, `react`, `react-dom`, `zod` (v4: contratos y entradas), `server-only`, `lucide-react` (iconos), `country-flag-icons` (banderas). | Las mínimas para el MVP. |
| Dependencias aprobadas de desarrollo: `typescript`, `@types/*`, `tailwindcss`, `@tailwindcss/turbopack`, `eslint`, `eslint-config-next`, `prettier`, `prettier-plugin-tailwindcss`, `vitest`, `@vitejs/plugin-react`, `jsdom`, `@testing-library/react`, `@testing-library/user-event`, `@playwright/test`, `@axe-core/playwright`. | Lint, formato y tests (§12). |
| **NO DEBEN** usarse: axios ni otro cliente HTTP (se usa `fetch`), gestores de estado globales (Redux, Zustand, Jotai), librerías de formularios (react-hook-form, Formik), TanStack Query ni SWR, librerías de fechas (moment, date-fns, dayjs: se usa `Intl`), librerías de i18n en el MVP, MSW ni librerías de aserciones extra. | El servidor es la fuente de datos; los formularios usan Server Actions y `useActionState`. |
| **DEBE avisarse siempre antes de instalar una librería** (de runtime o de desarrollo, también las aprobadas en esta tabla): nombre, versión, para qué se usa en el proyecto y por qué no basta la plataforma. **No se instala sin la confirmación explícita del usuario**, y una aprobación no vale para otra librería. | El usuario decide qué entra al proyecto. |
| **DEBE explicarse cómo funciona una librería antes de escribir el primer código que la usa**: su modelo mental, la parte de su API que se va a usar y un ejemplo mínimo aplicado a este proyecto. El PR que la introduce repite esa explicación en su justificación. | Nadie mantiene código sobre una herramienta que no entiende. |
| **NO DEBE** añadirse una dependencia directa sin la aprobación anterior ni sin añadirla a esta tabla: es una enmienda MINOR. Una opción experimental de Next solo se activa si está aquí: hoy, `experimental.authInterrupts` (`forbidden()`). | Binario pequeño y mantenimiento acotado. |

## §2. Arquitectura

```
proxy.ts                         request-id, nonce de CSP, renovación de la sesión y redirección optimista (§6)
src/
  app/                           solo rutas y composición: page, layout, loading, error, not-found, forbidden, route
    (site)/                      landing, marketplace y legales: públicos y cacheables
    (auth)/                      login, registro y páginas con token
    (portal)/                    portal de empresa (cliente y proveedor)
    backoffice/                  personal interno
    api/health/route.ts          sonda del orquestador
  features/<modulo>/             una por módulo del backend que consume, con su mismo nombre
    api.ts                       server-only: llama a la API con shared/api y parsea con contracts
    contracts.ts                 esquemas zod de los DTO de la API, tipos inferidos y límites
    model.ts                     funciones puras: etiquetas de estado, derivados, permisos de UI
    actions.ts                   Server Actions ('use server'): FormData → api → ActionState
    messages.ts                  código de error → { mensaje, campo }
    components/                  componentes de la feature (Server por defecto)
  shared/
    config/                      única lectura del entorno (env.ts server-only, public-env.ts)
    api/                         cliente HTTP server-only, ApiError, ActionState, mensajes transversales
    auth/                        cookies de sesión, refresh con single-flight, sesión actual, grants, can/canIn
    ui/                          sistema de diseño: tokens en uso, componentes y layouts base (§8)
    format/                      fechas, dinero, números y unidades (§10)
    lib/                         utilidades puras sin dependencias del proyecto
```

| Regla | Justificación |
|---|---|
| **DEBE** cada feature vivir en `src/features/<modulo>/` y llamarse como el **módulo del backend** cuyo contrato consume (`inquiry`, `quote`, `company`…). Las que no consumen API llevan un nombre propio (`site`). | Una pantalla se rastrea hasta su spec del backend sin traducir nombres. |
| **DEBE** `app/` limitarse a componer: lee `params`/`searchParams`, llama al `api.ts` de las features, comprueba la sesión (§6) y renderiza componentes. **NO DEBE** llamar a `fetch`, leer `process.env` ni contener reglas de negocio. | La página es el *composition root* de su ruta. |
| **NO DEBE** una feature importar valores de otra. **PUEDE** importar solo tipos (`import type`) del `contracts.ts` de otra para nombrar lo que recibe por props. La composición entre features la hace la página: por ejemplo, la página de una solicitud pide la solicitud (`inquiry`) y su cotización (`quote`) y renderiza los componentes de las dos. | Features aisladas y reemplazables. |
| **DEBEN** llevar `import 'server-only'` `features/*/api.ts`, `shared/api`, `shared/auth` y `shared/config/env.ts`. **NO DEBE** un componente con `'use client'` importarlos. | Un token o un secreto nunca llega al bundle del navegador. |
| **DEBE** toda llamada a la API pasar por `shared/api` (base URL, cabeceras de §6, timeout, `ApiError`, parseo con zod). | Un solo punto de integración con el backend. |
| **DEBE** inyectarse por parámetro lo que una función necesita probar (el `fetch`, el reloj, los datos). **NO DEBE** haber estado de módulo mutable, salvo la memoria del single-flight del refresh (§6). | Se puede probar sin `vi.mock` de módulos propios (§12). |

**Imports permitidos.** Los verifica ESLint (`import/no-restricted-paths` y `@typescript-eslint/no-restricted-imports` con `allowTypeImports`) en `pnpm lint`.

| Módulo | PUEDE importar | NO DEBE importar |
|---|---|---|
| `src/app/**` | `features/*/{api,actions,model,messages,components}`, `shared/{auth,ui,format,lib}`, `next/*` | `shared/api` directamente, `shared/config/env` (salvo `route.ts` de health), `fetch` |
| `features/<m>/api.ts` | su `contracts.ts`, `shared/{api,auth,lib,format}`, `server-only`, `next/cache` | `components/`, `actions.ts`, otras features, `next/navigation` |
| `features/<m>/contracts.ts` | `zod`, `shared/lib`, `import type` de otro `contracts.ts` | Todo lo demás |
| `features/<m>/model.ts` | su `contracts.ts`, `shared/{format,lib}`, `shared/auth/grants` (puro) | `api.ts`, `actions.ts`, React, `next/*` |
| `features/<m>/actions.ts` | su `api.ts`, `contracts.ts`, `messages.ts`, `shared/{api,auth,lib}`, `next/cache`, `next/navigation`, `zod` | `components/`, otras features |
| `features/<m>/components/**` | su `model.ts`, `messages.ts`, `actions.ts`, `import type` de su `contracts.ts` y de otros, `shared/{ui,format,lib}`, `react`, `next/link`, `next/image`, `next/navigation` | `api.ts`, `shared/{api,auth,config}`, valores de otras features |
| `shared/ui` | `react`, `next/link`, `lucide-react`, `country-flag-icons`, `shared/lib` | `features/*`, `shared/{api,auth,config}` |
| `shared/{api,auth}` | `shared/{config,lib,format}`, `zod`, `server-only`, `next/headers`, `next/server` | `features/*`, `src/app/*`, `shared/ui` |
| `shared/{config,format,lib}` | Solo la plataforma, `zod` y entre ellos (`config` también `server-only`) | Todo lo demás |
| `proxy.ts` | `shared/{auth,config,lib}`, `next/server` | `features/*`, `src/app/*` |

**Features del MVP.** "Crea" es la spec que la introduce; "Amplían", las que le añaden rutas o acciones.

| Feature | Módulos del backend que consume | Crea | Amplían |
|---|---|---|---|
| `catalog` | `country`, `currency`, `documenttype`, `transporttype`, `service` (categorías) | 00 | 08 |
| `marketplace` | `marketplace` | 02 | 03 |
| `site` | — (contenido de la landing) | 03 | — |
| `auth` | `auth` (login, logout, verificación, restablecimiento, invitaciones) | 04 | — |
| `onboarding` | `onboarding` (registro e invitaciones) | 04 | 05, 08 |
| `user` | `user`, `person` | 05 | 08 |
| `company` · `client` | `company` · `client` | 05 | 09 |
| `rbac` | `rbac` (roles y asignaciones; `/me/grants` vive en `shared/auth`) | 05 | 08 |
| `inquiry` · `quote` | `inquiry` · `quote` | 06 | 10 |
| `provider` · `service` | `provider` · `service` | 07 | 09 |
| `audit` | `audit` | 08 | — |
| `corridor` | `corridor` (vista interna) | 09 | — |
| `report` | `report` | 11 | — |

## §3. Nombres

| Elemento | Regla | Ejemplo |
|---|---|---|
| Rutas (URL) | Inglés, kebab-case, recursos en plural, `[id]` para el UUID. Las de *Rutas que fija el backend* son contrato. | `/inquiries/[id]`, `/company/users` |
| Carpetas de `app/` | Igual que la URL; los grupos entre paréntesis | `(portal)/inquiries/[id]/page.tsx` |
| Componentes | PascalCase, un componente exportado por archivo, mismo nombre que el archivo; exportación con nombre | `QuoteCard.tsx` → `export function QuoteCard` |
| Otros módulos | Minúscula; los fijos de §2 en cada feature | `api.ts`, `model.ts`, `money.ts` |
| Funciones de `api.ts` | Verbo + recurso, como la acción del backend | `getInquiry`, `listQuotes`, `acceptQuote` |
| Server Actions | `<verbo><Recurso>Action` | `acceptQuoteAction` |
| Esquemas zod | `<recurso>Schema` y su tipo `type <Recurso> = z.infer<…>` | `inquirySchema`, `Inquiry` |
| Límites | `<RECURSO>_LIMITS` en `contracts.ts`, con los valores de la spec del backend | `INQUIRY_LIMITS.notes = 2000` |
| Permisos | El texto del backend, en constantes de `shared/auth/permissions.ts` | `PERM.quoteRespond = 'quote:respond'` |
| Hooks y utilidades | camelCase; los hooks empiezan por `use` | `formatMoney`, `useDialog` |
| Tests | `<archivo>.test.ts(x)` junto al archivo; E2E en `e2e/<flujo>.spec.ts` | `model.test.ts` |
| Variables de entorno | UPPER_SNAKE; solo las `NEXT_PUBLIC_*` llegan al navegador | `API_BASE_URL` |
| Siglas | En mayúscula dentro de identificadores | `requestID`, `APIError` |

**Glosario backend → interfaz.** En la UI (en español, tuteando) los conceptos se llaman así:

| Backend | Interfaz | Backend | Interfaz |
|---|---|---|---|
| `Corridor` | Ruta (Colombia → Costa Rica) | `Interaction` | Mensaje, conversación |
| `Inquiry` (`SOL-…`) | Solicitud | `Quote` / `QuoteVersion` (`COT-…`) | Cotización / versión |
| `CostComponent` | Concepto | Asesor (`inquiry:advise`) | Asesor de Global 360 |
| `Company` / `Client` / `Provider` | Empresa / cliente / proveedor | `Service` / `ServiceCategory` | Servicio / categoría |
| `User` / `Person` | Usuario / persona | `Role` | Rol (Administrador, Operativo) |

Las etiquetas de cada estado se definen en la spec que lo muestra y viven en el `model.ts` de su feature; nunca se muestra el valor persistido (`in_contact`).

## §4. Errores

| Regla | Justificación |
|---|---|
| **DEBE** toda respuesta no 2xx de la API convertirse en `ApiError{status, code, requestID}` en `shared/api`, con `code` sacado de `{"error": "<CODE>"}`. Los errores propios del front son `NETWORK_ERROR` (API inalcanzable o timeout) y `CONTRACT_MISMATCH` (respuesta que no cumple su esquema). | Un solo tipo de error en todo el front. |
| **DEBE** cada feature tener en `messages.ts` el texto en español de cada código que pueden devolver sus rutas, y el campo del formulario al que pertenece si lo hay. Los transversales (`INVALID_BODY`, `RATE_LIMITED`, `FORBIDDEN`, `INTERNAL_ERROR`, `NETWORK_ERROR`…) viven en `shared/api/messages.ts`. | La API devuelve un código sin campo: el front decide dónde mostrarlo. |
| **DEBE** un código sin texto mostrar el mensaje genérico con el «código de soporte» (el `requestID`). **NO DEBE** mostrarse nunca el texto crudo de la API, un stack ni un `JSON.stringify`. | Nada de jerga técnica para el usuario, y soporte puede seguir la incidencia. |
| Por status: 401 `TOKEN_EXPIRED` → renovar la sesión (§6); otro 401, o `INVALID_REFRESH_TOKEN`/`REFRESH_TOKEN_REUSED` → cerrar la sesión e ir a `/login?next=`; 403 → `forbidden()`; 404 (también el de aislamiento por empresa) → `notFound()`; 409 → mensaje del código junto al control que lo provocó; 429 → «Demasiados intentos, espera un minuto» (la API no envía `Retry-After`); 5xx o `NETWORK_ERROR` → `error.tsx` del segmento con el código de soporte. | Mismo comportamiento en todas las pantallas. |
| **DEBEN** compararse los errores por `code`, nunca por texto. | El texto no es contrato. |
| **DEBE** existir `error.tsx` en cada segmento raíz (`(site)`, `(auth)`, `(portal)`, `backoffice`) y `global-error.tsx`, `not-found.tsx` y `forbidden.tsx` en la raíz. | Ninguna pantalla en blanco. |
| **DEBE** un error loguearse una sola vez, en el servidor y en el borde (`shared/api` para 5xx, `NETWORK_ERROR` y `CONTRACT_MISMATCH`), sin datos sensibles (§11). Los componentes no loguean. | Un error, un log. |

## §5. Validación

| Tipo | Dónde | Cómo | Resultado |
|---|---|---|---|
| Pistas en el navegador: obligatorio, longitud, formato, rango | `components/` | Atributos HTML (`required`, `maxLength`, `type`, `min`, `max`, `pattern`) con los valores de `<RECURSO>_LIMITS` | El navegador avisa antes de enviar |
| Forma y tipos de la entrada de una Server Action | `actions.ts` | `zod` sobre el `FormData` (tipos, presencia, recorte, conversiones como m³ → litros) | `INVALID_BODY` local, sin llamar a la API |
| Reglas de negocio (formatos de documento, unicidad, estados, permisos) | **La API** | El front envía y traduce el código | Mensaje de `messages.ts` |
| Respuesta de la API | `api.ts` | `schema.parse` del DTO | `CONTRACT_MISMATCH` |
| Parámetros de la URL (`searchParams`, `[id]`) | `app/` | Esquema zod; un `[id]` que no es UUID es un `notFound()` sin llamar a la API | 404 o filtros por defecto |
| Entorno | `shared/config` | zod al arrancar | El proceso no arranca |

| Regla | Justificación |
|---|---|
| **La API es la autoridad.** **NO DEBE** el front bloquear un envío con una regla que la API no tiene, ni duplicar en código una regla de negocio (formato del NIT, transición de estado). Los límites de longitud y rango **PUEDEN** reflejarse como atributos HTML, definidos una sola vez en `contracts.ts` y con la sección del backend de la que salen. La única comprobación propia del front es la de un campo de confirmación que no se envía (repetir la contraseña). | Una regla en dos sitios acaba distinta. |
| **NO DEBE** enviarse a la API lo que el usuario no decide: el front no rellena IDs, estados, autores ni `companyId` ajenos en un body, y no confía en un `<input type="hidden">` para autorizar. | Evita la suplantación (`backend/§5`). |
| **DEBE** toda Server Action parsear su entrada con zod aunque el formulario sea propio. | Una Server Action es un endpoint POST público. |
| **DEBEN** parsearse las fechas de la API con un parser tolerante a la fracción de segundo (RFC 3339). | Go serializa `time.Time` con fracciones variables. |

## §6. Sesión, autenticación y autorización

| Regla | Justificación |
|---|---|
| **Cookies de sesión.** El par de `POST /auth/login` y `/auth/refresh` (`backend/05 §4`) se guarda en dos cookies `httpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, con prefijo `__Host-` fuera de local: `g360_at` (access token, `maxAge` = `expiresIn`) y `g360_rt` (refresh token, `maxAge` = `SESSION_REFRESH_MAX_AGE`). **NO DEBEN** guardarse tokens en `localStorage`, `sessionStorage`, una cookie legible desde JS ni el estado de React. | Un XSS no puede robar la sesión. |
| **Llamadas autenticadas.** Solo el servidor llama a la API, con `Authorization: Bearer <g360_at>`. El navegador nunca llama a la API: en el backend, `CORS_ALLOWED_ORIGINS` solo lista el origen del front por defensa en profundidad. | La API queda en red privada (§14). |
| **Cabeceras reenviadas.** Toda llamada lleva `X-Request-ID` (el del request entrante, generado en `proxy.ts` si falta, `^[A-Za-z0-9-]{8,64}$`), el `User-Agent` del navegador y `X-Forwarded-For` con la IP del cliente. El backend declara el CIDR del front en `TRUSTED_PROXIES`. | El rate limit y la auditoría del backend son por IP (`backend/00`): sin esto, todos los usuarios comparten la IP del BFF. |
| **Renovación solo en `proxy.ts`.** Antes de renderizar, si `g360_at` falta o vence en menos de 60 s y existe `g360_rt`, `proxy.ts` llama a `/auth/refresh`, reescribe las cookies de la respuesta y del request que sigue. Los Server Components no renuevan: no pueden escribir cookies. Si un render recibe `TOKEN_EXPIRED`, redirige a `/session/refresh?next=`, un route handler que usa el mismo mecanismo. | Next solo permite escribir cookies en `proxy`, Server Functions y route handlers. |
| **Single-flight del refresh.** La API **no tiene ventana de gracia**: reutilizar un refresh token, aunque sean dos requests en paralelo, revoca la familia entera (`backend/RF-05.3`, `CA-05.7`). Por eso `shared/auth` deduplica por hash del refresh token y memoriza el par nuevo unos 10 s para los requests paralelos que traen la cookie vieja. En el MVP el front corre en **una sola instancia** (o con afinidad de sesión); escalar horizontalmente exige antes una enmienda de `backend/05`. | Las precargas de `<Link>` y las pestañas paralelas no cierran la sesión. |
| **Fin de la sesión.** Con `INVALID_REFRESH_TOKEN` o `REFRESH_TOKEN_REUSED`, o si `GET /users/me` responde 404, se borran las cookies y una ruta privada redirige a `/login?next=`. El logout es una Server Action: `POST /auth/logout {refreshToken}` y borrar las cookies. Tras cambiar la contraseña, el backend invalida también la sesión actual: la Server Action hace un login nuevo con la contraseña nueva. | El usuario nunca queda en un estado a medias. |
| **Rutas privadas.** Toda ruta privada vive bajo `app/(portal)` o `app/backoffice`. `proxy.ts` redirige a `/login?next=` si no hay `g360_rt` (comprobación optimista), y **cada `page.tsx` privada llama a `requireSession()` o `requirePermission(perm)`** de `shared/auth`: los layouts no bastan, porque no se vuelven a renderizar al navegar. El backoffice exige además un usuario sin empresa (`companyId: null`). | Una página privada nunca se sirve sin sesión. |
| **Permisos en la UI.** `shared/auth` obtiene `GET /me/grants` una vez por request (`React.cache`) y expone `can(grants, perm)` y `canIn(grants, companyID, perm)`, que replican `Principal.Can`/`CanIn` (`backend/00 RF-00.6`; `"*"` lo concede todo). **Solo deciden qué se muestra**: la autorización la decide la API y su 403/404 se trata según §4. | Ocultar un botón no es seguridad. |
| **NO DEBE** decidirse nada por nombre de rol (`if (role === 'client_admin')`) ni codificarse una tabla rol → pantalla. El menú, los botones y las rutas dependen de permisos. | Los roles son datos que Operaciones cambia (`backend/§6`). |
| **NO DEBE** aceptarse en `next` (ni en ningún redirect) nada que no sea una ruta relativa de la propia app (empieza por `/` y no por `//`). | Evita el *open redirect*. |
| **Páginas con token** (`/verify-email`, `/reset-password`, `/accept-invitation`): la página **no llama a la API al renderizar**; el token se envía por una Server Action tras una acción del usuario o al montarse en el cliente, y luego se quita de la URL. Responden con `Referrer-Policy: no-referrer`. | Un GET no muta (§7) y los escáneres de enlaces del correo no consumen el token. |

## §7. Render, datos y mutaciones

| Capa | DEBE | NO DEBE |
|---|---|---|
| `app/**/page.tsx` | Server Component. Valida `params`/`searchParams` con zod, llama a `requireSession`/`requirePermission` si es privada, pide los datos al `api.ts` de cada feature (en paralelo con `Promise.all`) y compone componentes. Datos que dependen de la sesión dentro de `<Suspense>`. | Llamar a `fetch`, leer cookies directamente, poner un `if` de negocio, pasar a un Client Component más datos de los que muestra. |
| `features/*/api.ts` | Una función por ruta del backend. Lecturas públicas con `'use cache'` + `cacheLife` + `cacheTag('<recurso>')` y un respaldo si la API falla (la landing nunca se rompe). Lecturas privadas sin caché del servidor (por request; `'use cache: private'` solo para datos de la sesión). | Cachear en el servidor una respuesta que dependa del usuario; tragarse un error que no sea de un bloque público con respaldo. |
| `features/*/actions.ts` | `'use server'`. Firma `(prev: ActionState, formData: FormData) => Promise<ActionState>`; parsea con zod, llama al `api.ts`, traduce `ApiError` con `messages.ts` y termina con `updateTag`, `refresh()` o `redirect()`. | Decidir permisos (los decide la API), devolver el `ApiError` crudo, recibir IDs ajenos sin que la API los compruebe. |
| `features/*/components/**` | Server Components por defecto. `'use client'` solo en la hoja interactiva más pequeña (un formulario con `useActionState`, un filtro, un diálogo). Formularios con `<form action={…}>` que funcionan sin JS cuando es posible. | Pedir datos desde el cliente (`useEffect` + `fetch`), duplicar estado del servidor en el cliente. |
| URL | Los filtros, la pestaña y la paginación de un listado viven en `searchParams` (compartibles y con «atrás»). Paginación `?page=&pageSize=` hacia la API (`backend/§8`). | Guardar filtros solo en estado de React. |
| Navegación | `<Link>` con precarga por defecto en lo público; en lo privado, la precarga no puede disparar más de un refresh (§6). | `router.push` para lo que es un enlace. |
| GET | Leer. | **Mutar**: ninguna página ni route handler GET cambia estado en la API. |

## §8. Sistema de diseño y contenido

| Regla | Justificación |
|---|---|
| **DEBEN** los colores, tipografías, radios, sombras y animaciones definirse como tokens en `src/app/globals.css` (`@theme`), partiendo de los de la landing actual: `navy-950…600`, `gold-200…700`, `ivory`, `whatsapp`; fuentes Inter (texto) y Montserrat (títulos) con `next/font`; utilidades `text-gold-gradient` y `text-gold-gradient-deep`. **NO DEBEN** escribirse valores hex, `rgb()` ni tamaños arbitrarios (`text-[13px]`) en los componentes. | Una marca coherente que se cambia en un solo sitio. |
| **DEBE** todo control reutilizable vivir en `src/shared/ui` (botones, campos, tablas, diálogos, insignias de estado, paginación, layouts base…; spec 01) y **NO DEBEN** las features crear variantes propias de un componente que ya existe. | Consistencia y accesibilidad en un solo sitio. |
| **DEBE** la interfaz funcionar desde 360 px de ancho sin scroll horizontal (las tablas anchas se desplazan dentro de su caja), con objetivos táctiles de al menos 44 px. | Muchos usuarios entran desde el celular. |
| **DEBE** la maqueta tomarse como referencia visual. Una pantalla sin maqueta (portal del proveedor, backoffice) se construye con el kit y los patrones del portal del cliente. | Coherencia sin bloquear el desarrollo por diseño. |
| **DEBEN** los textos de la interfaz estar en español (es-CO), tuteando, en tono cercano y profesional, en frases cortas. Un mensaje de error dice qué pasó y qué hacer. Un estado vacío explica qué va a aparecer ahí y cómo conseguirlo. | La voz de la maqueta («Tu empresa, sin fronteras.»). |
| **NO DEBEN** inventarse datos en la UI: si la API no da un dato (nombre del asesor, precio), la pantalla usa el texto genérico que diga su spec. | La interfaz no promete lo que el sistema no sabe. |
| **NO DEBE** mostrarse ningún precio ni comisión fuera de una cotización (`backend/10`, `backend/12 RF-12.8`). | Gerencia: el valor sale de la cotización del asesor. |

## §9. Accesibilidad

| Regla | Justificación |
|---|---|
| **DEBE** cumplirse WCAG 2.2 AA: contraste de al menos 4,5:1 (3:1 para texto grande e iconos), foco visible en todo control, orden de tabulación lógico y navegación completa con teclado. | Requisito de calidad del MVP (spec 12). |
| **DEBE** usarse HTML semántico: `<button>` para acciones, `<a href>` para navegación, `<label>` asociado a cada campo, un `<h1>` por página, landmarks (`header`, `nav`, `main`, `footer`) y un enlace «Saltar al contenido». **NO DEBE** ponerse un `onClick` en un `div` o `span`. | Los lectores de pantalla y el teclado funcionan sin trucos. |
| **DEBEN** los errores de un formulario anunciarse (`aria-live="polite"` en el resumen y `aria-describedby` + `aria-invalid` en el campo), y el foco ir al primer campo con error tras enviar. | El usuario sabe qué corregir. |
| **DEBEN** los iconos decorativos llevar `aria-hidden`, los botones de solo icono un `aria-label`, las imágenes con contenido un `alt` útil y las animaciones respetar `prefers-reduced-motion`. | Sin ruido ni mareos. |
| **DEBE** la E2E pasar axe en cada pantalla sin violaciones *serious* ni *critical* (§12). | Se verifica, no se supone. |

## §10. Formatos

| Regla | Justificación |
|---|---|
| **DEBEN** formatearse las fechas solo con las funciones de `shared/format` (`Intl.DateTimeFormat('es-CO')`), en la zona horaria del usuario: la cookie `tz` que fija el navegador al cargar, o `America/Bogota` si no existe. Las páginas públicas cacheadas usan `America/Bogota`. Las fechas sin hora (`desiredShipDate`, `AAAA-MM-DD`) se muestran sin convertir de zona. | Una fecha UTC mal convertida cambia de día entre CO y CR. |
| **DEBE** el dinero manejarse como `{amount, currency}` en unidades menores (`backend/§9`), y formatearse con `formatMoney` usando `decimals` y `symbol` del catálogo `GET /currencies` (`US$ 2.800,00`). **NO DEBE** usarse `number` con decimales para un monto: la conversión a texto y desde texto se hace con aritmética de enteros sobre cadenas. | Sin errores de redondeo. |
| **DEBE** un monto escrito por el usuario convertirse a unidades menores con `parseMoneyInput(texto, decimals)`: sin separador de miles, `,` o `.` como separador decimal y como mucho `decimals` decimales; si no, error de campo. | Una sola interpretación de «2.800». |
| **NO DEBE** el front calcular totales, comisiones, vigencias ni estados efectivos: muestra lo que devuelve la API. | El cálculo vive en el backend (`backend/12`). |
| **DEBEN** las unidades convertirse en `actions.ts` con funciones puras: el volumen se pide en m³ y se envía en litros enteros (1 m³ = 1000 L), el peso en kg enteros. | El contrato de `backend/11` va en litros enteros. |
| **DEBEN** los nombres de países, monedas, tipos de transporte, tipos de documento y categorías resolverse con los catálogos públicos (feature `catalog`, en caché); un ID sin nombre en el catálogo se muestra como «—». | La API devuelve IDs y códigos. |

## §11. Seguridad

| Regla | Justificación |
|---|---|
| **DEBE** `proxy.ts` fijar en toda respuesta: `Content-Security-Policy` con nonce por request (`default-src 'self'`, `script-src 'self' 'nonce-…' 'strict-dynamic'`, `img-src 'self' data: https:`, `frame-ancestors 'none'`, `form-action 'self'`, `base-uri 'self'`, `object-src 'none'`), `Strict-Transport-Security` fuera de local, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` (`no-referrer` en las páginas con token) y `Permissions-Policy` restrictiva. | Defensa en profundidad contra XSS, clickjacking y fugas por Referer. |
| **NO DEBE** usarse `dangerouslySetInnerHTML`, salvo para el JSON-LD con `<` escapado como `<`. **NO DEBE** renderizarse HTML que venga de la API: todo texto del usuario se muestra como texto. | XSS. |
| **NO DEBE** haber secretos en el código, en `NEXT_PUBLIC_*` ni con valor por defecto. Solo `NEXT_PUBLIC_*` llega al navegador, y nunca lleva un token, una URL interna ni una clave. | El bundle del cliente es público. |
| **NO DEBEN** loguearse ni enviarse a terceros contraseñas, tokens, cookies, la cabecera `Authorization`, cuerpos de request ni los `?token=` de las páginas con token. | Superficie mínima (`backend/§11`). |
| **NO DEBEN** ponerse datos personales en la URL (emails, documentos, nombres). Los filtros de los listados usan IDs y estados. | Las URLs quedan en historiales, logs y Referer. |
| **DEBE** la adquisición (UTM y `referrer`) guardarse en una cookie propia de la primera visita, sin datos personales, con el `referrer` reducido a su origen y cada valor recortado a 100 caracteres (`backend/07`). | Atribución sin rastreo de más. |
| **DEBEN** las imágenes con URL externa (`logoUrl` del proveedor) mostrarse con `<img>` (con `referrerPolicy="no-referrer"` y `loading="lazy"`) dentro de la CSP `img-src https:`. | La URL la decide el proveedor; `next/image` no conoce el dominio. |
| **DEBE** fijarse `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` y un `cacheHandler` compartido antes de correr más de una instancia (§6). | Las Server Actions y la caché deben valer entre instancias. |
| **DEBE** revisarse `pnpm audit --prod` antes de cada salida a producción; una vulnerabilidad alta o crítica bloquea el despliegue. | Cadena de suministro. |

## §12. Tests

| Regla | Justificación |
|---|---|
| **DEBEN** usarse Vitest (entorno `node` para lo de servidor y `jsdom` para componentes), Testing Library para los componentes y Playwright para la E2E. Los stubs se escriben a mano y se inyectan por parámetro. **NO DEBE** usarse `vi.mock` sobre módulos del proyecto; solo **PUEDE** usarse para `server-only` y `next/*`. | Sin librerías de mocks (§1) y con funciones probables (§2). |
| **Puros** (DEBE): tests table-driven de `model.ts`, `shared/format` (fechas, dinero, unidades), `shared/auth/grants` (`can`/`canIn`) y de cada `contracts.ts` (acepta el ejemplo de la spec del backend, rechaza un campo que falta). | Las reglas de presentación quedan protegidas. |
| **Actions y API** (DEBE): cada Server Action con un `api` stub: entrada inválida, éxito y cada código que su spec mapea a un campo. `shared/api` con un `fetch` stub: cabeceras de §6, `ApiError`, `CONTRACT_MISMATCH`, `NETWORK_ERROR`. El single-flight del refresh con dos llamadas en paralelo. | El contrato con el backend se prueba en un sitio. |
| **Componentes** (DEBERÍA): los formularios muestran el error de cada código en su campo, y los controles condicionados por permisos aparecen o no según `grants`. Se consulta por rol y nombre accesible (`getByRole`). | Lo que ve el usuario, sin acoplarse al DOM. |
| **E2E** (DEBE en los flujos críticos de cada spec): `e2e/`, contra el backend de desarrollo con la semilla y `NOTIFIER=file` (los enlaces de los emails se leen de `tmp/mail/`), con axe en cada pantalla visitada (§9). Se saltan con un aviso si la API no responde. | El front se prueba contra la API real, no contra una imitación. |
| **DEBE** cada test citar en un comentario el `CA-NN.x` que verifica (no en su nombre). | Trazabilidad spec → test. |

## §13. Configuración

| Regla | Justificación |
|---|---|
| **DEBE** el entorno leerse **solo** en `src/shared/config`: `env.ts` (server-only, validado con zod al arrancar) y `public-env.ts` (solo `NEXT_PUBLIC_*`). Ningún otro módulo lee `process.env`. | Un único punto de configuración. |
| **DEBE** faltar una variable obligatoria impedir el arranque. Los valores por defecto viven en `env.ts`. | Falla rápido. |
| **NO DEBEN** commitearse `.env` ni `.env.*`, salvo `.env.example`. Toda variable nueva se añade a `.env.example` y a esta tabla en el mismo PR. | Configuración documentada. |

| Variable | Obligatoria | Por defecto | Notas |
|---|---|---|---|
| `API_BASE_URL` | Sí | — | Base de la API con el prefijo: `http://localhost:5050/api/v1`. En producción, la dirección **privada** del backend |
| `APP_PUBLIC_URL` | Sí | — | URL pública del front. **Debe coincidir con `APP_PUBLIC_URL` del backend**, que la usa en los enlaces de los emails |
| `NEXT_PUBLIC_SITE_URL` | Sí | — | La misma URL, para metadatos, `sitemap` y Open Graph |
| `SESSION_COOKIE_SECURE` | No | `true` | `false` solo en local con http; con `false` las cookies van sin `__Host-` |
| `SESSION_REFRESH_MAX_AGE` | No | `168h` | Igual a `REFRESH_TOKEN_TTL` del backend |
| `API_TIMEOUT` | No | `10s` | Timeout de cada llamada a la API |
| `PUBLIC_REVALIDATE` | No | `300s` | Vida de la caché de los datos públicos (§7) |
| `LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, `error` |
| `NEXT_PUBLIC_WHATSAPP_NUMBER` | Sí | — | Solo dígitos con indicativo (`573005561093`) |
| `NEXT_PUBLIC_WHATSAPP_MESSAGE` | No | Texto de la landing | Mensaje prellenado |
| `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` | Con más de una instancia | — | Clave de 32 bytes en base64, igual en todas las instancias (§11) |

## §14. Operación y rendimiento

| Regla | Justificación |
|---|---|
| **DEBE** el front desplegarse como contenedor Node (`output: 'standalone'`) **en la misma red que el backend**, detrás del mismo proxy TLS. La API no se expone a internet: solo la llama el BFF. | Superficie mínima y una IP de cliente fiable (§6). |
| **DEBE** existir `GET /api/health`, pública: 200 si el proceso responde y la API contesta a `/health` con un timeout corto, y 503 si no. | Sondas del orquestador. |
| **DEBEN** los logs del servidor ser JSON en una línea a stdout, con nivel, mensaje, `requestId`, ruta (la plantilla, no la URL con parámetros) y duración de las llamadas a la API. **NO DEBEN** incluir cabeceras, cookies, cuerpos ni `searchParams` con datos (§11). | Una incidencia se sigue de punta a punta junto con el log del backend. |
| **DEBEN** medirse las Web Vitals con `useReportWebVitals` hacia el log del servidor. Presupuestos: LCP < 2,5 s y CLS < 0,1 en la landing y el marketplace (móvil, p75), e INP < 200 ms en el portal. | Rendimiento observable sin analítica de terceros. |
| **NO DEBEN** añadirse scripts de analítica o de terceros sin enmendar esta constitución (dependencia, CSP y aviso de cookies). | Privacidad y CSP. |
| **DEBEN** existir ambientes separados (desarrollo, pruebas y producción), cada uno contra su backend y con sus secretos. | Espejo de `backend/§14`. |

## §15. Idioma, estilo y comentarios

| Elemento | Idioma |
|---|---|
| Identificadores, nombres de archivo, rutas, claves de JSON, logs | Inglés |
| Textos de la interfaz, comentarios, documentación (`docs/`), specs, commits y PR | Español |

| Regla | Justificación |
|---|---|
| **DEBE** el código pasar `pnpm typecheck`, `pnpm lint` y `pnpm format:check` sin avisos. **NO DEBEN** usarse `any`, `@ts-ignore`, `@ts-expect-error` sin motivo en el mismo comentario, ni `as` para afirmar el tipo de un dato externo (se parsea con zod). | El compilador trabaja para nosotros. |
| **DEBE** todo export de `shared/` y de `features/*/{api,model,actions}.ts` tener un comentario de documentación que empiece por su nombre. **DEBE** todo comentario describir de forma concisa qué hace lo que comenta, sin explicar el porqué, en **2 líneas como máximo** de hasta 100 columnas. | Se lee de un vistazo; el porqué va en la spec o en el PR. |
| **NO DEBEN** los comentarios citar tareas (`G360F-xxxx`), specs, `RF`/`CA` ni secciones de esta constitución, salvo el `CA` de cada test (§12) y las excepciones de §18. **NO DEBE** dejarse código comentado. | La trazabilidad vive en las specs, los commits y los PR. |

Un comentario de más de 2 líneas es motivo de rechazo. Esta comprobación DEBE salir vacía:

```bash
find src e2e proxy.ts -name '*.ts' -o -name '*.tsx' | xargs awk 'FNR==1{n=0} /^[[:space:]]*(\/\/|\* )/{if(++n==3) print FILENAME":"FNR; next} {n=0}'
```

Una página privada sin comprobación de sesión es motivo de rechazo (§6). Esta comprobación DEBE salir vacía:

```bash
find 'src/app/(portal)' src/app/backoffice -name page.tsx | xargs grep -L -E 'require(Session|Permission)\('
```

## §16. Ramas y commits

| Regla | Justificación |
|---|---|
| Se trabaja en ramas `G360F-xxxx-<slug>` y se integra a `main` por PR. | `main` siempre compila. |
| **DEBE** el commit seguir el formato `[G360F-xxxx] <tipo>: descripción en español`, con el tipo de Conventional Commits en inglés (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`) y la descripción en minúscula y sin punto final. Ejemplo: `[G360F-0042] feat: se añade el detalle de la solicitud`. | Cada commit apunta a su tarea. |
| Los commits los hace el usuario: Claude no hace commit ni push si no se le pide. `.claude/` no se versiona; `CLAUDE.md` sí. | Control humano del historial. |

## §17. Proceso SDD (Spec-Driven Development)

| Regla | Justificación |
|---|---|
| **El SDD tiene tres documentos**: esta constitución, las specs de `docs/specs/` y `docs/tasks.md` (generado). **NO DEBEN** crearse índices ni otros documentos de proceso aparte. | Una sola fuente de verdad por tema. |
| **NO DEBE** escribirse código de producción sin una spec **Aprobada**. Una spec pasa a *Aprobada* cuando sus preguntas abiertas ya no bloquean ningún RF **y** las rutas del backend que consume están en una spec del backend *Aprobada* o *Implementada*. Pasa a *Implementada* cuando todas sus tareas están mergeadas. | La spec es el contrato, y el del backend va primero. |
| **DEBEN** las specs llamarse `NN-<nombre>.spec.md` y seguir la plantilla de abajo. `NN` es el prefijo de sus requisitos (`RF-NN.x`) y criterios (`CA-NN.x`), propios de este repositorio: un RF del backend se cita siempre como `backend/RF-NN.x`. | Todas se leen igual y no se confunden con las del backend. |
| **DEBEN** las tareas definirse en la tabla *Tareas* de su spec, con un ID `G360F-xxxx`, una fase (F0–F12) y un tipo: `impl`, `test` u `ops`. Las épicas post-MVP (`epic`) se declaran en `EXTRA` dentro de `docs/tools/gen_tasks.py`. Los IDs van en **orden secuencial por spec** (spec 00 primero; dentro de cada spec, por fase y por fila), sin saltos, y una tarea solo depende de tareas con número menor. Mientras ninguna tarea esté cerrada, los IDs se compactan con `gen_tasks.py docs --renumber`. Desde la primera casilla `[x]` son estables y una tarea nueva toma el siguiente ID libre. | El ID es el ticket del commit, y el orden de la lista es el orden de trabajo. |
| **DEBE** cumplirse la trazabilidad que valida `gen_tasks.py` (código 0): IDs, `RF` y `CA` únicos y definidos en su spec; un RF se escribe `- **RF-NN.x** — …` y un CA `- **CA-NN.x** (RF-NN.y) — Dado…, cuando…, entonces…`; toda tarea `impl` u `ops` cita un `RF` y toda `test` un `CA`; todo RF tiene tarea `impl`/`ops`, tarea `test` y CA; todo CA tiene tarea `test`; dependencias existentes, sin ciclos, sin apuntar a una fase posterior ni a un número mayor. | Requisito → tarea → commit → test. |
| **DEBE** cada hueco del contrato de la API escribirse en la §11 de la spec como `- **Backend/NN** — <qué falta>. Por defecto: <qué hace el front mientras tanto>.` `gen_tasks.py` los reúne en *Pendientes con el backend* de `docs/tasks.md`. | Una lista viva de lo que hay que pedir al backend, sin duplicarla. |
| **DEBE** `docs/tasks.md` regenerarse con `python3 docs/tools/gen_tasks.py docs` cada vez que cambia una tabla *Tareas* o un pendiente con el backend, y nunca editarse a mano salvo las casillas `[x]`. | La lista no se separa de las specs. |
| **DEBE**, si cambia un comportamiento, actualizarse primero la spec y sus tareas, y después el código. Dentro de una feature se escribe de dentro hacia fuera: `contracts.ts` → `api.ts` → `model.ts` → `actions.ts`/`messages.ts` → `components/` → `app/`. | La documentación no se queda atrás. |
| **DEBE** cada PR citar sus tareas, sus `RF` y su spec, y marcar en `docs/tasks.md` la casilla de las tareas que cierra. | Revisión contra el contrato y avance visible. |
| **DEBE** `README.md` describir el proyecto en términos simples y ampliarse en el PR que añade algo que se puede usar o levantar. | Lo lee cualquiera. |

**Plantilla de spec**

```markdown
# Spec NN — <Nombre> (`<feature>`)

| | |
|---|---|
| Estado | Borrador · Aprobada · Implementada |
| Features | `src/features/<feature>`, … |
| Rutas | `/…` |
| Backend | `backend/NN` (estado), … |
| Depende de | Spec 00, … |

## 1. Resumen y alcance
## 2. Origen                          (artboards de la maqueta y specs del backend de las que sale cada requisito)
## 3. Requisitos funcionales          (- **RF-NN.x** — …)
## 4. Rutas y pantallas               (tabla Ruta | Acceso | Artboard | RF)
## 5. Contrato consumido              (tabla Endpoint | backend/NN §4 | Uso; tabla código → mensaje y campo)
## 6. Estados y reglas de la interfaz (etiquetas de estado, permisos que muestran u ocultan, vacíos, cargas)
## 7. Componentes, datos y caché
## 8. Accesibilidad y SEO
## 9. Criterios de aceptación         (- **CA-NN.x** (RF-NN.y) — Dado…, cuando…, entonces…)
## 10. Tareas                         (| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |)
## 11. Fuera de alcance y preguntas abiertas   (cada pregunta con su valor por defecto; huecos como - **Backend/NN** — …)
```

**Checklist antes de mergear**

- [ ] `pnpm typecheck`, `pnpm lint`, `pnpm format:check`, `pnpm test` y `pnpm build` limpios; `pnpm test:e2e` en verde si se tocó un flujo crítico.
- [ ] Las comprobaciones de comentarios y de páginas privadas (§15) salen vacías.
- [ ] Las librerías nuevas se avisaron y se explicaron antes de instalarlas (§1), y están en la tabla de §1.
- [ ] Cada código de error nuevo que puede llegar a la pantalla tiene su texto en `messages.ts`.
- [ ] Los controles nuevos usan `shared/ui` y pasan axe; no hay hex ni tamaños arbitrarios.
- [ ] Las variables nuevas están en `.env.example` y en §13.
- [ ] `gen_tasks.py` pasa, `docs/tasks.md` está regenerado y las casillas de las tareas cerradas están marcadas.
- [ ] `README.md` está actualizado si el PR añade algo que se puede usar o levantar.
- [ ] Si el PR toca una regla de esta constitución, la enmienda va en el mismo PR.

## §18. Gobierno

| Regla | Justificación |
|---|---|
| Toda enmienda es un PR que modifica este archivo, explica el motivo y actualiza la versión, la fecha de *Última enmienda* y el historial. Versionado: **MAJOR** si se quita o redefine un principio; **MINOR** si se añade una regla o una dependencia; **PATCH** si se cambia la redacción sin cambiar el significado. | La regla cambia de forma visible. |
| Una excepción puntual se documenta junto al código y se aprueba en la revisión: `// constitución: excepción §7 — <motivo>`. Una excepción que se repite indica que la regla necesita una enmienda. | Excepciones visibles y raras. |
| Un cambio de la constitución del backend que afecte al contrato (formato de errores, sesión, paginación, dinero) obliga a revisar esta en el mismo ciclo. | Los dos repositorios no se separan. |
| Lo que hoy incumple esta constitución está en el Apéndice A. Cuando se corrige una entrada, se borra en el mismo PR (enmienda PATCH). | La deuda no sienta precedente. |

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-11-06 | Primera versión, a partir de la maqueta del canvas, de la landing actual (`global360_frontend`) y de las specs 00–14 del backend: Next.js 16 como BFF con sesión en cookies `httpOnly`, kit de UI propio con Tailwind 4, despliegue en contenedor junto a la API, backoffice en la misma aplicación, fases alineadas con el backend, IDs `G360F-xxxx` y aviso y explicación obligatorios antes de instalar una librería |

## Apéndice A — Deuda conocida

| # | Regla | Ubicación | Desviación | Se corrige en |
|---|---|---|---|---|
