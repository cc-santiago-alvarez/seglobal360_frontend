# Tareas — SEGlobal 360 frontend

> **Archivo generado** por `docs/tools/gen_tasks.py`. La fuente de cada tarea es la tabla *Tareas* de su spec, y la de cada pendiente con el backend, las líneas `- **Backend/NN** — …` de la §11 de su spec. Las épicas post-MVP se definen en el script (`EXTRA`). Lo único que se edita a mano son las casillas `[x]`, que se conservan al regenerar (§7).

## 1. Cómo leer este documento

- **ID:** `G360F-xxxx`, con numeración propia del frontend de 4 dígitos. Es también el ticket del commit (`[G360F-xxxx] feat: …`, constitución §16). Los IDs van en orden secuencial por spec, y una tarea solo depende de tareas con número menor. Mientras ninguna tarea esté cerrada, se compactan con `--renumber` (§7); después son estables, y una tarea nueva toma el siguiente ID libre.
- **Formato:** `- [ ] ID [P] tipo título`, seguido de una línea con lo que cubre y sus dependencias, y otra con los archivos.
- **`[x]`:** la tarea está mergeada en `main`. Se marca a mano en el PR que la cierra.
- **`[P]`:** la tarea puede empezar al inicio de su fase, porque no depende de otra tarea de la misma fase. Las tareas `[P]` de una fase se pueden repartir en paralelo.
- **Cubre:** los requisitos (`RF-NN.x`) que implementa o los criterios de aceptación (`CA-NN.x`) que verifica.
- **Tipo:** `impl` (código de producción), `test`, `ops` (repositorio, infraestructura, operación) o `epic` (post-MVP: exige escribir y aprobar su spec antes del código).
- **Reglas:** las de trazabilidad de constitución §17. Este script las valida.

## 2. Resumen

| Fase | Nombre | Tareas | Hechas | impl | test | ops | epic |
|---|---|---|---|---|---|---|---|
| F0 | Preparación del repositorio (spec 00) | 5 | 0 | 0 | 1 | 4 | 0 |
| F1 | Plataforma base, sistema de diseño y landing migrada (specs 00, 01 y 03) | 32 | 0 | 22 | 10 | 0 | 0 |
| F2 | Fundación: acceso, portal y backoffice básico (specs 04, 05, 08 y 09) | 21 | 0 | 14 | 7 | 0 | 0 |
| F3 | Clientes y proveedores (specs 04, 05, 07, 08 y 09) | 27 | 0 | 18 | 9 | 0 | 0 |
| F4 | Corredor y marketplace (specs 02, 03 y 09) | 17 | 0 | 11 | 6 | 0 | 0 |
| F5 | Solicitud y cotización (specs 06 y 10) | 22 | 0 | 17 | 5 | 0 | 0 |
| F6 | Backoffice y salida a producción (specs 11 y 12) | 16 | 0 | 5 | 5 | 6 | 0 |
| | **Subtotal MVP (F0–F6)** | **140** | **0** | | | | |
| F7 | Órdenes y operación logística | 1 | 0 | 0 | 0 | 0 | 1 |
| F8 | Documentos | 1 | 0 | 0 | 0 | 0 | 1 |
| F9 | Pagos y liquidaciones | 1 | 0 | 0 | 0 | 0 | 1 |
| F10 | CRM y adquisición | 1 | 0 | 0 | 0 | 0 | 1 |
| F11 | Backoffice ampliado y seguridad | 1 | 0 | 0 | 0 | 0 | 1 |
| F12 | Escalamiento e integraciones | 1 | 0 | 0 | 0 | 0 | 1 |
| | **Total** | **146** | **0** | **87** | **43** | **10** | **6** |

```
F0 ─▶ F1 ─▶ F2 ─▶ F3 ─▶ F4 ─▶ F5 ─▶ F6 ═╪═▶ F7, F8, F9, F10, F11, F12 (cada una tras su épica del backend)
                                   corte MVP
```

| Spec | Título | Estado |
|---|---|---|
| [spec 00](specs/00-plataforma-base.spec.md) | Spec 00 — Plataforma base (`shared/*`, `catalog`) | Borrador |
| [spec 01](specs/01-sistema-diseno.spec.md) | Spec 01 — Sistema de diseño y layouts (`shared/ui`) | Borrador |
| [spec 02](specs/02-marketplace.spec.md) | Spec 02 — Marketplace público (`marketplace`) | Borrador |
| [spec 03](specs/03-sitio-publico.spec.md) | Spec 03 — Sitio público y landing (`site`) | Borrador |
| [spec 04](specs/04-registro-acceso.spec.md) | Spec 04 — Registro y acceso (`auth`, `onboarding`) | Borrador |
| [spec 05](specs/05-portal-cuenta-empresa.spec.md) | Spec 05 — Portal: inicio, cuenta, empresa y usuarios (`user`, `company`, `client`, `rbac`) | Borrador |
| [spec 06](specs/06-portal-solicitudes-cotizaciones.spec.md) | Spec 06 — Portal: solicitudes y cotizaciones (`inquiry`, `quote`) | Borrador |
| [spec 07](specs/07-portal-proveedor.spec.md) | Spec 07 — Portal del proveedor (`provider`, `service`) | Borrador |
| [spec 08](specs/08-backoffice-plataforma.spec.md) | Spec 08 — Backoffice: plataforma (`catalog`, `rbac`, `user`, `audit`) | Borrador |
| [spec 09](specs/09-backoffice-empresas-proveedores-corredores.spec.md) | Spec 09 — Backoffice: empresas, proveedores y corredores (`company`, `client`, `provider`, `service`, `corridor`) | Borrador |
| [spec 10](specs/10-backoffice-comercial.spec.md) | Spec 10 — Backoffice comercial: solicitudes y cotizador (`inquiry`, `quote`) | Borrador |
| [spec 11](specs/11-backoffice-bandeja-reportes.spec.md) | Spec 11 — Backoffice: bandeja, reportes y correcciones (`report`) | Borrador (bloqueada por `backend/13`, en Borrador) |
| [spec 12](specs/12-calidad-salida-produccion.spec.md) | Spec 12 — Calidad y salida a producción | Borrador |

## 3. Tareas por fase

### F0 — Preparación del repositorio (spec 00)

Specs: [spec 00](specs/00-plataforma-base.spec.md).

- [ ] **G360F-0001** [P] `ops` Esqueleto Next 16 con `src/`, TypeScript strict, Tailwind 4 base, `next.config.ts` (`cacheComponents`, `authInterrupts`, `standalone`) y scripts de pnpm, avisando y explicando cada dependencia
  - cubre: RF-00.1 · depende de: —
  - archivos: `package.json`, `pnpm-lock.yaml`, `next.config.ts`, `tsconfig.json`, `src/app/layout.tsx`, `src/app/globals.css`
- [ ] **G360F-0002** `ops` ESLint con las fronteras de constitución §2, Prettier con el plugin de Tailwind y scripts `lint`, `typecheck`, `format`
  - cubre: RF-00.1 · depende de: G360F-0001
  - archivos: `eslint.config.mjs`, `.prettierrc`, `package.json`
- [ ] **G360F-0003** `ops` Vitest (proyectos `node` y `jsdom`), Testing Library, Playwright con axe y helper de E2E que salta sin API
  - cubre: RF-00.1 · depende de: G360F-0001
  - archivos: `vitest.config.ts`, `playwright.config.ts`, `e2e/support/*.ts`
- [ ] **G360F-0004** `ops` `.gitignore`, `.env.example` con las variables de §13 y `README.md` inicial
  - cubre: RF-00.1, RF-00.2 · depende de: G360F-0001
  - archivos: `.gitignore`, `.env.example`, `README.md`
- [ ] **G360F-0005** `test` Prueba del esqueleto: comandos en verde y casos de frontera que hacen fallar el lint
  - cubre: CA-00.1 · depende de: G360F-0002, G360F-0003, G360F-0004
  - archivos: `src/shared/lib/boundaries.fixture.test.ts`, `eslint.config.mjs`

**Criterio de salida F0:** El esqueleto de Next compila y pasan `pnpm lint`, `pnpm typecheck`, `pnpm test` y `pnpm build`.

### F1 — Plataforma base, sistema de diseño y landing migrada (specs 00, 01 y 03)

Specs: [spec 00](specs/00-plataforma-base.spec.md), [spec 01](specs/01-sistema-diseno.spec.md), [spec 03](specs/03-sitio-publico.spec.md).

- [ ] **G360F-0006** [P] `impl` Configuración: `env.ts` y `public-env.ts` con zod, y `parseDuration`
  - cubre: RF-00.2 · depende de: G360F-0005
  - archivos: `src/shared/config/*.ts`, `src/shared/lib/duration.ts`
- [ ] **G360F-0007** `impl` Cliente de la API: `apiRequest`, `apiPublic`, `pageSchema`, `ApiError`, `ActionState`, `toActionState` y mensajes transversales
  - cubre: RF-00.3, RF-00.4 · depende de: G360F-0006
  - archivos: `src/shared/api/*.ts`
- [ ] **G360F-0008** `impl` `handlePageError` y páginas raíz `global-error`, `not-found` y `forbidden`
  - cubre: RF-00.4 · depende de: G360F-0007
  - archivos: `src/shared/api/page-error.ts`, `src/app/{global-error,not-found,forbidden}.tsx`
- [ ] **G360F-0009** `impl` Cookies de sesión, `readAccessExpiry`, `refreshSession` con single-flight y route handler `/session/refresh`
  - cubre: RF-00.5, RF-00.6 · depende de: G360F-0007
  - archivos: `src/shared/auth/{session,refresh}.ts`, `src/app/session/refresh/route.ts`
- [ ] **G360F-0010** `impl` `proxy.ts`: request-id, nonce y cabeceras de seguridad, renovación y redirección optimista
  - cubre: RF-00.6, RF-00.8 · depende de: G360F-0009
  - archivos: `proxy.ts`, `src/shared/auth/proxy-session.ts`, `src/shared/lib/csp.ts`
- [ ] **G360F-0011** `impl` Sesión actual y permisos: `getCurrentUser`, `getGrants`, `can`/`canIn`, `require*` y constantes de permisos
  - cubre: RF-00.7 · depende de: G360F-0009
  - archivos: `src/shared/auth/{current-user,grants,guards,permissions}.ts`
- [ ] **G360F-0012** `impl` Feature `catalog`: contratos, lecturas cacheadas y búsquedas por ID o código
  - cubre: RF-00.9 · depende de: G360F-0007
  - archivos: `src/features/catalog/{contracts,api,model}.ts`
- [ ] **G360F-0013** `impl` Formatos: fechas con zona, dinero, entrada de montos, unidades, puntos básicos y `TimezoneCookie`
  - cubre: RF-00.10 · depende de: G360F-0012
  - archivos: `src/shared/format/*.ts`, `src/shared/format/TimezoneCookie.tsx`
- [ ] **G360F-0014** `impl` `/api/health` y logger JSON con saneamiento
  - cubre: RF-00.11 · depende de: G360F-0007
  - archivos: `src/app/api/health/route.ts`, `src/shared/lib/logger.ts`
- [ ] **G360F-0015** `test` Tests de configuración, cliente de la API y traducción de errores
  - cubre: CA-00.2, CA-00.3, CA-00.4 · depende de: G360F-0008
  - archivos: `src/shared/config/*.test.ts`, `src/shared/api/*.test.ts`
- [ ] **G360F-0016** `test` Tests de cookies, single-flight, `/session/refresh` y `proxy.ts`
  - cubre: CA-00.5, CA-00.6, CA-00.8 · depende de: G360F-0010
  - archivos: `src/shared/auth/*.test.ts`, `proxy.test.ts`
- [ ] **G360F-0017** `test` Tests de grants, `can`/`canIn` y guardas
  - cubre: CA-00.7 · depende de: G360F-0011
  - archivos: `src/shared/auth/{grants,guards}.test.ts`
- [ ] **G360F-0018** `test` Tests de los contratos de `catalog` y de los formatos
  - cubre: CA-00.9, CA-00.10 · depende de: G360F-0013
  - archivos: `src/features/catalog/*.test.ts`, `src/shared/format/*.test.ts`
- [ ] **G360F-0019** `test` Tests de `/api/health` y del saneamiento del logger
  - cubre: CA-00.11 · depende de: G360F-0014
  - archivos: `src/app/api/health/route.test.ts`, `src/shared/lib/logger.test.ts`
- [ ] **G360F-0020** [P] `impl` Tokens de la landing y semánticos, fuentes con `next/font` y utilidades en `globals.css`
  - cubre: RF-01.1 · depende de: G360F-0005
  - archivos: `src/app/globals.css`, `src/app/layout.tsx`, `src/shared/ui/fonts.ts`
- [ ] **G360F-0021** `impl` Componentes de acción y de formulario, `FormErrorSummary` y `useFocusFirstError`
  - cubre: RF-01.2 · depende de: G360F-0020, G360F-0007
  - archivos: `src/shared/ui/{Button,SubmitButton,Field,Input,PasswordInput,Textarea,Select,Checkbox,RadioCardGroup,FieldGroup,FormErrorSummary}.tsx`
- [ ] **G360F-0022** `impl` Componentes de datos y de estado, `Dialog` y `ConfirmDialog`
  - cubre: RF-01.3 · depende de: G360F-0020
  - archivos: `src/shared/ui/{Card,DescriptionList,Table,Pagination,Tabs,Breadcrumbs,Stepper,Avatar,Timeline,StatusBadge,Alert,EmptyState,Skeleton,Dialog,ConfirmDialog}.tsx`
- [ ] **G360F-0023** `impl` Shell del sitio: `Logo`, `SiteHeader` con menú móvil, `SiteFooter`, `WhatsAppFloat` y `SkipLink`
  - cubre: RF-01.4 · depende de: G360F-0022
  - archivos: `src/shared/ui/site/*.tsx`
- [ ] **G360F-0024** `impl` Shell de acceso `AuthLayout`
  - cubre: RF-01.5 · depende de: G360F-0022
  - archivos: `src/shared/ui/auth/AuthLayout.tsx`
- [ ] **G360F-0025** `impl` Shell del portal `PortalShell` con menú lateral y versión móvil
  - cubre: RF-01.6 · depende de: G360F-0022
  - archivos: `src/shared/ui/portal/*.tsx`
- [ ] **G360F-0026** `impl` Shell del backoffice `BackofficeShell` con grupos e insignia de ambiente
  - cubre: RF-01.7 · depende de: G360F-0022
  - archivos: `src/shared/ui/backoffice/*.tsx`
- [ ] **G360F-0027** `impl` `error.tsx` y `loading.tsx` de cada segmento raíz y catálogo visual `/dev/ui`
  - cubre: RF-01.8 · depende de: G360F-0023, G360F-0024, G360F-0025, G360F-0026, G360F-0008
  - archivos: `src/app/*/error.tsx`, `src/app/*/loading.tsx`, `src/app/dev/ui/page.tsx`
- [ ] **G360F-0028** `test` Tests de componentes de formulario, datos y diálogos
  - cubre: CA-01.2, CA-01.3 · depende de: G360F-0021, G360F-0022
  - archivos: `src/shared/ui/*.test.tsx`
- [ ] **G360F-0029** `test` Tests de los cuatro shells (orden, actual, móvil, grupos, ambiente)
  - cubre: CA-01.4, CA-01.5, CA-01.6, CA-01.7 · depende de: G360F-0027
  - archivos: `src/shared/ui/{site,auth,portal,backoffice}/*.test.tsx`
- [ ] **G360F-0030** `test` E2E de `/dev/ui` con axe a 360 y 1440 px, prueba de contraste de tonos y búsqueda de hex y tamaños arbitrarios
  - cubre: CA-01.1, CA-01.8 · depende de: G360F-0027
  - archivos: `e2e/ui-kit.spec.ts`, `src/shared/ui/tokens.test.ts`
- [ ] **G360F-0041** `impl` Migración de las secciones, el contenido, las imágenes y los datos de contacto de la landing actual
  - cubre: RF-03.1 · depende de: G360F-0023
  - archivos: `src/features/site/{content,site}.ts`, `src/features/site/components/*.tsx`, `src/app/(site)/page.tsx`, `public/images/*`
- [ ] **G360F-0042** `impl` Metadatos, JSON-LD `Organization`, `robots.ts` y `sitemap.ts` con las URLs fijas
  - cubre: RF-03.2 · depende de: G360F-0041
  - archivos: `src/app/(site)/layout.tsx`, `src/app/{robots,sitemap}.ts`, `src/app/opengraph-image.jpg`, `src/app/icon.svg`
- [ ] **G360F-0043** `impl` Páginas legales con versión y fecha, y `noindex` mientras no haya texto
  - cubre: RF-03.3 · depende de: G360F-0023
  - archivos: `src/app/(site)/legal/{terms,privacy}/page.tsx`, `src/features/site/legal.ts`
- [ ] **G360F-0044** `impl` Captura de la adquisición en `proxy.ts` con la cookie `g360_acq`
  - cubre: RF-03.4 · depende de: G360F-0010
  - archivos: `src/shared/lib/acquisition.ts`, `proxy.ts`
- [ ] **G360F-0045** `impl` `/get-quote` y enlaces de WhatsApp
  - cubre: RF-03.5 · depende de: G360F-0041, G360F-0009
  - archivos: `src/app/(site)/get-quote/route.ts`, `src/features/site/whatsapp.ts`
- [ ] **G360F-0046** `test` Tests de adquisición, `/get-quote`, `robots` y `sitemap` fijos
  - cubre: CA-03.2, CA-03.4, CA-03.5 · depende de: G360F-0042, G360F-0044, G360F-0045
  - archivos: `src/shared/lib/acquisition.test.ts`, `src/app/(site)/get-quote/route.test.ts`, `src/app/{robots,sitemap}.test.ts`
- [ ] **G360F-0047** `test` E2E de la landing migrada y de las páginas legales con axe a 360 y 1440 px
  - cubre: CA-03.1, CA-03.3 · depende de: G360F-0043, G360F-0045
  - archivos: `e2e/landing.spec.ts`

**Criterio de salida F1:** El front arranca con la configuración validada, llama a la API de desarrollo con request-id y errores uniformes, el kit y los layouts existen y la landing actual está migrada.

### F2 — Fundación: acceso, portal y backoffice básico (specs 04, 05, 08 y 09)

Specs: [spec 04](specs/04-registro-acceso.spec.md), [spec 05](specs/05-portal-cuenta-empresa.spec.md), [spec 08](specs/08-backoffice-plataforma.spec.md), [spec 09](specs/09-backoffice-empresas-proveedores-corredores.spec.md).

- [ ] **G360F-0051** [P] `impl` `signIn` y `signOut` en `shared/auth`, y feature `auth` con sus contratos y mensajes
  - cubre: RF-04.1, RF-04.2 · depende de: G360F-0009, G360F-0011
  - archivos: `src/shared/auth/sign-in.ts`, `src/features/auth/{contracts,messages}.ts`
- [ ] **G360F-0052** `impl` `/login`: formulario, acción con redirección por `cid` y `next`, y redirección con sesión ya iniciada
  - cubre: RF-04.1, RF-04.9 · depende de: G360F-0051, G360F-0024
  - archivos: `src/app/(auth)/login/page.tsx`, `src/features/auth/{actions.ts,components/LoginForm.tsx}`
- [ ] **G360F-0053** `impl` `LogoutButton` y su acción, conectado en los shells del portal y del backoffice
  - cubre: RF-04.2 · depende de: G360F-0051, G360F-0025, G360F-0026
  - archivos: `src/features/auth/components/LogoutButton.tsx`, `src/features/auth/actions.ts`
- [ ] **G360F-0054** `test` Tests de las acciones de login y logout (redirecciones, `next`, errores, cookies)
  - cubre: CA-04.1, CA-04.2, CA-04.9 · depende de: G360F-0052, G360F-0053
  - archivos: `src/features/auth/actions.test.ts`
- [ ] **G360F-0055** `test` E2E de login y logout con el superadmin de la semilla y con un usuario de empresa
  - cubre: CA-04.1, CA-04.2, CA-04.9 · depende de: G360F-0054
  - archivos: `e2e/auth.spec.ts`
- [ ] **G360F-0061** [P] `impl` Features `user` (perfil propio, contraseña, listado y estados), `company` (lectura y listado) y `rbac` (permisos, roles y asignaciones): contratos, `api.ts` y mensajes; las reutiliza el backoffice (specs 08 y 09)
  - cubre: RF-05.1, RF-05.3, RF-05.6, RF-05.8 · depende de: G360F-0011
  - archivos: `src/features/user/{contracts,api,messages}.ts`, `src/features/company/{contracts,api,messages,model}.ts`, `src/features/rbac/{contracts,api,messages}.ts`
- [ ] **G360F-0062** `impl` Layout del portal, `_nav.ts` por permisos e inicio `/portal` con los avisos de estado
  - cubre: RF-05.1, RF-05.2 · depende de: G360F-0061, G360F-0025, G360F-0053
  - archivos: `src/app/(portal)/{layout.tsx,_nav.ts,portal/page.tsx}`, `src/features/company/components/CompanyStatusNotice.tsx`
- [ ] **G360F-0063** `impl` `/account`: datos personales y cambio de contraseña con nuevo inicio de sesión
  - cubre: RF-05.3 · depende de: G360F-0061, G360F-0051
  - archivos: `src/app/(portal)/account/page.tsx`, `src/features/user/{actions.ts,components/{ProfileForm,PasswordForm}.tsx}`
- [ ] **G360F-0064** `test` Tests del menú por permisos, de los avisos del inicio y de las acciones de la cuenta
  - cubre: CA-05.1, CA-05.2, CA-05.3 · depende de: G360F-0062, G360F-0063
  - archivos: `src/app/(portal)/_nav.test.ts`, `src/features/{company,user}/**/*.test.ts(x)`
- [ ] **G360F-0065** `test` E2E del portal: menú según el rol, inicio y cambio de contraseña
  - cubre: CA-05.1, CA-05.2, CA-05.3 · depende de: G360F-0064, G360F-0055
  - archivos: `e2e/portal-account.spec.ts`
- [ ] **G360F-0093** `impl` Layout del backoffice, `_nav.ts` por grants globales e inicio `/backoffice`
  - cubre: RF-08.1 · depende de: G360F-0026, G360F-0053, G360F-0061
  - archivos: `src/app/backoffice/{layout.tsx,_nav.ts,page.tsx}`
- [ ] **G360F-0094** `impl` Administración de países, monedas, tipos de documento y tipos de transporte
  - cubre: RF-08.2 · depende de: G360F-0093, G360F-0012
  - archivos: `src/app/backoffice/catalogs/page.tsx`, `src/features/catalog/{actions.ts,components/*}`
- [ ] **G360F-0095** `impl` Roles: listado, detalle con permisos agrupados, alta, edición y estado
  - cubre: RF-08.3 · depende de: G360F-0093
  - archivos: `src/app/backoffice/roles/{page.tsx,[id]/page.tsx}`, `src/features/rbac/{actions.ts,components/{RoleTable,RoleForm,PermissionPicker}.tsx}`
- [ ] **G360F-0096** `impl` `RoleAssignmentsPanel`: asignaciones de un usuario, asignar y revocar
  - cubre: RF-08.4 · depende de: G360F-0095
  - archivos: `src/features/rbac/components/RoleAssignmentsPanel.tsx`, `src/features/rbac/{actions,model}.ts`
- [ ] **G360F-0097** `impl` Usuarios: listado global con filtros y detalle con estados y asignaciones
  - cubre: RF-08.5 · depende de: G360F-0096
  - archivos: `src/app/backoffice/users/{page.tsx,[id]/page.tsx}`, `src/features/user/components/{BackofficeUserTable,UserDetail}.tsx`
- [ ] **G360F-0098** `impl` Feature `audit`: `/backoffice/audit-logs` con filtros y `AuditTrail`
  - cubre: RF-08.6 · depende de: G360F-0093
  - archivos: `src/features/audit/*`, `src/app/backoffice/audit-logs/page.tsx`
- [ ] **G360F-0099** `test` Tests de menú, catálogos, roles, asignaciones, usuarios y auditoría
  - cubre: CA-08.1, CA-08.2, CA-08.3, CA-08.4, CA-08.5, CA-08.6 · depende de: G360F-0094, G360F-0097, G360F-0098
  - archivos: `src/app/backoffice/_nav.test.ts`, `src/features/{catalog,rbac,user,audit}/**/*.test.ts(x)`
- [ ] **G360F-0100** `test` E2E del superadmin: catálogo de prueba, rol nuevo asignado y revocado, estado de un usuario y auditoría
  - cubre: CA-08.1, CA-08.2, CA-08.4, CA-08.5 · depende de: G360F-0099, G360F-0055
  - archivos: `e2e/backoffice-platform.spec.ts`
- [ ] **G360F-0104** `impl` Empresas: listado con pestañas y filtros, y detalle con usuarios e historial
  - cubre: RF-09.1, RF-09.2 · depende de: G360F-0093, G360F-0098
  - archivos: `src/app/backoffice/companies/{page.tsx,[id]/page.tsx}`, `src/features/company/components/{CompanyTable,CompanyDetail}.tsx`
- [ ] **G360F-0105** `impl` Empresas: edición, corrección de la razón social con motivo y alta
  - cubre: RF-09.2, RF-09.3 · depende de: G360F-0104
  - archivos: `src/app/backoffice/companies/new/page.tsx`, `src/features/company/{actions.ts,components/{CompanyAdminForm,LegalNameForm}.tsx}`
- [ ] **G360F-0106** `test` Tests y E2E del listado, el detalle, la edición y el alta de empresas
  - cubre: CA-09.1, CA-09.2, CA-09.3 · depende de: G360F-0105, G360F-0100
  - archivos: `src/features/company/**/*.test.ts(x)`, `e2e/backoffice-companies.spec.ts`

**Criterio de salida F2:** Login funcional con roles: un usuario entra, ve el menú según sus permisos, la sesión se renueva sin que lo note y sale; el superadmin gestiona catálogos, roles, empresas y usuarios desde el backoffice.

### F3 — Clientes y proveedores (specs 04, 05, 07, 08 y 09)

Specs: [spec 04](specs/04-registro-acceso.spec.md), [spec 05](specs/05-portal-cuenta-empresa.spec.md), [spec 07](specs/07-portal-proveedor.spec.md), [spec 08](specs/08-backoffice-plataforma.spec.md), [spec 09](specs/09-backoffice-empresas-proveedores-corredores.spec.md).

- [ ] **G360F-0056** [P] `impl` Feature `onboarding` y `/register`: formulario por bloques, tipos de documento por país, consentimiento, acción y panel «Revisa tu correo»
  - cubre: RF-04.3 · depende de: G360F-0052, G360F-0044
  - archivos: `src/features/onboarding/*`, `src/app/(auth)/register/page.tsx`
- [ ] **G360F-0057** [P] `impl` `/verify-email` con envío al montar y `ResendVerificationForm` (también en el login)
  - cubre: RF-04.4, RF-04.5 · depende de: G360F-0052
  - archivos: `src/app/(auth)/verify-email/page.tsx`, `src/features/auth/components/{VerifyEmail,ResendVerificationForm}.tsx`
- [ ] **G360F-0058** `impl` `/forgot-password`, `/reset-password` y `/accept-invitation` con `SetPasswordForm`
  - cubre: RF-04.6, RF-04.7, RF-04.8 · depende de: G360F-0057
  - archivos: `src/app/(auth)/{forgot-password,reset-password,accept-invitation}/page.tsx`, `src/features/auth/components/{ForgotPasswordForm,SetPasswordForm}.tsx`
- [ ] **G360F-0059** `test` Tests de las acciones de registro (cuerpo, adquisición, confirmación, mapeo de códigos) y de las páginas con token
  - cubre: CA-04.3, CA-04.4, CA-04.5, CA-04.6, CA-04.7, CA-04.8 · depende de: G360F-0056, G360F-0058
  - archivos: `src/features/onboarding/*.test.ts`, `src/features/auth/*.test.ts(x)`
- [ ] **G360F-0060** `test` E2E de registro → verificación → login, recuperación → restablecimiento e invitación, leyendo los `.eml` de `tmp/mail/`
  - cubre: CA-04.3, CA-04.4, CA-04.5, CA-04.6, CA-04.7, CA-04.8 · depende de: G360F-0059
  - archivos: `e2e/registration.spec.ts`, `e2e/password.spec.ts`, `e2e/support/mail.ts`
- [ ] **G360F-0066** [P] `impl` `/company`: datos y edición por permiso, perfil comercial del cliente y `TagsInput`
  - cubre: RF-05.4, RF-05.5 · depende de: G360F-0062
  - archivos: `src/app/(portal)/company/page.tsx`, `src/features/company/{actions.ts,components/*}`, `src/features/client/*`, `src/shared/ui/TagsInput.tsx`
- [ ] **G360F-0067** [P] `impl` `/company/users`: listado con roles, estados y acciones por fila; modelo de `rbac` (`assignableRoles`, `isLastManager`)
  - cubre: RF-05.6 · depende de: G360F-0062
  - archivos: `src/app/(portal)/company/users/page.tsx`, `src/features/user/{actions.ts,components/{UsersTable,UserStatusActions}.tsx}`, `src/features/rbac/model.ts`
- [ ] **G360F-0068** `impl` Invitar a un usuario con roles asignables
  - cubre: RF-05.7 · depende de: G360F-0067, G360F-0056
  - archivos: `src/features/onboarding/{api,actions}.ts`, `src/features/onboarding/components/InviteUserForm.tsx`
- [ ] **G360F-0069** `impl` Cambiar el rol en dos llamadas, con aviso de fallo parcial y protección del último administrador
  - cubre: RF-05.8 · depende de: G360F-0067
  - archivos: `src/features/rbac/{actions.ts,components/RoleSelect.tsx}`
- [ ] **G360F-0070** `test` Tests de empresa, perfil comercial, estados de usuario, invitación, roles asignables, último administrador y cambio de rol
  - cubre: CA-05.4, CA-05.5, CA-05.6, CA-05.7, CA-05.8 · depende de: G360F-0066, G360F-0068, G360F-0069
  - archivos: `src/features/{company,client,user,rbac,onboarding}/**/*.test.ts(x)`
- [ ] **G360F-0071** `test` E2E de empresa y usuarios: edición por permiso, invitación aceptada, cambio de rol y desactivación
  - cubre: CA-05.4, CA-05.6, CA-05.7, CA-05.8 · depende de: G360F-0070, G360F-0060
  - archivos: `e2e/portal-company.spec.ts`
- [ ] **G360F-0084** [P] `impl` Features `provider` y `service`: contratos, límites, `api.ts`, modelos (etiquetas, estados editables, acciones por estado, pista de obligatorios) y mensajes
  - cubre: RF-07.1 · depende de: G360F-0011, G360F-0012
  - archivos: `src/features/{provider,service}/{contracts,api,model,messages}.ts`
- [ ] **G360F-0085** `impl` Menú del grupo Proveedor y bloque del perfil en el inicio
  - cubre: RF-07.2 · depende de: G360F-0084, G360F-0062
  - archivos: `src/app/(portal)/{_nav.ts,portal/page.tsx}`, `src/features/provider/components/ProviderStatusBlock.tsx`
- [ ] **G360F-0086** `impl` `/provider`: formulario del perfil con `PATCH` parcial, solo lectura por estado o permiso, y envío a revisión
  - cubre: RF-07.3, RF-07.4 · depende de: G360F-0084, G360F-0066
  - archivos: `src/app/(portal)/provider/page.tsx`, `src/features/provider/{actions.ts,components/{ProviderForm,SubmitForReview}.tsx}`
- [ ] **G360F-0087** `impl` `/provider/services`: tabla con filtro de estado, avisos y vacío
  - cubre: RF-07.5 · depende de: G360F-0084, G360F-0062
  - archivos: `src/app/(portal)/provider/services/page.tsx`, `src/features/service/components/ServiceTable.tsx`
- [ ] **G360F-0088** `impl` Alta y edición de un servicio, con rutas habilitadas si está publicado
  - cubre: RF-07.6 · depende de: G360F-0087
  - archivos: `src/app/(portal)/provider/services/{new,[id]}/page.tsx`, `src/features/service/{actions.ts,components/{ServiceForm,EnabledRoutes}.tsx}`
- [ ] **G360F-0089** `impl` Acciones de estado del servicio con confirmaciones y `updateTag('marketplace')`
  - cubre: RF-07.7 · depende de: G360F-0088
  - archivos: `src/features/service/{actions.ts,components/ServiceStatusActions.tsx}`
- [ ] **G360F-0090** `test` Tests de contratos y modelos de proveedor y servicio
  - cubre: CA-07.1, CA-07.4, CA-07.7 · depende de: G360F-0084
  - archivos: `src/features/{provider,service}/*.test.ts`
- [ ] **G360F-0091** `test` Tests de acciones y componentes (permisos, solo lectura, `PATCH` parcial, tránsito, errores de publicación)
  - cubre: CA-07.2, CA-07.3, CA-07.5, CA-07.6, CA-07.7 · depende de: G360F-0085, G360F-0086, G360F-0089
  - archivos: `src/features/{provider,service}/**/*.test.tsx`, `src/app/(portal)/_nav.test.ts`
- [ ] **G360F-0092** `test` E2E del proveedor: perfil, revisión y publicación (backoffice por API), servicio publicado visible en el marketplace
  - cubre: CA-07.3, CA-07.4, CA-07.6, CA-07.7 · depende de: G360F-0091, G360F-0060
  - archivos: `e2e/provider-portal.spec.ts`
- [ ] **G360F-0101** `impl` Invitar personal interno con roles globales asignables
  - cubre: RF-08.7 · depende de: G360F-0097, G360F-0068
  - archivos: `src/app/backoffice/users/page.tsx`, `src/features/onboarding/{api,actions}.ts`
- [ ] **G360F-0102** [P] `impl` Pestaña de categorías de servicio
  - cubre: RF-08.8 · depende de: G360F-0094
  - archivos: `src/features/catalog/components/ServiceCategoryForm.tsx`, `src/features/catalog/actions.ts`
- [ ] **G360F-0103** `test` Tests y E2E de la invitación interna y de las categorías
  - cubre: CA-08.6, CA-08.7, CA-08.8 · depende de: G360F-0101, G360F-0102, G360F-0060
  - archivos: `src/features/{onboarding,catalog}/**/*.test.ts(x)`, `e2e/backoffice-platform-f3.spec.ts`
- [ ] **G360F-0107** [P] `impl` Validación y estados de la empresa con motivo y confirmación
  - cubre: RF-09.4 · depende de: G360F-0105
  - archivos: `src/features/company/{actions,model}.ts`, `src/features/company/components/CompanyStatusActions.tsx`
- [ ] **G360F-0108** `impl` Clientes: listado y perfil comercial en el detalle de la empresa
  - cubre: RF-09.5 · depende de: G360F-0105, G360F-0066
  - archivos: `src/app/backoffice/clients/page.tsx`, `src/features/client/{api.ts,components/ClientTable.tsx}`
- [ ] **G360F-0109** `impl` Proveedores: listado, detalle, acciones de revisión y publicación, edición y moderación de servicios
  - cubre: RF-09.6 · depende de: G360F-0104, G360F-0089
  - archivos: `src/app/backoffice/providers/{page.tsx,[id]/page.tsx}`, `src/features/provider/{actions,model}.ts`, `src/features/provider/components/{ProviderTable,ProviderReview,ProviderStatusActions}.tsx`, `src/features/service/components/ServiceModeration.tsx`
- [ ] **G360F-0110** `test` Tests y E2E de validación de empresas, clientes y revisión de proveedores
  - cubre: CA-09.2, CA-09.4, CA-09.5, CA-09.6 · depende de: G360F-0107, G360F-0108, G360F-0109, G360F-0060, G360F-0092
  - archivos: `src/features/{company,client,provider,service}/**/*.test.ts(x)`, `e2e/backoffice-validation.spec.ts`

**Criterio de salida F3:** Una empresa se registra, verifica su correo y Global 360 la valida desde el backoffice; un proveedor completa su perfil, es aprobado y publicado y publica un servicio; el administrador de la empresa gestiona sus datos y sus usuarios.

### F4 — Corredor y marketplace (specs 02, 03 y 09)

Specs: [spec 02](specs/02-marketplace.spec.md), [spec 03](specs/03-sitio-publico.spec.md), [spec 09](specs/09-backoffice-empresas-proveedores-corredores.spec.md).

- [ ] **G360F-0031** [P] `impl` Contratos y lecturas cacheadas del marketplace, con traducción de 404 y errores
  - cubre: RF-02.1, RF-02.6 · depende de: G360F-0012
  - archivos: `src/features/marketplace/{contracts,api,messages}.ts`
- [ ] **G360F-0032** `impl` Modelo: filtros desde `searchParams`, nombres de rutas, tránsito y textos de tarjetas
  - cubre: RF-02.2, RF-02.3 · depende de: G360F-0031, G360F-0013
  - archivos: `src/features/marketplace/model.ts`
- [ ] **G360F-0033** `impl` Listado `/marketplace`: pestañas, buscador y filtros, tarjetas, conteo, paginación, vacío y estado de error
  - cubre: RF-02.2, RF-02.6 · depende de: G360F-0032, G360F-0027
  - archivos: `src/app/(site)/marketplace/page.tsx`, `src/features/marketplace/components/{MarketplaceFilters,ServiceCard,ProviderCard,MarketplaceError}.tsx`
- [ ] **G360F-0034** `impl` Detalle del servicio con panel de cotización según `canRequestQuote`
  - cubre: RF-02.3 · depende de: G360F-0033
  - archivos: `src/app/(site)/marketplace/services/[id]/page.tsx`, `src/features/marketplace/components/{ServiceDetail,QuotePanel}.tsx`
- [ ] **G360F-0035** `impl` Perfil del proveedor con sus servicios paginados
  - cubre: RF-02.4 · depende de: G360F-0033
  - archivos: `src/app/(site)/marketplace/providers/[id]/page.tsx`, `src/features/marketplace/components/ProviderProfile.tsx`
- [ ] **G360F-0036** `impl` Metadatos, JSON-LD, `noindex` de listados filtrados y `listSitemapEntries`
  - cubre: RF-02.5 · depende de: G360F-0034, G360F-0035
  - archivos: `src/features/marketplace/{seo,api}.ts`, `generateMetadata` de las páginas
- [ ] **G360F-0037** `test` Tests de contratos, filtros y modelo
  - cubre: CA-02.1, CA-02.2 · depende de: G360F-0032
  - archivos: `src/features/marketplace/*.test.ts`
- [ ] **G360F-0038** `test` Tests de componentes: panel de cotización, perfil sin secciones vacías y estado de error
  - cubre: CA-02.3, CA-02.4, CA-02.6 · depende de: G360F-0035
  - archivos: `src/features/marketplace/components/*.test.tsx`
- [ ] **G360F-0039** `test` Tests de SEO y de `listSitemapEntries`
  - cubre: CA-02.5 · depende de: G360F-0036
  - archivos: `src/features/marketplace/seo.test.ts`
- [ ] **G360F-0040** `test` E2E del marketplace contra el backend de desarrollo (proveedor publicado, corredor activo) con axe y caché
  - cubre: CA-02.2, CA-02.3, CA-02.4, CA-02.6 · depende de: G360F-0036
  - archivos: `e2e/marketplace.spec.ts`, `e2e/support/seed-marketplace.ts`
- [ ] **G360F-0048** `impl` Bloques del MVP: hero con buscador, Cómo funciona, Rutas, Proveedores, ¿Eres proveedor? y Contacto, con `Suspense` y ocultación ante error o vacío
  - cubre: RF-03.6 · depende de: G360F-0031, G360F-0041
  - archivos: `src/features/site/components/{HeroSearch,HowItWorks,RoutesBlock,ProvidersBlock,ProviderCallout,QuoteContact}.tsx`, `src/app/(site)/page.tsx`
- [ ] **G360F-0049** `impl` Sitemap con las URLs del marketplace y respaldo si la API falla
  - cubre: RF-03.7 · depende de: G360F-0036, G360F-0042
  - archivos: `src/app/sitemap.ts`
- [ ] **G360F-0050** `test` Tests de los bloques (vacío, error, contenido) y E2E de la landing con datos y del sitemap
  - cubre: CA-03.6, CA-03.7 · depende de: G360F-0048, G360F-0049
  - archivos: `src/features/site/components/*.test.tsx`, `e2e/landing-mvp.spec.ts`
- [ ] **G360F-0111** [P] `impl` Feature `corridor` y corredores: listado, alta, detalle, edición y estado
  - cubre: RF-09.7 · depende de: G360F-0093, G360F-0012
  - archivos: `src/features/corridor/*`, `src/app/backoffice/corridors/{page.tsx,new/page.tsx,[id]/page.tsx}`
- [ ] **G360F-0112** `impl` Servicios habilitados del corredor: tabla con nombres, habilitar y deshabilitar
  - cubre: RF-09.8 · depende de: G360F-0111, G360F-0109
  - archivos: `src/features/corridor/components/{CorridorServices,EnableServiceForm}.tsx`, `src/features/corridor/actions.ts`
- [ ] **G360F-0113** `impl` Reglas de comisión: versiones, nueva versión porcentual o fija, simulador y `percentToBps`
  - cubre: RF-09.9 · depende de: G360F-0111, G360F-0013
  - archivos: `src/features/corridor/components/{CommissionRules,CommissionRuleForm,CommissionPreview}.tsx`, `src/features/corridor/{model,actions}.ts`
- [ ] **G360F-0114** `test` Tests y E2E de corredores, servicios habilitados y comisiones, hasta ver la ruta en la landing y el marketplace
  - cubre: CA-09.7, CA-09.8, CA-09.9 · depende de: G360F-0112, G360F-0113, G360F-0050
  - archivos: `src/features/corridor/**/*.test.ts(x)`, `e2e/backoffice-corridors.spec.ts`

**Criterio de salida F4:** La landing muestra rutas y proveedores reales, el marketplace lista y filtra servicios y proveedores, y el backoffice activa CO↔CR con su regla de comisión.

### F5 — Solicitud y cotización (specs 06 y 10)

Specs: [spec 06](specs/06-portal-solicitudes-cotizaciones.spec.md), [spec 10](specs/10-backoffice-comercial.spec.md).

- [ ] **G360F-0072** [P] `impl` Feature `inquiry`: contratos, límites, `api.ts`, modelo (etiquetas, línea de tiempo, autores, orden) y mensajes
  - cubre: RF-06.1 · depende de: G360F-0011, G360F-0013
  - archivos: `src/features/inquiry/{contracts,api,model,messages}.ts`
- [ ] **G360F-0073** [P] `impl` Feature `quote` (vista del cliente): contratos, `api.ts`, modelo del panel y mensajes
  - cubre: RF-06.1 · depende de: G360F-0011, G360F-0013
  - archivos: `src/features/quote/{contracts,api,model,messages}.ts`
- [ ] **G360F-0074** `impl` Menú Solicitudes, acción «Nueva solicitud» y bloques del inicio
  - cubre: RF-06.2 · depende de: G360F-0072, G360F-0073, G360F-0062
  - archivos: `src/app/(portal)/{_nav.ts,portal/page.tsx}`, `src/features/quote/components/PendingQuotesBlock.tsx`, `src/features/inquiry/components/RecentInquiries.tsx`
- [ ] **G360F-0075** `impl` `/inquiries`: filtros por URL, tabla y paginación
  - cubre: RF-06.3 · depende de: G360F-0072, G360F-0062
  - archivos: `src/app/(portal)/inquiries/page.tsx`, `src/features/inquiry/components/{InquiryTable,InquiryFilters}.tsx`
- [ ] **G360F-0076** `impl` `/inquiries/new`: asistente de cuatro pasos, prellenado desde el marketplace, conversiones y acción
  - cubre: RF-06.4 · depende de: G360F-0075, G360F-0031
  - archivos: `src/app/(portal)/inquiries/new/page.tsx`, `src/features/inquiry/{actions.ts,components/InquiryWizard.tsx}`
- [ ] **G360F-0077** `impl` `/inquiries/[id]`: cabecera, línea de tiempo, datos, asesor y cancelación
  - cubre: RF-06.5 · depende de: G360F-0075
  - archivos: `src/app/(portal)/inquiries/[id]/page.tsx`, `src/features/inquiry/components/{InquiryHeader,InquiryTimeline,InquiryDetails,AdvisorCard,CancelInquiryButton}.tsx`
- [ ] **G360F-0078** `impl` Conversación con el asesor y redactor
  - cubre: RF-06.6 · depende de: G360F-0077
  - archivos: `src/features/inquiry/components/{Conversation,MessageComposer}.tsx`, `src/features/inquiry/actions.ts`
- [ ] **G360F-0079** `impl` Panel de la cotización con aceptar y rechazar por versión
  - cubre: RF-06.7 · depende de: G360F-0077, G360F-0073
  - archivos: `src/features/quote/{actions.ts,components/{QuotePanel,QuoteRespondActions}.tsx}`
- [ ] **G360F-0080** `impl` `/quotes/[id]`: redirección a la solicitud, panel propio y «no disponible»
  - cubre: RF-06.8 · depende de: G360F-0079
  - archivos: `src/app/(portal)/quotes/[id]/page.tsx`
- [ ] **G360F-0081** `test` Tests de contratos y modelos (etiquetas, línea de tiempo, autores, orden, estados del panel, fechas de filtros, prellenado)
  - cubre: CA-06.1, CA-06.3, CA-06.6, CA-06.7 · depende de: G360F-0072, G360F-0073
  - archivos: `src/features/{inquiry,quote}/*.test.ts`
- [ ] **G360F-0082** `test` Tests de las acciones y componentes (crear con conversiones, mensajes, cancelar, aceptar y rechazar con sus errores, redirecciones)
  - cubre: CA-06.2, CA-06.4, CA-06.5, CA-06.6, CA-06.7, CA-06.8 · depende de: G360F-0074, G360F-0076, G360F-0078, G360F-0080
  - archivos: `src/features/{inquiry,quote}/**/*.test.ts(x)`
- [ ] **G360F-0083** `test` E2E del flujo del cliente: crear desde el marketplace, conversar y aceptar (los pasos del asesor, por API)
  - cubre: CA-06.2, CA-06.4, CA-06.5, CA-06.6, CA-06.7, CA-06.8 · depende de: G360F-0082, G360F-0040, G360F-0071
  - archivos: `e2e/inquiry-quote-client.spec.ts`, `e2e/support/advisor-api.ts`
- [ ] **G360F-0115** `impl` Vistas internas de `inquiry` y `quote` (contratos, `api.ts`, modelos, mensajes) y entradas del menú
  - cubre: RF-10.1 · depende de: G360F-0072, G360F-0073, G360F-0093
  - archivos: `src/features/{inquiry,quote}/{contracts,api,model,messages}.ts`, `src/app/backoffice/_nav.ts`
- [ ] **G360F-0116** `impl` `/backoffice/inquiries`: pestañas, filtros y tabla con nombres
  - cubre: RF-10.2 · depende de: G360F-0115
  - archivos: `src/app/backoffice/inquiries/page.tsx`, `src/features/inquiry/components/BackofficeInquiryTable.tsx`
- [ ] **G360F-0117** `impl` Detalle de la solicitud: datos, línea de tiempo, tomar, asignar, cerrar, cancelar e historial
  - cubre: RF-10.3 · depende de: G360F-0116, G360F-0098
  - archivos: `src/app/backoffice/inquiries/[id]/page.tsx`, `src/features/inquiry/{actions.ts,components/{AdvisorActions,AssignAdvisor,QuoteSummary}.tsx}`
- [ ] **G360F-0118** `impl` Conversación del asesor con canal, fecha y visibilidad
  - cubre: RF-10.4 · depende de: G360F-0117, G360F-0078
  - archivos: `src/features/inquiry/components/{AdvisorConversation,InteractionComposer}.tsx`
- [ ] **G360F-0119** `impl` Crear la cotización con la moneda de la ruta
  - cubre: RF-10.5 · depende de: G360F-0117
  - archivos: `src/features/quote/{actions.ts,components/CreateQuote.tsx}`
- [ ] **G360F-0120** `impl` Cotizador: editor de conceptos, borrador, totales de la API, envío, versión nueva, respuesta e historial
  - cubre: RF-10.6 · depende de: G360F-0119
  - archivos: `src/app/backoffice/quotes/[id]/page.tsx`, `src/features/quote/components/{QuoteEditor,ComponentRows,QuoteTotals,SendQuote,ReviseQuote,QuoteVersions}.tsx`
- [ ] **G360F-0121** `impl` `/backoffice/quotes`: pestañas, filtros y tabla
  - cubre: RF-10.7 · depende de: G360F-0115
  - archivos: `src/app/backoffice/quotes/page.tsx`, `src/features/quote/components/BackofficeQuoteTable.tsx`
- [ ] **G360F-0122** `impl` Solicitud a nombre de un cliente con el paso «Solicitante»
  - cubre: RF-10.8 · depende de: G360F-0117, G360F-0076, G360F-0105
  - archivos: `src/app/backoffice/companies/[id]/inquiries/new/page.tsx`, `src/features/inquiry/components/InquiryWizard.tsx`
- [ ] **G360F-0123** `test` Tests de menú, contratos, acciones por estado, redactor, filas de conceptos y conversión de montos
  - cubre: CA-10.1, CA-10.2, CA-10.3, CA-10.4, CA-10.5, CA-10.6, CA-10.7, CA-10.8 · depende de: G360F-0118, G360F-0120, G360F-0121, G360F-0122
  - archivos: `src/features/{inquiry,quote}/**/*.test.ts(x)`, `src/app/backoffice/_nav.test.ts`
- [ ] **G360F-0124** `test` E2E del asesor: tomar, conversar, cotizar, enviar, revisar y ver la aceptación del cliente
  - cubre: CA-10.3, CA-10.4, CA-10.5, CA-10.6, CA-10.7 · depende de: G360F-0123, G360F-0083
  - archivos: `e2e/inquiry-quote-advisor.spec.ts`

**Criterio de salida F5:** Un cliente crea una solicitud desde el marketplace, el asesor la toma y conversa con él, le envía la cotización y el cliente la acepta en línea.

### F6 — Backoffice y salida a producción (specs 11 y 12)

Specs: [spec 11](specs/11-backoffice-bandeja-reportes.spec.md), [spec 12](specs/12-calidad-salida-produccion.spec.md).

- [ ] **G360F-0125** [P] `impl` Feature `report`: contratos, `api.ts`, modelo (rango, tasas, minutos) y mensajes
  - cubre: RF-11.1, RF-11.2, RF-11.3, RF-11.4 · depende de: G360F-0093, G360F-0013
  - archivos: `src/features/report/{contracts,api,model,messages}.ts`
- [ ] **G360F-0126** `impl` Bandeja en `/backoffice` con contadores y enlaces
  - cubre: RF-11.1 · depende de: G360F-0125
  - archivos: `src/app/backoffice/page.tsx`, `src/features/report/components/InboxCounters.tsx`
- [ ] **G360F-0127** `impl` `/backoffice/reports` con las pestañas de embudo, adquisición y asesores
  - cubre: RF-11.2, RF-11.3, RF-11.4 · depende de: G360F-0125
  - archivos: `src/app/backoffice/reports/page.tsx`, `src/features/report/components/{FunnelReport,AcquisitionReport,AdvisorsReport,DateRangeFilter}.tsx`
- [ ] **G360F-0128** [P] `impl` Correcciones manuales de solicitudes y cotizaciones
  - cubre: RF-11.5, RF-11.6 · depende de: G360F-0120
  - archivos: `src/features/inquiry/components/OverrideInquiryStatus.tsx`, `src/features/quote/components/{ExtendValidity,OverrideQuoteStatus}.tsx`, `src/features/{inquiry,quote}/actions.ts`
- [ ] **G360F-0129** `test` Tests y E2E de la bandeja, los reportes y las correcciones
  - cubre: CA-11.1, CA-11.2, CA-11.3, CA-11.4, CA-11.5, CA-11.6 · depende de: G360F-0126, G360F-0127, G360F-0128
  - archivos: `src/features/report/**/*.test.ts(x)`, `e2e/backoffice-reports.spec.ts`
- [ ] **G360F-0130** [P] `ops` Ambiente de E2E en pruebas: backend con la semilla, buzón de `NOTIFIER=file` accesible, helpers de datos, de correo y de axe, y datos con sufijos únicos
  - cubre: RF-12.1, RF-12.2 · depende de: G360F-0124, G360F-0114, G360F-0110
  - archivos: `e2e/support/*.ts`, `playwright.config.ts`, infraestructura de pruebas
- [ ] **G360F-0131** `test` E2E de punta a punta del MVP por la interfaz
  - cubre: CA-12.1 · depende de: G360F-0130
  - archivos: `e2e/mvp-end-to-end.spec.ts`
- [ ] **G360F-0132** `test` Barrido de axe y recorridos solo con teclado de los flujos críticos
  - cubre: CA-12.2 · depende de: G360F-0131
  - archivos: `e2e/a11y.spec.ts`, `e2e/keyboard.spec.ts`
- [ ] **G360F-0133** [P] `impl` Web Vitals: `useReportWebVitals` y `POST /api/vitals` al log
  - cubre: RF-12.3 · depende de: G360F-0014
  - archivos: `src/shared/lib/web-vitals.ts`, `src/app/api/vitals/route.ts`
- [ ] **G360F-0134** `test` Verificación de los presupuestos de rendimiento y del límite de `/api/vitals`
  - cubre: CA-12.3 · depende de: G360F-0133, G360F-0050
  - archivos: `src/app/api/vitals/route.test.ts`, `e2e/performance.spec.ts`
- [ ] **G360F-0135** [P] `ops` `Dockerfile` standalone no root con `HEALTHCHECK` y `.dockerignore`
  - cubre: RF-12.4 · depende de: G360F-0014
  - archivos: `Dockerfile`, `.dockerignore`
- [ ] **G360F-0136** `ops` CI: lint, tipos, formato, comprobaciones de §15, tests, build, auditoría y E2E; despliegue a pruebas y promoción a producción
  - cubre: RF-12.5 · depende de: G360F-0135, G360F-0005
  - archivos: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`
- [ ] **G360F-0137** `ops` Envío de logs y alertas del front (5xx, health, `CONTRACT_MISMATCH`, `NETWORK_ERROR`)
  - cubre: RF-12.6 · depende de: G360F-0135
  - archivos: Infraestructura (fuera del repositorio), `README.md`
- [ ] **G360F-0138** `ops` Plan de migración del dominio, configuración del backend (`APP_PUBLIC_URL`, `TRUSTED_PROXIES`, `CORS_ALLOWED_ORIGINS`) y retiro de la landing anterior
  - cubre: RF-12.7 · depende de: G360F-0135, G360F-0050
  - archivos: Infraestructura, `README.md`, `../global360_frontend/README.md`
- [ ] **G360F-0139** `test` Ensayo general en pruebas: contenedor, CI, alertas, IP real y rate limit por IP, enlaces de emails, cookies y cabeceras, y checklist de go-live
  - cubre: CA-12.4, CA-12.5, CA-12.6, CA-12.7, CA-12.8 · depende de: G360F-0136, G360F-0137, G360F-0138, G360F-0132, G360F-0134, G360F-0129
  - archivos: `e2e/deployment.spec.ts`, PR de ensayo
- [ ] **G360F-0140** `ops` Salida a producción: cambio de DNS, piloto abierto y checklist de go-live firmada
  - cubre: RF-12.7, RF-12.8 · depende de: G360F-0139
  - archivos: Infraestructura, PR de salida

**Criterio de salida F6:** Bandeja y reportes del backoffice, E2E de interfaz y axe en verde, presupuestos de rendimiento cumplidos y dominio migrado: **MVP en producción**.

---

> **Corte del MVP.** Lo que sigue son épicas post-MVP. Cada una exige escribir y aprobar su spec (con RF, CA y tareas propias) antes de escribir código.

### F7 — Órdenes y operación logística

- [ ] **G360F-0141** [P] `epic` Spec y desarrollo del **seguimiento de órdenes y envíos** para el cliente (hitos e historial) y de su gestión por Operaciones en el backoffice
  - cubre: — · depende de: G360F-0140
  - archivos: spec por escribir

**Criterio de salida F7:** El cliente sigue sus órdenes y envíos con sus hitos, y Operaciones los gestiona desde el backoffice.

### F8 — Documentos

- [ ] **G360F-0142** [P] `epic` Spec y desarrollo de **documentos**: carga con progreso, versiones y descarga por orden y envío; logo y documentos del proveedor
  - cubre: — · depende de: G360F-0140
  - archivos: spec por escribir

**Criterio de salida F8:** Documentos cargados, versionados y descargables por orden y envío; logo y documentos del proveedor.

### F9 — Pagos y liquidaciones

- [ ] **G360F-0143** [P] `epic` Spec y desarrollo de **pagos**: checkout con la pasarela, estado de pagos, facturas y reembolsos para el cliente; conciliación en el backoffice
  - cubre: — · depende de: G360F-0140
  - archivos: spec por escribir

**Criterio de salida F9:** Checkout con la pasarela, estado de pagos y facturas para el cliente, y conciliación en el backoffice.

### F10 — CRM y adquisición

- [ ] **G360F-0144** [P] `epic` Spec y desarrollo del **formulario público de leads** y de la medición de campañas de punta a punta
  - cubre: — · depende de: G360F-0140
  - archivos: spec por escribir

**Criterio de salida F10:** Leads y campañas medidos de punta a punta.

### F11 — Backoffice ampliado y seguridad

- [ ] **G360F-0145** [P] `epic` MFA en el acceso de los roles administrativos y backoffice ampliado (Personal, Legal, Tecnología, reportes financieros)
  - cubre: — · depende de: G360F-0140
  - archivos: spec por escribir

**Criterio de salida F11:** MFA para los administradores y módulos internos ampliados.

### F12 — Escalamiento e integraciones

- [ ] **G360F-0146** [P] `epic` Sitio y portal en inglés (i18n), WhatsApp y mensajería en tiempo real en la conversación de la solicitud
  - cubre: — · depende de: G360F-0140
  - archivos: spec por escribir

**Criterio de salida F12:** Sitio y portal en inglés, WhatsApp y mensajería en tiempo real.

## 4. Matriz de trazabilidad: requisito → tareas

| Spec | RF | Implementan | Verifican (tests) | CA |
|---|---|---|---|---|
| 00 | RF-00.1 | G360F-0001, G360F-0002, G360F-0003, G360F-0004 | G360F-0005 | CA-00.1 |
| 00 | RF-00.2 | G360F-0004, G360F-0006 | G360F-0015 | CA-00.2 |
| 00 | RF-00.3 | G360F-0007 | G360F-0015 | CA-00.3 |
| 00 | RF-00.4 | G360F-0007, G360F-0008 | G360F-0015 | CA-00.4 |
| 00 | RF-00.5 | G360F-0009 | G360F-0016 | CA-00.5 |
| 00 | RF-00.6 | G360F-0009, G360F-0010 | G360F-0016 | CA-00.6 |
| 00 | RF-00.7 | G360F-0011 | G360F-0017 | CA-00.7 |
| 00 | RF-00.8 | G360F-0010 | G360F-0016 | CA-00.8 |
| 00 | RF-00.9 | G360F-0012 | G360F-0018 | CA-00.9 |
| 00 | RF-00.10 | G360F-0013 | G360F-0018 | CA-00.10 |
| 00 | RF-00.11 | G360F-0014 | G360F-0019 | CA-00.11 |
| 01 | RF-01.1 | G360F-0020 | G360F-0030 | CA-01.1 |
| 01 | RF-01.2 | G360F-0021 | G360F-0028 | CA-01.2 |
| 01 | RF-01.3 | G360F-0022 | G360F-0028 | CA-01.3 |
| 01 | RF-01.4 | G360F-0023 | G360F-0029 | CA-01.4 |
| 01 | RF-01.5 | G360F-0024 | G360F-0029 | CA-01.5 |
| 01 | RF-01.6 | G360F-0025 | G360F-0029 | CA-01.6 |
| 01 | RF-01.7 | G360F-0026 | G360F-0029 | CA-01.7 |
| 01 | RF-01.8 | G360F-0027 | G360F-0030 | CA-01.8 |
| 02 | RF-02.1 | G360F-0031 | G360F-0037 | CA-02.1 |
| 02 | RF-02.2 | G360F-0032, G360F-0033 | G360F-0037, G360F-0040 | CA-02.2 |
| 02 | RF-02.3 | G360F-0032, G360F-0034 | G360F-0038, G360F-0040 | CA-02.3 |
| 02 | RF-02.4 | G360F-0035 | G360F-0038, G360F-0040 | CA-02.4 |
| 02 | RF-02.5 | G360F-0036 | G360F-0039 | CA-02.5 |
| 02 | RF-02.6 | G360F-0031, G360F-0033 | G360F-0038, G360F-0040 | CA-02.6 |
| 03 | RF-03.1 | G360F-0041 | G360F-0047 | CA-03.1 |
| 03 | RF-03.2 | G360F-0042 | G360F-0046 | CA-03.2 |
| 03 | RF-03.3 | G360F-0043 | G360F-0047 | CA-03.3 |
| 03 | RF-03.4 | G360F-0044 | G360F-0046 | CA-03.4 |
| 03 | RF-03.5 | G360F-0045 | G360F-0046 | CA-03.5 |
| 03 | RF-03.6 | G360F-0048 | G360F-0050 | CA-03.6 |
| 03 | RF-03.7 | G360F-0049 | G360F-0050 | CA-03.7 |
| 04 | RF-04.1 | G360F-0051, G360F-0052 | G360F-0054, G360F-0055 | CA-04.1 |
| 04 | RF-04.2 | G360F-0051, G360F-0053 | G360F-0054, G360F-0055 | CA-04.2 |
| 04 | RF-04.3 | G360F-0056 | G360F-0059, G360F-0060 | CA-04.3 |
| 04 | RF-04.4 | G360F-0057 | G360F-0059, G360F-0060 | CA-04.4 |
| 04 | RF-04.5 | G360F-0057 | G360F-0059, G360F-0060 | CA-04.5 |
| 04 | RF-04.6 | G360F-0058 | G360F-0059, G360F-0060 | CA-04.6 |
| 04 | RF-04.7 | G360F-0058 | G360F-0059, G360F-0060 | CA-04.7 |
| 04 | RF-04.8 | G360F-0058 | G360F-0059, G360F-0060 | CA-04.8 |
| 04 | RF-04.9 | G360F-0052 | G360F-0054, G360F-0055 | CA-04.9 |
| 05 | RF-05.1 | G360F-0061, G360F-0062 | G360F-0064, G360F-0065 | CA-05.1 |
| 05 | RF-05.2 | G360F-0062 | G360F-0064, G360F-0065 | CA-05.2 |
| 05 | RF-05.3 | G360F-0061, G360F-0063 | G360F-0064, G360F-0065 | CA-05.3 |
| 05 | RF-05.4 | G360F-0066 | G360F-0070, G360F-0071 | CA-05.4 |
| 05 | RF-05.5 | G360F-0066 | G360F-0070 | CA-05.5 |
| 05 | RF-05.6 | G360F-0061, G360F-0067 | G360F-0070, G360F-0071 | CA-05.6 |
| 05 | RF-05.7 | G360F-0068 | G360F-0070, G360F-0071 | CA-05.7 |
| 05 | RF-05.8 | G360F-0061, G360F-0069 | G360F-0070, G360F-0071 | CA-05.8 |
| 06 | RF-06.1 | G360F-0072, G360F-0073 | G360F-0081 | CA-06.1 |
| 06 | RF-06.2 | G360F-0074 | G360F-0082, G360F-0083 | CA-06.2 |
| 06 | RF-06.3 | G360F-0075 | G360F-0081 | CA-06.3 |
| 06 | RF-06.4 | G360F-0076 | G360F-0082, G360F-0083 | CA-06.4 |
| 06 | RF-06.5 | G360F-0077 | G360F-0082, G360F-0083 | CA-06.5 |
| 06 | RF-06.6 | G360F-0078 | G360F-0081, G360F-0082, G360F-0083 | CA-06.6 |
| 06 | RF-06.7 | G360F-0079 | G360F-0081, G360F-0082, G360F-0083 | CA-06.7 |
| 06 | RF-06.8 | G360F-0080 | G360F-0082, G360F-0083 | CA-06.8 |
| 07 | RF-07.1 | G360F-0084 | G360F-0090 | CA-07.1 |
| 07 | RF-07.2 | G360F-0085 | G360F-0091 | CA-07.2 |
| 07 | RF-07.3 | G360F-0086 | G360F-0091, G360F-0092 | CA-07.3 |
| 07 | RF-07.4 | G360F-0086 | G360F-0090, G360F-0092 | CA-07.4 |
| 07 | RF-07.5 | G360F-0087 | G360F-0091 | CA-07.5 |
| 07 | RF-07.6 | G360F-0088 | G360F-0091, G360F-0092 | CA-07.6 |
| 07 | RF-07.7 | G360F-0089 | G360F-0090, G360F-0091, G360F-0092 | CA-07.7 |
| 08 | RF-08.1 | G360F-0093 | G360F-0099, G360F-0100 | CA-08.1 |
| 08 | RF-08.2 | G360F-0094 | G360F-0099, G360F-0100 | CA-08.2 |
| 08 | RF-08.3 | G360F-0095 | G360F-0099 | CA-08.3 |
| 08 | RF-08.4 | G360F-0096 | G360F-0099, G360F-0100 | CA-08.4 |
| 08 | RF-08.5 | G360F-0097 | G360F-0099, G360F-0100 | CA-08.5 |
| 08 | RF-08.6 | G360F-0098 | G360F-0099, G360F-0103 | CA-08.6 |
| 08 | RF-08.7 | G360F-0101 | G360F-0103 | CA-08.7 |
| 08 | RF-08.8 | G360F-0102 | G360F-0103 | CA-08.8 |
| 09 | RF-09.1 | G360F-0104 | G360F-0106 | CA-09.1 |
| 09 | RF-09.2 | G360F-0104, G360F-0105 | G360F-0106, G360F-0110 | CA-09.2 |
| 09 | RF-09.3 | G360F-0105 | G360F-0106 | CA-09.3 |
| 09 | RF-09.4 | G360F-0107 | G360F-0110 | CA-09.4 |
| 09 | RF-09.5 | G360F-0108 | G360F-0110 | CA-09.5 |
| 09 | RF-09.6 | G360F-0109 | G360F-0110 | CA-09.6 |
| 09 | RF-09.7 | G360F-0111 | G360F-0114 | CA-09.7 |
| 09 | RF-09.8 | G360F-0112 | G360F-0114 | CA-09.8 |
| 09 | RF-09.9 | G360F-0113 | G360F-0114 | CA-09.9 |
| 10 | RF-10.1 | G360F-0115 | G360F-0123 | CA-10.1 |
| 10 | RF-10.2 | G360F-0116 | G360F-0123 | CA-10.2 |
| 10 | RF-10.3 | G360F-0117 | G360F-0123, G360F-0124 | CA-10.3 |
| 10 | RF-10.4 | G360F-0118 | G360F-0123, G360F-0124 | CA-10.4 |
| 10 | RF-10.5 | G360F-0119 | G360F-0123, G360F-0124 | CA-10.5 |
| 10 | RF-10.6 | G360F-0120 | G360F-0123, G360F-0124 | CA-10.6 |
| 10 | RF-10.7 | G360F-0121 | G360F-0123, G360F-0124 | CA-10.7 |
| 10 | RF-10.8 | G360F-0122 | G360F-0123 | CA-10.8 |
| 11 | RF-11.1 | G360F-0125, G360F-0126 | G360F-0129 | CA-11.1 |
| 11 | RF-11.2 | G360F-0125, G360F-0127 | G360F-0129 | CA-11.2 |
| 11 | RF-11.3 | G360F-0125, G360F-0127 | G360F-0129 | CA-11.3 |
| 11 | RF-11.4 | G360F-0125, G360F-0127 | G360F-0129 | CA-11.4 |
| 11 | RF-11.5 | G360F-0128 | G360F-0129 | CA-11.5 |
| 11 | RF-11.6 | G360F-0128 | G360F-0129 | CA-11.6 |
| 12 | RF-12.1 | G360F-0130 | G360F-0131 | CA-12.1 |
| 12 | RF-12.2 | G360F-0130 | G360F-0132 | CA-12.2 |
| 12 | RF-12.3 | G360F-0133 | G360F-0134 | CA-12.3 |
| 12 | RF-12.4 | G360F-0135 | G360F-0139 | CA-12.4 |
| 12 | RF-12.5 | G360F-0136 | G360F-0139 | CA-12.5 |
| 12 | RF-12.6 | G360F-0137 | G360F-0139 | CA-12.6 |
| 12 | RF-12.7 | G360F-0138, G360F-0140 | G360F-0139 | CA-12.7 |
| 12 | RF-12.8 | G360F-0140 | G360F-0139 | CA-12.8 |

## 5. Épicas post-MVP

| ID | Fase | Épica | Depende de |
|---|---|---|---|
| G360F-0141 | F7 | Spec y desarrollo del **seguimiento de órdenes y envíos** para el cliente (hitos e historial) y de su gestión por Operaciones en el backoffice | G360F-0140 |
| G360F-0142 | F8 | Spec y desarrollo de **documentos**: carga con progreso, versiones y descarga por orden y envío; logo y documentos del proveedor | G360F-0140 |
| G360F-0143 | F9 | Spec y desarrollo de **pagos**: checkout con la pasarela, estado de pagos, facturas y reembolsos para el cliente; conciliación en el backoffice | G360F-0140 |
| G360F-0144 | F10 | Spec y desarrollo del **formulario público de leads** y de la medición de campañas de punta a punta | G360F-0140 |
| G360F-0145 | F11 | MFA en el acceso de los roles administrativos y backoffice ampliado (Personal, Legal, Tecnología, reportes financieros) | G360F-0140 |
| G360F-0146 | F12 | Sitio y portal en inglés (i18n), WhatsApp y mensajería en tiempo real en la conversación de la solicitud | G360F-0140 |

## 6. Pendientes con el backend

Huecos del contrato de la API que encontraron las specs del frontend. Cada uno se resuelve enmendando la spec del backend indicada; mientras tanto, el front aplica el valor por defecto que dice su spec.

| Spec del front | Spec del backend | Pendiente |
|---|---|---|
| [spec 00](specs/00-plataforma-base.spec.md) | `backend/00` | Para que el rate limit y la auditoría vean la IP real, `TRUSTED_PROXIES` del backend debe incluir el CIDR del front y el BFF reenvía `X-Forwarded-For`. Por defecto: se configura en el despliegue (spec 12); en local, el backend ve la IP del front. |
| [spec 00](specs/00-plataforma-base.spec.md) | `backend/05` | La rotación del refresh no tiene ventana de gracia: dos refresh con el mismo token revocan la familia (`backend/RF-05.3`, `CA-05.7`). Por defecto: single-flight en el BFF con una sola instancia; antes de escalar el front se pide una gracia corta en la que el token recién rotado devuelva el mismo par. |
| [spec 01](specs/01-sistema-diseno.spec.md) | `backend/03` | `GET /me/grants` no trae los nombres de los roles del usuario, y la maqueta muestra «Administrador» u «Operativo» en el menú; `client_operator` no tiene `role:read` para pedirlos. Por defecto: el menú muestra el nombre del usuario y su email, sin el rol. |
| [spec 02](specs/02-marketplace.spec.md) | `backend/10` | La búsqueda distingue tildes y los visitantes suelen escribir sin ellas. Por defecto: se envía el texto tal cual; se propone a la API una comparación insensible a tildes (collation `es` con fuerza 1). |
| [spec 02](specs/02-marketplace.spec.md) | `backend/10` | `GET /marketplace/corridors` no informa cuántos servicios tiene cada ruta, y el bloque de rutas de la landing no puede decir «[n] servicios». Por defecto: no se muestra el conteo por ruta. |
| [spec 03](specs/03-sitio-publico.spec.md) | `backend/07` | `acquisition` acepta texto libre de hasta 100 caracteres y marketing no ha fijado la lista de `source`. Por defecto: se envía `utm_source` tal cual llega. |
| [spec 03](specs/03-sitio-publico.spec.md) | `backend/10` | La proyección pública del corredor no trae `quoteValidityDays`, y la maqueta muestra «Vigencia de la cotización: 15 días» en el bloque de rutas. Por defecto: la tarjeta no muestra la vigencia. |
| [spec 04](specs/04-registro-acceso.spec.md) | `backend/07` | Un email perdido no se puede reenviar en el caso de una invitación: reinvitar responde `PERSON_ALREADY_EXISTS`. Por defecto: `/accept-invitation` con enlace vencido remite a «Recuperar contraseña», que funciona después de verificar el correo con el reenvío. |
| [spec 04](specs/04-registro-acceso.spec.md) | `backend/07` | `POST /registrations` no recibe la aceptación de los términos ni de la política de datos (un campo extra responde `INVALID_BODY`), y la ley de protección de datos exige poder probar la autorización (fecha y versión del texto aceptado). **Bloquea el go-live (F6).** Por defecto: la casilla es obligatoria en el formulario y no se envía; se pide añadir `consents: [{document, version}]` al registro y a la aceptación de invitaciones. |
| [spec 05](specs/05-portal-cuenta-empresa.spec.md) | `backend/03` | Cambiar un rol son dos llamadas no atómicas, y nada impide dejar a una empresa sin administrador ni que uno se quite a sí mismo su rol. Por defecto: RF-05.8 (aviso de fallo parcial y `isLastManager` en la UI); se pide un endpoint de cambio de rol atómico y la protección del último administrador de empresa. |
| [spec 05](specs/05-portal-cuenta-empresa.spec.md) | `backend/03` | Los roles no tienen un nombre visible distinto de su código (`client_admin`). Por defecto: se muestra su `description`; se pide un `displayName` en el rol o una descripción en español en la semilla. |
| [spec 05](specs/05-portal-cuenta-empresa.spec.md) | `backend/04` | Un `client_admin` no puede ver los nombres de los usuarios de su empresa: `GET /users` solo trae `personId` y `GET /persons/:id` exige `person:read` global. Por defecto: la tabla muestra el correo y las iniciales sacadas del correo; se pide incluir `person{firstName, lastName}` en la respuesta de usuario o un permiso de lectura de personas por empresa. |
| [spec 05](specs/05-portal-cuenta-empresa.spec.md) | `backend/04` | `GET /users/me` no trae el documento de la persona, y la maqueta de «Mi cuenta» lo muestra. Por defecto: «Mi cuenta» no muestra el documento. |
| [spec 05](specs/05-portal-cuenta-empresa.spec.md) | `backend/07` | `estimatedMonthlyShipments` no se puede vaciar una vez informado (`null` significa «no cambiar»). Por defecto: el campo lo indica y no admite vaciarse. |
| [spec 06](specs/06-portal-solicitudes-cotizaciones.spec.md) | `backend/11` | La solicitud solo trae `advisorId` y el cliente no puede consultar usuarios internos: no hay forma de mostrar el nombre del asesor. Por defecto: «Tu asesor de Global 360»; se pide un `advisor{firstName}` en la vista del cliente. |
| [spec 06](specs/06-portal-solicitudes-cotizaciones.spec.md) | `backend/11` | Las interacciones no traen el nombre del autor, y `client_operator` no tiene `user:read` para resolverlo. Por defecto: «Tú», «Tu empresa» y «Tu asesor»; se pide `author{firstName}` en la respuesta. |
| [spec 06](specs/06-portal-solicitudes-cotizaciones.spec.md) | `backend/12` | La vista del cliente de la cotización está pendiente de G360-0149 y la maqueta necesita `inquiryId` (para que `/quotes/[id]` lleve a la solicitud), `respondedAt` y `acceptedVersion` (para «Aceptaste la versión [n] el [fecha]») y el código de la solicitud con su ruta (bloque del inicio). Por defecto: página propia de la cotización, textos sin fecha y bloque sin datos de la solicitud. |
| [spec 06](specs/06-portal-solicitudes-cotizaciones.spec.md) | `backend/12` | Tras `revise`, la cotización vuelve a `draft` y desaparece para el cliente, así que el enlace del email anterior responde 404. Por defecto: «Tu asesor está actualizando la cotización» en el detalle y la página «no está disponible ahora» en `/quotes/[id]`. |
| [spec 07](specs/07-portal-proveedor.spec.md) | `backend/08` | El logo es una URL `https` externa (la carga de archivos llega en F8). Por defecto: el formulario pide la URL y muestra una vista previa. |
| [spec 07](specs/07-portal-proveedor.spec.md) | `backend/08` | No hay lectura de las rutas en que está habilitado un servicio para su propio proveedor (la fila de `corridor_services` es interna). Por defecto: se usa `inquiryPrefill.corridorIds` del marketplace, solo para servicios publicados. |
| [spec 08](specs/08-backoffice-plataforma.spec.md) | `backend/01` | La auditoría solo trae `actorId`. Por defecto: el correo del actor se resuelve con `GET /users/:id` por fila; se pide incluir el correo del actor en la entrada. |
| [spec 08](specs/08-backoffice-plataforma.spec.md) | `backend/04` | `GET /users` no filtra a los usuarios internos (`companyId` nulo) y no trae los nombres de las personas. Por defecto: un solo listado con la columna Empresa («Global 360» para los internos) y los nombres resueltos con `GET /persons/:id` por fila (20 llamadas en paralelo como mucho); se pide el filtro `internal=true` y `person{firstName, lastName}` en la respuesta. |
| [spec 09](specs/09-backoffice-empresas-proveedores-corredores.spec.md) | `backend/07` | `GET /clients` no trae el nombre de la empresa. Por defecto: se resuelve con `GET /companies/:id` por fila; se pide incluir `companyName` en la fila del cliente. |
| [spec 09](specs/09-backoffice-empresas-proveedores-corredores.spec.md) | `backend/09` | Las filas de `GET /corridors/:id/services` no traen el nombre del servicio ni el del proveedor, y no hay una lectura de servicios elegibles para un corredor. Por defecto: los nombres se resuelven con `GET /services/:id` por fila y el alta se hace eligiendo proveedor y servicio; se piden los nombres en la fila y un filtro `eligibleForCorridorId` en `GET /services`. |
| [spec 10](specs/10-backoffice-comercial.spec.md) | `backend/04` | No hay forma de listar a los asesores (usuarios internos con `inquiry:advise`). Por defecto: asignar busca usuarios por correo y la API valida que sea asesor; se pide un filtro `permission=inquiry:advise` en `GET /users`. |
| [spec 10](specs/10-backoffice-comercial.spec.md) | `backend/11` | La solicitud y sus interacciones no traen el nombre de la empresa, del asesor ni del autor. Por defecto: se resuelven por fila (`GET /companies/:id`, `GET /users/:id`); se pide incluirlos en la respuesta. |
| [spec 10](specs/10-backoffice-comercial.spec.md) | `backend/12` | La vista interna de la cotización está pendiente de G360-0149: falta confirmar cómo se exponen las versiones anteriores, si incluye `inquiryId`, `advisorId`, `acceptedVersion`, `rejectionReason` y las fechas, y si `PUT /quotes/:id/draft` devuelve el subtotal, la comisión y el total calculados. Esta spec no pasa a *Aprobada* hasta confirmarlo. Por defecto: si el borrador no trae los totales, se muestra «Se calcula al enviar». |
| [spec 11](specs/11-backoffice-bandeja-reportes.spec.md) | `backend/13` | La spec está en *Borrador*: no define el JSON de `GET /backoffice/inbox` ni el de `GET /reports/advisors`, y el de `GET /reports/acquisition` es parcial. **Bloquea esta spec.** Por defecto: los contratos de §5 se escriben cuando `backend/13` se apruebe. |
| [spec 11](specs/11-backoffice-bandeja-reportes.spec.md) | `backend/13` | No define el formato de `validUntil` en `extend-validity`. Por defecto: RFC 3339 en UTC, como el resto de la API. |
| [spec 12](specs/12-calidad-salida-produccion.spec.md) | `backend/14` | No dice nada del frontend ni de dónde se despliega. Por defecto: el front va en un contenedor en la misma red que el backend, detrás del mismo proxy TLS, y la API no se expone a internet; se pide reflejarlo en `backend/14` junto con `TRUSTED_PROXIES` y `CORS_ALLOWED_ORIGINS` del front. |

## 7. Regenerar y validar

El script lee los `RF`, los `CA` y las tablas *Tareas* de cada spec, junto con las épicas de `EXTRA`. Conserva las casillas `[x]` de este archivo, lo reescribe, y falla (código 1, con la lista de problemas) si encuentra:
- un ID, RF o CA duplicado, un RF o CA definido fuera de su spec, o un CA que cita un RF de otra spec;
- una fila de la tabla *Tareas* que no tiene 7 columnas, un tipo o una fase inválidos, o una épica en una fase del MVP;
- una tarea `impl` u `ops` sin RF, o una tarea `test` sin CA;
- un RF sin tarea `impl` u `ops`, sin tarea `test` o sin CA, o un CA que ninguna tarea `test` verifica;
- una dependencia inexistente, hacia una fase posterior, hacia una tarea con número mayor, o un ciclo;
- mientras ninguna tarea esté cerrada, una numeración que no sea secuencial por spec (G360F-0001…N sin saltos).

```bash
python3 docs/tools/gen_tasks.py docs              # valida y regenera
python3 docs/tools/gen_tasks.py docs --renumber   # compacta los IDs; solo antes de cerrar la primera tarea
```

Última generación: 13 specs, 103 RF, 103 CA, 146 tareas (0 hechas), 30 pendientes con el backend. Validación sin errores. Siguiente ID libre: `G360F-0147`.
