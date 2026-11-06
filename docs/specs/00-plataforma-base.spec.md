# Spec 00 — Plataforma base (`shared/*`, `catalog`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/shared/{config,api,auth,format,lib}`, `src/features/catalog`, `proxy.ts`, `src/app/api/health`, `src/app/session/refresh` |
| Rutas | `/api/health`, `/session/refresh` |
| Backend | `backend/00` (Implementada), `backend/02` (Implementada), `backend/03` (Implementada), `backend/05` (Implementada), `backend/08` (categorías, Implementada) |
| Depende de | — (sus tareas F0 preparan el repositorio) |

## 1. Resumen y alcance

Es la base sobre la que se construye todo el front: el repositorio y sus herramientas, la configuración, el cliente de la API del lado del servidor, el manejo uniforme de errores, la sesión en cookies con su renovación, los permisos para la interfaz, las cabeceras de seguridad, los catálogos públicos y los formatos de fecha, dinero y unidades.

No incluye el sistema de diseño ni los layouts (spec 01), ni ninguna pantalla de negocio. Las pantallas de login y logout son de la spec 04: esta spec solo da las piezas de sesión que esas pantallas usan.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Stack, scripts y estructura | Constitución §1, §2 y *Comandos*; landing actual (`../global360_frontend`: Next 16.4, Tailwind 4, pnpm 11) |
| Formato de error, request-id, paginación, rate limit e IP del cliente | `backend/00 §4` y RF-00.3, RF-00.6, RF-00.10, RF-00.11 |
| Par de tokens, refresh rotatorio sin gracia, logout, Guard | `backend/05 §4` y `backend/RF-05.3`, `CA-05.5`, `CA-05.7` |
| `GET /me/grants`, `Can`/`CanIn` | `backend/03 §4` (RF-03.7) y `backend/00` (RF-00.6) |
| Catálogos públicos | `backend/02 §4` y `backend/08 §4` (categorías de servicio) |
| Dinero en unidades menores y decimales del catálogo | `backend/§9`, `backend/02 §5` |
| Notas de la maqueta: «guardar los tokens en cookies httpOnly desde Next», «la landing nunca se rompe» | Artboards `MvpLogin` y `MvpLanding` (notas `nota-login` y `nota-bloques`) |

## 3. Requisitos funcionales

- **RF-00.1** — Repositorio y herramientas.
  - Proyecto Next.js 16 con `src/`, App Router, TypeScript `strict` + `noUncheckedIndexedAccess`, Tailwind 4 y pnpm 11 (`packageManager`). Cada dependencia se instala con el aviso y la explicación de constitución §1.
  - `next.config.ts`: `cacheComponents: true`, `experimental.authInterrupts: true`, `output: 'standalone'`, `poweredByHeader: false` y `typedRoutes` si la versión lo admite.
  - Scripts: `dev`, `build`, `start`, `lint`, `typecheck`, `format`, `format:check`, `test`, `test:e2e`.
  - ESLint con `eslint-config-next` y las reglas de fronteras de constitución §2 (`import/no-restricted-paths`, `@typescript-eslint/no-restricted-imports` con `allowTypeImports`), `no-explicit-any` y `ban-ts-comment`. Prettier con `prettier-plugin-tailwindcss`.
  - Vitest con dos proyectos (`node` para `*.test.ts` y `jsdom` para `*.test.tsx`), Testing Library y Playwright con `@axe-core/playwright`. `e2e/` arranca con un helper que salta las pruebas si `API_BASE_URL/../health` no responde.
  - `.gitignore` (incluye `.env*` salvo `.env.example`, `.next`, `coverage`, `playwright-report`, `test-results`), `.env.example` con las variables de constitución §13 y `README.md` inicial.
- **RF-00.2** — Configuración.
  - `shared/config/env.ts` (server-only) valida con zod las variables de constitución §13 al primer uso y exporta `env` tipado; los valores por defecto viven ahí. Una obligatoria ausente o inválida (URL mal formada, duración que no parsea) lanza un error que impide arrancar con el nombre de la variable, sin su valor.
  - `shared/config/public-env.ts` expone solo las `NEXT_PUBLIC_*`.
  - Las duraciones (`168h`, `10s`, `300s`) se parsean con una función pura de `shared/lib`.
- **RF-00.3** — Cliente de la API (`shared/api/client.ts`, server-only).
  - `apiRequest({method, path, query?, body?, auth, schema})` construye la URL con `API_BASE_URL`, serializa el body como JSON y añade `Accept`, `Content-Type`, `X-Request-ID`, `User-Agent` y `X-Forwarded-For` (constitución §6) leídos del request entrante con `headers()`; con `auth: 'user'`, también `Authorization: Bearer <g360_at>`.
  - Timeout con `AbortSignal.timeout(API_TIMEOUT)`; `cache: 'no-store'` en toda llamada con `auth: 'user'`.
  - Respuesta 2xx: `schema.parse` del JSON (o nada en 204). No 2xx: `ApiError{status, code, requestID}` con el `code` de `{"error"}` (si el cuerpo no lo trae, `INTERNAL_ERROR`) y el `X-Request-ID` de la respuesta. Fallo de red o timeout: `ApiError` con `NETWORK_ERROR`. Esquema que no cumple: `CONTRACT_MISMATCH`.
  - `apiPublic(...)` es la variante para lecturas públicas cacheables: sin cookies ni cabeceras del request (puede correr dentro de `'use cache'`).
  - Las páginas se piden con un helper `pageSchema(itemSchema)` para `{items, page, pageSize, total}`.
- **RF-00.4** — Errores y mensajes.
  - `ActionState` = `{status: 'idle'}`, `{status: 'success', message?}` o `{status: 'error', code, message, field?, requestID?}`.
  - `toActionState(err, messages)` traduce un `ApiError` con el mapa de la feature y, si el código no está, con `shared/api/messages.ts`; si tampoco, el mensaje genérico con el código de soporte. Un error que no es `ApiError` se loguea y se traduce como `INTERNAL_ERROR`.
  - `shared/api/messages.ts` tiene el texto de los códigos transversales: `INVALID_BODY`, `INVALID_ID`, `INVALID_QUERY`, `UNAUTHENTICATED`, `TOKEN_EXPIRED`, `FORBIDDEN`, `ROUTE_NOT_FOUND`, `RATE_LIMITED`, `INTERNAL_ERROR`, `NETWORK_ERROR`, `CONTRACT_MISMATCH`.
  - `handlePageError(err)` para las páginas: 404 → `notFound()`, 403 → `forbidden()`, 401 → redirección a `/session/refresh?next=` (si era `TOKEN_EXPIRED`) o a `/login?next=`; el resto se relanza al `error.tsx` con el `requestID` en el mensaje, para que el log del servidor una el `digest` que muestra la página con el request-id de la API.
  - Raíz: `global-error.tsx`, `not-found.tsx` y `forbidden.tsx` con el layout mínimo y un enlace al inicio. Los `error.tsx` de cada segmento llegan con sus layouts (spec 01).
- **RF-00.5** — Cookies de sesión (`shared/auth/session.ts`).
  - `setSession(pair)` escribe `g360_at` (`maxAge` = `expiresIn`) y `g360_rt` (`maxAge` = `SESSION_REFRESH_MAX_AGE`) con `httpOnly`, `sameSite: 'lax'`, `path: '/'` y, si `SESSION_COOKIE_SECURE`, `secure` y el prefijo `__Host-`. `clearSession()` las borra. Solo se llaman desde Server Actions, route handlers o `proxy.ts`.
  - `readAccessExpiry(token)` decodifica (sin verificar) el `exp` y el `cid` del JWT para decidir la renovación y el inicio del usuario; la verificación es de la API.
  - `signIn(email, password)` llama a `POST /auth/login` y guarda el par con `setSession`; devuelve el `cid` o lanza el `ApiError`. `signOut()` llama a `POST /auth/logout {refreshToken}`, ignora su resultado y borra las cookies. Las usan el login (spec 04) y el cambio de contraseña (spec 05).
- **RF-00.6** — Renovación con single-flight.
  - `refreshSession(refreshToken)` llama a `POST /auth/refresh` una sola vez por refresh token: las llamadas concurrentes con el mismo token (clave: su SHA-256) comparten la misma promesa, y el par resultante se memoriza 10 s para los requests que todavía traen la cookie vieja. La memoria es un `Map` de módulo con limpieza por vencimiento (la excepción de constitución §2).
  - `proxy.ts` renueva si `g360_at` falta o vence en menos de 60 s y existe `g360_rt`: escribe las cookies en la respuesta y reescribe la cabecera `cookie` del request que sigue, para que el render ya use el token nuevo.
  - Con `INVALID_REFRESH_TOKEN` o `REFRESH_TOKEN_REUSED`, borra las cookies; si la ruta es privada, redirige a `/login?next=<ruta>`. Con `NETWORK_ERROR` o 5xx no borra nada y deja seguir (la página mostrará su error).
  - `GET /session/refresh?next=` (route handler) hace lo mismo y redirige a `next` (validado como ruta relativa) o a `/login?next=`.
- **RF-00.7** — Sesión actual y permisos (`shared/auth`).
  - `getCurrentUser()`: `GET /users/me` (`backend/04 §4`) con `React.cache` por request; `null` sin sesión. Un 404 (usuario inexistente o no activo) se trata como fin de sesión.
  - `getGrants()`: `GET /me/grants` (`backend/03 §4`) con `React.cache`; `can(grants, perm)` y `canIn(grants, companyID, perm)` replican `Principal.Can`/`CanIn` (grant con `companyId: null` es global; `"*"` concede todo).
  - `shared/auth/permissions.ts`: constantes de los permisos que usa la interfaz, con el texto exacto del backend.
  - `requireSession()` (redirige a `/login?next=` sin sesión), `requirePermission(perm, companyID?)` (llama a `forbidden()` si no lo tiene), `requireCompanyUser()` y `requireInternalUser()` (el usuario tiene o no `companyId`; si no corresponde, `notFound()`).
- **RF-00.8** — `proxy.ts`.
  - Genera un `X-Request-ID` (UUID) si el entrante no cumple `^[A-Za-z0-9-]{8,64}$` y lo pasa al render y a la respuesta.
  - Genera el nonce y fija las cabeceras de seguridad de constitución §11; en las páginas con token, `Referrer-Policy: no-referrer`.
  - Aplica la renovación de RF-00.6 y la redirección optimista: una ruta de `(portal)` o `/backoffice` sin `g360_rt` va a `/login?next=`.
  - `matcher` excluye `_next/static`, `_next/image`, `favicon`, imágenes y `/api/health`.
- **RF-00.9** — Catálogos públicos (`features/catalog`).
  - `listCountries()`, `listCurrencies()`, `listDocumentTypes({countryId, holder})`, `listTransportTypes()` y `listServiceCategories()` sobre las rutas públicas de `backend/02 §4` y `backend/08 §4`, solo activos, con `'use cache'`, `cacheLife` = `PUBLIC_REVALIDATE` y `cacheTag('catalog:<nombre>')`.
  - `contracts.ts` con los esquemas de §6 de `backend/02` (incluido `pattern: null` y `decimals`) y de las categorías (`slug`, `sortOrder`).
  - `model.ts`: búsquedas por ID o código (`countryName(id)`, `transportTypeName(code)`…) que devuelven `—` si no existe, y el orden de las categorías por `sortOrder` y nombre.
- **RF-00.10** — Formatos (`shared/format`).
  - `formatDate`, `formatDateTime` y `formatMonthYear` con `Intl.DateTimeFormat('es-CO')` y la zona de la cookie `tz` (por defecto `America/Bogota`); `formatPlainDate('AAAA-MM-DD')` sin conversión de zona.
  - `TimezoneCookie` (Client Component del layout raíz) fija `tz` con `Intl.DateTimeFormat().resolvedOptions().timeZone` si falta o cambió.
  - `formatMoney({amount, currency}, currencies)` con `decimals` y `symbol` del catálogo, aritmética entera sobre cadenas, miles con `.` y decimales con `,` (`US$ 2.800,00`); una moneda fuera del catálogo se formatea con 2 decimales y el código ISO.
  - `parseMoneyInput(texto, decimals)` → unidades menores o error; `cubicMetersToLiters(texto)` → entero (hasta 3 decimales); `formatLiters` y `formatKg` para mostrar.
  - `formatBps(1250)` → «12,50 %».
- **RF-00.11** — Salud y logs.
  - `GET /api/health`: 200 `{"status":"ok"}` si la API responde a su `/health` en menos de 2 s; si no, 503 `{"status":"unavailable"}`. Sin caché.
  - `shared/lib/logger.ts`: JSON en una línea a stdout con `level`, `msg`, `requestId`, `route` y campos permitidos; descarta las claves `authorization`, `cookie`, `token`, `refreshToken`, `accessToken`, `password` a cualquier profundidad. `shared/api` loguea cada llamada (método, plantilla de ruta, status, duración) en `debug` y los 5xx, `NETWORK_ERROR` y `CONTRACT_MISMATCH` en `error`.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/api/health` | Pública | — | RF-00.11 |
| `/session/refresh?next=` | Con cookie de refresh | — | RF-00.6 |
| `not-found`, `forbidden`, `global-error` (raíz) | — | — | RF-00.4 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `POST /auth/refresh` `{refreshToken}` → `{accessToken, refreshToken, tokenType, expiresIn}` | `backend/05 §4` | Renovación (RF-00.6) |
| `GET /users/me` | `backend/04 §4` | Usuario actual (RF-00.7) |
| `GET /me/grants` → `{userId, grants: [{permission, companyId}]}` | `backend/03 §4` | Permisos de la UI (RF-00.7) |
| `GET /countries`, `/currencies`, `/document-types?countryId=&holder=`, `/transport-types` | `backend/02 §4` | Catálogos (RF-00.9) |
| `GET /service-categories` | `backend/08 §4` | Catálogo de categorías (RF-00.9) |
| `GET /health` (fuera de `/api/v1`) | `backend/00 §4` | Salud (RF-00.11) |

| Código | Mensaje (transversal) |
|---|---|
| `INVALID_BODY` | «Revisa los datos del formulario.» |
| `INVALID_QUERY` | «Revisa los filtros de la búsqueda.» |
| `UNAUTHENTICATED`, `TOKEN_EXPIRED` | «Tu sesión terminó. Ingresa de nuevo.» |
| `FORBIDDEN` | «No tienes permiso para hacer esto.» |
| `RATE_LIMITED` | «Demasiados intentos. Espera un minuto y vuelve a intentarlo.» |
| `NETWORK_ERROR` | «No pudimos conectar con Global 360. Revisa tu conexión e inténtalo de nuevo.» |
| `INTERNAL_ERROR`, `CONTRACT_MISMATCH`, desconocido | «Algo salió mal de nuestro lado. Si se repite, escríbenos con el código de soporte {requestID}.» |

## 6. Estados y reglas de la interfaz

- `not-found`: «No encontramos esta página» con enlace al inicio. `forbidden`: «No tienes acceso a esta sección» con enlace al inicio de su superficie.
- Ninguna pantalla muestra un token, un código interno de la API ni un stack.

## 7. Componentes, datos y caché

- Lecturas públicas (`catalog`): `'use cache'` con `PUBLIC_REVALIDATE` y etiquetas `catalog:*`; las acciones de administración (spec 08) llaman a `updateTag`.
- Lecturas privadas: `cache: 'no-store'` y `React.cache` por request.
- `TimezoneCookie` es el único Client Component de esta spec.

## 8. Accesibilidad y SEO

- Las páginas `not-found` y `forbidden` tienen `<h1>`, `lang="es"` heredado y `noindex` (Next lo añade en `forbidden()`).
- `/session/refresh` y `/api/health` no se indexan (`robots` de la spec 03).

## 9. Criterios de aceptación

- **CA-00.1** (RF-00.1) — Dado el repositorio recién preparado, cuando se ejecutan `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` y `pnpm format:check`, entonces todos terminan con código 0; y un archivo de prueba en `src/features/a/components` que importa `src/features/b/api.ts`, o un componente `'use client'` que importa `shared/api`, hace fallar `pnpm lint`. Un `import type` desde `features/b/contracts.ts` no falla.
- **CA-00.2** (RF-00.2) — Dado un entorno sin `API_BASE_URL`, o con `API_TIMEOUT=abc`, cuando se carga `env`, entonces lanza un error que nombra la variable y no imprime ningún valor; con las obligatorias presentes, aplica los valores por defecto de constitución §13 (`SESSION_COOKIE_SECURE=true`, `API_TIMEOUT=10s`…).
- **CA-00.3** (RF-00.3) — Dado un `fetch` stub, cuando `apiRequest` hace una llamada con `auth: 'user'`, entonces envía `Authorization: Bearer <cookie>`, `X-Request-ID` del request, `User-Agent` y `X-Forwarded-For` del navegador, y `cache: 'no-store'`; con `apiPublic` no envía ninguna de las cuatro primeras. Una respuesta 409 `{"error":"QUOTE_EXPIRED"}` con `X-Request-ID: abc12345` produce `ApiError{409, QUOTE_EXPIRED, abc12345}`; un 500 sin JSON, `INTERNAL_ERROR`; un timeout, `NETWORK_ERROR`; un 200 que no cumple el esquema, `CONTRACT_MISMATCH`; y un 204, `undefined`.
- **CA-00.4** (RF-00.4) — `toActionState` con `INQUIRY_LOCATION_INVALID` y un mapa que lo asocia al campo `origin.city` devuelve ese campo y su texto; con `RATE_LIMITED` y un mapa sin él, el texto transversal; con `XYZ_UNKNOWN`, el genérico con el `requestID`. `handlePageError` con 404 llama a `notFound`, con 403 a `forbidden`, con 401 `TOKEN_EXPIRED` redirige a `/session/refresh?next=` y con 500 relanza.
- **CA-00.5** (RF-00.5) — `setSession` con `SESSION_COOKIE_SECURE=true` escribe `__Host-g360_at` y `__Host-g360_rt` con `httpOnly`, `secure`, `sameSite=lax`, `path=/` y los `maxAge` de RF-00.5; con `false`, sin prefijo ni `secure`. `readAccessExpiry` devuelve el `exp` de un JWT de ejemplo y `null` para un texto que no es JWT.
- **CA-00.6** (RF-00.6) — Dadas dos llamadas simultáneas a `refreshSession` con el mismo refresh token y un `fetch` stub que tarda 50 ms, entonces el stub recibe **una sola** llamada y las dos obtienen el mismo par; una tercera llamada 5 s después con el token viejo recibe el par memorizado sin llamar a la API, y una 11 s después sí llama. Con `REFRESH_TOKEN_REUSED`, la respuesta de `proxy.ts` borra las dos cookies y, en `/inquiries`, redirige a `/login?next=%2Finquiries`; con `NETWORK_ERROR` no borra las cookies.
- **CA-00.7** (RF-00.7) — `can` con `[{permission: "*", companyId: null}]` concede `quote:respond`; `canIn(grants, "A", "user:manage")` es verdadero con `{user:manage, A}` y falso con `{user:manage, B}`; `can(grants, "user:manage")` es falso con un grant solo de empresa. `requirePermission` sin el permiso llama a `forbidden()`; `requireInternalUser` con un usuario con `companyId` llama a `notFound()`; `getCurrentUser` con un 404 de `/users/me` borra la sesión.
- **CA-00.8** (RF-00.8) — Una petición a `/portal` sin cookies recibe un 307 a `/login?next=%2Fportal`; a `/` no redirige. Toda respuesta trae `X-Request-ID` (el entrante si cumple el patrón, uno nuevo si es `abc`), `Content-Security-Policy` con un nonce distinto en cada petición, `X-Content-Type-Options: nosniff` y `frame-ancestors 'none'`; `/verify-email` trae `Referrer-Policy: no-referrer`.
- **CA-00.9** (RF-00.9) — Los esquemas de `catalog` aceptan los ejemplos de `backend/02 §4` y de las categorías de `backend/08`, y rechazan una moneda sin `decimals`. `countryName` con un ID desconocido devuelve `—`. Las categorías salen ordenadas por `sortOrder` y, a igualdad, por nombre.
- **CA-00.10** (RF-00.10) — `formatMoney({amount: 280000, currency: "USD"})` con el catálogo de la semilla da `US$ 2.800,00`; con `amount: 9007199254740993` no pierde precisión. `parseMoneyInput("2800,5", 2)` da `280050`, `"2.800,50"` es error, `"10.123"` con 2 decimales es error. `cubicMetersToLiters("1,25")` da `1250`. `formatDateTime("2026-12-05T15:00:00.123Z")` con `tz=America/Costa_Rica` muestra las 9:00 del 5 de diciembre; `formatPlainDate("2026-12-05")` muestra el 5 de diciembre en cualquier zona. `formatBps(1250)` da `12,50 %`.
- **CA-00.11** (RF-00.11) — Con la API caída, `/api/health` responde 503; con la API arriba, 200. Un log de una llamada fallida no contiene la cabecera `Authorization`, el valor de las cookies ni un `refreshToken` aunque el objeto logueado los traiga anidados.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0001 | Esqueleto Next 16 con `src/`, TypeScript strict, Tailwind 4 base, `next.config.ts` (`cacheComponents`, `authInterrupts`, `standalone`) y scripts de pnpm, avisando y explicando cada dependencia | ops | F0 | RF-00.1 | — | `package.json`, `pnpm-lock.yaml`, `next.config.ts`, `tsconfig.json`, `src/app/layout.tsx`, `src/app/globals.css` |
| G360F-0002 | ESLint con las fronteras de constitución §2, Prettier con el plugin de Tailwind y scripts `lint`, `typecheck`, `format` | ops | F0 | RF-00.1 | G360F-0001 | `eslint.config.mjs`, `.prettierrc`, `package.json` |
| G360F-0003 | Vitest (proyectos `node` y `jsdom`), Testing Library, Playwright con axe y helper de E2E que salta sin API | ops | F0 | RF-00.1 | G360F-0001 | `vitest.config.ts`, `playwright.config.ts`, `e2e/support/*.ts` |
| G360F-0004 | `.gitignore`, `.env.example` con las variables de §13 y `README.md` inicial | ops | F0 | RF-00.1, RF-00.2 | G360F-0001 | `.gitignore`, `.env.example`, `README.md` |
| G360F-0005 | Prueba del esqueleto: comandos en verde y casos de frontera que hacen fallar el lint | test | F0 | CA-00.1 | G360F-0002, G360F-0003, G360F-0004 | `src/shared/lib/boundaries.fixture.test.ts`, `eslint.config.mjs` |
| G360F-0006 | Configuración: `env.ts` y `public-env.ts` con zod, y `parseDuration` | impl | F1 | RF-00.2 | G360F-0005 | `src/shared/config/*.ts`, `src/shared/lib/duration.ts` |
| G360F-0007 | Cliente de la API: `apiRequest`, `apiPublic`, `pageSchema`, `ApiError`, `ActionState`, `toActionState` y mensajes transversales | impl | F1 | RF-00.3, RF-00.4 | G360F-0006 | `src/shared/api/*.ts` |
| G360F-0008 | `handlePageError` y páginas raíz `global-error`, `not-found` y `forbidden` | impl | F1 | RF-00.4 | G360F-0007 | `src/shared/api/page-error.ts`, `src/app/{global-error,not-found,forbidden}.tsx` |
| G360F-0009 | Cookies de sesión, `readAccessExpiry`, `refreshSession` con single-flight y route handler `/session/refresh` | impl | F1 | RF-00.5, RF-00.6 | G360F-0007 | `src/shared/auth/{session,refresh}.ts`, `src/app/session/refresh/route.ts` |
| G360F-0010 | `proxy.ts`: request-id, nonce y cabeceras de seguridad, renovación y redirección optimista | impl | F1 | RF-00.6, RF-00.8 | G360F-0009 | `proxy.ts`, `src/shared/auth/proxy-session.ts`, `src/shared/lib/csp.ts` |
| G360F-0011 | Sesión actual y permisos: `getCurrentUser`, `getGrants`, `can`/`canIn`, `require*` y constantes de permisos | impl | F1 | RF-00.7 | G360F-0009 | `src/shared/auth/{current-user,grants,guards,permissions}.ts` |
| G360F-0012 | Feature `catalog`: contratos, lecturas cacheadas y búsquedas por ID o código | impl | F1 | RF-00.9 | G360F-0007 | `src/features/catalog/{contracts,api,model}.ts` |
| G360F-0013 | Formatos: fechas con zona, dinero, entrada de montos, unidades, puntos básicos y `TimezoneCookie` | impl | F1 | RF-00.10 | G360F-0012 | `src/shared/format/*.ts`, `src/shared/format/TimezoneCookie.tsx` |
| G360F-0014 | `/api/health` y logger JSON con saneamiento | impl | F1 | RF-00.11 | G360F-0007 | `src/app/api/health/route.ts`, `src/shared/lib/logger.ts` |
| G360F-0015 | Tests de configuración, cliente de la API y traducción de errores | test | F1 | CA-00.2, CA-00.3, CA-00.4 | G360F-0008 | `src/shared/config/*.test.ts`, `src/shared/api/*.test.ts` |
| G360F-0016 | Tests de cookies, single-flight, `/session/refresh` y `proxy.ts` | test | F1 | CA-00.5, CA-00.6, CA-00.8 | G360F-0010 | `src/shared/auth/*.test.ts`, `proxy.test.ts` |
| G360F-0017 | Tests de grants, `can`/`canIn` y guardas | test | F1 | CA-00.7 | G360F-0011 | `src/shared/auth/{grants,guards}.test.ts` |
| G360F-0018 | Tests de los contratos de `catalog` y de los formatos | test | F1 | CA-00.9, CA-00.10 | G360F-0013 | `src/features/catalog/*.test.ts`, `src/shared/format/*.test.ts` |
| G360F-0019 | Tests de `/api/health` y del saneamiento del logger | test | F1 | CA-00.11 | G360F-0014 | `src/app/api/health/route.test.ts`, `src/shared/lib/logger.test.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Varias instancias del front: exigen `cacheHandler` compartido, `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` y resolver el refresh entre instancias. Fuera del MVP.
- Analítica de producto: no hay en el MVP; solo Web Vitals al log (spec 12).
- **Pregunta:** ¿qué zona horaria se usa en los correos y en las páginas públicas? Por defecto, `America/Bogota` en lo público y la del navegador en lo privado.
- **Backend/05** — La rotación del refresh no tiene ventana de gracia: dos refresh con el mismo token revocan la familia (`backend/RF-05.3`, `CA-05.7`). Por defecto: single-flight en el BFF con una sola instancia; antes de escalar el front se pide una gracia corta en la que el token recién rotado devuelva el mismo par.
- **Backend/00** — Para que el rate limit y la auditoría vean la IP real, `TRUSTED_PROXIES` del backend debe incluir el CIDR del front y el BFF reenvía `X-Forwarded-For`. Por defecto: se configura en el despliegue (spec 12); en local, el backend ve la IP del front.
