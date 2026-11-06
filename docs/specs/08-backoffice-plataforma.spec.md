# Spec 08 — Backoffice: plataforma (`catalog`, `rbac`, `user`, `audit`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/{catalog,rbac,user,onboarding,audit}`, `src/app/backoffice` |
| Rutas | `/backoffice`, `/backoffice/catalogs`, `/backoffice/roles`, `/backoffice/roles/[id]`, `/backoffice/users`, `/backoffice/users/[id]`, `/backoffice/audit-logs` |
| Backend | `backend/01`, `backend/02`, `backend/03`, `backend/04`, `backend/07`, `backend/08` (todas Implementadas) |
| Depende de | Specs 00, 01, 04 y 05 |

## 1. Resumen y alcance

Es la parte del backoffice con la que el superadmin y `global360_admin` administran la plataforma: el layout y el menú del backoffice, los catálogos (países, monedas, tipos de documento, tipos de transporte y categorías de servicio), los roles y sus permisos, las asignaciones de roles, los usuarios (internos y de empresas) y la auditoría (F2), más la invitación de personal interno y las categorías de servicio (F3). Es el criterio de salida de F2: «el superadmin gestiona roles, empresas y usuarios, y todo queda auditado».

Las empresas, los proveedores y los corredores son de la spec 09; la operación comercial, de la spec 10.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Criterio de F2 (superadmin gestiona roles, empresas y usuarios; todo auditado) | `backend/CLAUDE.md`, *Alcance y fases* |
| Catálogos: rutas, campos editables e inmutables, activar y desactivar, semilla | `backend/02 §4` y §5 (RF-02.1 a RF-02.6) |
| Categorías de servicio | `backend/08 §4` (RF-08.5) |
| Permisos, roles, asignaciones, antiescalada, último superadmin | `backend/03 §4` y §5 (RF-03.1 a RF-03.6) |
| Usuarios: listado global, estados, bloqueo con motivo | `backend/04 §4` (RF-04.6, RF-04.8) |
| Invitación de personal interno | `backend/07 §4` (RF-07.6) |
| Auditoría: filtros, paginación, snapshots | `backend/01 §4` (RF-01.2, RF-01.3) |

## 3. Requisitos funcionales

- **RF-08.1** — Layout, menú e inicio del backoffice.
  - `backoffice/layout.tsx` exige un usuario interno (`requireInternalUser`) y renderiza `BackofficeShell` con `LogoutButton`. Cada página exige además su permiso **global** (`requirePermission(perm)` sin empresa).
  - `src/app/backoffice/_nav.ts` arma los grupos con `can` (solo grants globales): **Operación** — Inicio (`/backoffice`), Solicitudes (`inquiry:read`, spec 10); **Empresas** — Empresas (`company:read`), Clientes (`client:read`), Proveedores (`provider:read`), Corredores (`corridor:read`) (spec 09); **Administración** — Catálogos (alguno de `country:manage`, `currency:manage`, `document_type:manage`, `transport_type:manage`, `service_category:manage`), Roles (`role:read`), Usuarios (`user:read`), Auditoría (`audit:read`); Reportes (`report:read`, spec 11). Cada spec añade sus entradas en este archivo.
  - `/backoffice` (hasta la bandeja de la spec 11): «Hola, [nombres]» y accesos a las secciones permitidas.
- **RF-08.2** — Catálogos `/backoffice/catalogs?tab=` (países, monedas, tipos de documento y tipos de transporte).
  - Pestañas por URL, cada una visible con su `<catálogo>:manage`. Tabla con activos e inactivos (`includeInactive=true`): países (código ISO, nombre), monedas (código, nombre, símbolo, decimales), tipos de documento (país, código, nombre, titulares, patrón) y tipos de transporte (código, nombre), con su estado.
  - Alta en un `Dialog` con los campos de `backend/02 §4`; edición solo de los editables (nombre; en monedas, también el símbolo; en tipos de documento, titulares y patrón); los inmutables (`isoCode`, `decimals`, `countryId`, `code`) se muestran en solo lectura.
  - Activar y desactivar con `ConfirmDialog` («Desactivar un país lo quita de los formularios; lo que ya lo usa no cambia.»).
  - Tras cada cambio, `updateTag('catalog:<nombre>')` para que los formularios y el marketplace lo vean.
- **RF-08.3** — Roles `/backoffice/roles` y `/backoffice/roles/[id]` (`role:read`).
  - Listado con filtros de alcance (`global`, `company`) y estado: nombre, descripción, alcance, «Sistema» si `isSystem`, número de permisos y estado.
  - Detalle con sus permisos agrupados por módulo (el prefijo antes de `:`), con el texto de `GET /permissions`.
  - Con `role:manage`: alta (nombre, descripción, alcance, permisos con casillas agrupadas), edición (nombre, descripción y permisos; el alcance no cambia) y activar o desactivar. Al editar un rol de sistema se avisa: «Es un rol de sistema: el cambio afecta a todas las empresas que lo usan.».
- **RF-08.4** — Asignaciones de roles (componente `RoleAssignmentsPanel`, en el detalle de un usuario).
  - Lista de `GET /role-assignments?userId=` (activas y revocadas, con quién y cuándo), «Asignar rol» (rol activo y, si es de alcance `company`, la empresa del usuario) con `POST /role-assignments`, y «Revocar» con motivo opcional (hasta 500) con `POST /role-assignments/:id/revoke`.
  - Los roles que se ofrecen son los asignables por el usuario actual (`assignableRoles`, spec 05) del alcance que corresponde.
- **RF-08.5** — Usuarios `/backoffice/users` y `/backoffice/users/[id]` (`user:read`).
  - Listado de `GET /users` con filtros de estado, empresa (`companyId`) y búsqueda por prefijo del correo (`q`), y columnas correo, nombre (§11), empresa (o «Global 360» si no tiene), estado y último ingreso.
  - Detalle: correo, persona, empresa, estado con su motivo, fechas (verificación, último ingreso, cambio de contraseña), acciones de estado con `user:manage` (las de la spec 05, con «Eres tú» en el propio) y `RoleAssignmentsPanel`.
- **RF-08.6** — Auditoría `/backoffice/audit-logs` (`audit:read`).
  - Filtros por URL: entidad, ID de la entidad, actor, empresa, acción y rango de fechas (convertido a RFC 3339).
  - Tabla de la más reciente a la más antigua: fecha, actor (correo, o «Sistema» si `actorId` es `null`), entidad e ID, acción, motivo e IP. Cada fila se expande y muestra `before` y `after` como texto JSON con formato (sin interpretar HTML), y el `requestId`.
  - `AuditTrail` (componente de `features/audit`) muestra el historial de una entidad (`?entity=&entityId=`) y lo usan los detalles de las specs 08, 09 y 10.
- **RF-08.7** — Invitar personal interno. En `/backoffice/users`, con `user:manage` global, «Invitar a Global 360» con el formulario de la spec 05 y los roles asignables de alcance `global`; llama a `POST /users/internal`. Con 201: «Invitación enviada. La persona recibirá un correo para crear su contraseña.».
- **RF-08.8** — Categorías de servicio. La pestaña «Categorías» de `/backoffice/catalogs` (`service_category:manage`) lista activas e inactivas por `sortOrder`, crea (`slug`, nombre, descripción, orden), edita (nombre, descripción, orden; el `slug` es inmutable) y activa o desactiva; tras cada cambio, `updateTag('catalog:service-categories')` y `updateTag('marketplace')`.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| Layout de `backoffice` y `/backoffice` | Usuario interno | — (sin maqueta) | RF-08.1 |
| `/backoffice/catalogs?tab=countries\|currencies\|document-types\|transport-types\|service-categories` | `<catálogo>:manage` global | — | RF-08.2, RF-08.8 |
| `/backoffice/roles`, `/backoffice/roles/[id]` | `role:read` global | — | RF-08.3 |
| `/backoffice/users`, `/backoffice/users/[id]` | `user:read` global | — | RF-08.4, RF-08.5, RF-08.7 |
| `/backoffice/audit-logs` | `audit:read` global | — | RF-08.6 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET/POST/PATCH /countries`, `/currencies`, `/document-types`, `/transport-types` y `POST …/:id/activate`, `/deactivate` | `backend/02 §4` | RF-08.2 |
| `GET/POST/PATCH /service-categories` y `POST …/:id/activate`, `/deactivate` | `backend/08 §4` | RF-08.8 |
| `GET /permissions`, `GET/POST/PATCH /roles`, `POST /roles/:id/activate`, `/deactivate` | `backend/03 §4` | RF-08.3 |
| `GET /role-assignments?userId=`, `POST /role-assignments`, `POST /role-assignments/:id/revoke` | `backend/03 §4` | RF-08.4 |
| `GET /users`, `GET /users/:id`, `POST /users/:id/activate`, `/deactivate`, `/block`, `/unblock` | `backend/04 §4` | RF-08.5 |
| `GET /persons/:id` | `backend/04 §4` | Nombres de las personas (`person:read` global) |
| `GET /companies/:id` | `backend/04 §4` | Nombre de la empresa de un usuario |
| `POST /users/internal {person, email, roleId}` | `backend/07 §4` | RF-08.7 |
| `GET /audit-logs?entity=&entityId=&actorId=&companyId=&action=&from=&to=&page=&pageSize=` | `backend/01 §4` | RF-08.6 |

| Código | Mensaje |
|---|---|
| `COUNTRY_ISO_CODE_INVALID`, `CURRENCY_ISO_CODE_INVALID` | El código debe tener 2 letras (país) o 3 letras (moneda). |
| `CURRENCY_DECIMALS_INVALID` | Los decimales van de 0 a 4. |
| `DOCUMENT_TYPE_PATTERN_INVALID` | La expresión regular no es válida. |
| `DOCUMENT_TYPE_HOLDER_INVALID` | Elige al menos un titular: persona o empresa. |
| `*_NAME_REQUIRED`, `*_CODE_INVALID`, `CURRENCY_SYMBOL_REQUIRED`, `DOCUMENT_TYPE_COUNTRY_INVALID` | Revisa el campo (texto por código en `catalog/messages.ts`). |
| `*_ALREADY_EXISTS` (catálogos, roles, categorías) | Ya existe un registro con ese código. |
| `SERVICE_CATEGORY_SLUG_INVALID` | El identificador usa solo minúsculas, números y guiones (2 a 60). |
| `ROLE_ASSIGNMENT_ESCALATION` | No puedes asignar un rol con permisos que tú no tienes. |
| `ROLE_ASSIGNMENT_SCOPE_MISMATCH` | Un rol de empresa necesita una empresa, y uno global no la lleva. |
| `ROLE_ASSIGNMENT_LAST_SUPERADMIN` | No se puede revocar el último superadmin. |
| `ROLE_ASSIGNMENT_ALREADY_EXISTS`, `ROLE_ASSIGNMENT_ALREADY_REVOKED` | Esa asignación ya existe / ya estaba revocada. |
| `ROLE_ASSIGNMENT_USER_INVALID`, `ROLE_ASSIGNMENT_COMPANY_INVALID` | El usuario debe estar activo / la empresa no existe. |
| `ROLE_INACTIVE`, `ROLE_NOT_FOUND` | Ese rol no está disponible. |
| Códigos de usuario e invitación | Los de la spec 05 |

## 6. Estados y reglas de la interfaz

- Catálogos, roles y categorías: `isActive`/`status` activo «Activo» (`success`), inactivo «Inactivo» (`neutral`). Asignaciones: `active` «Vigente» (`success`), `revoked` «Revocada» (`neutral`).
- Estados de usuario: los de la spec 05.
- El backoffice solo usa grants **globales**: un usuario interno sin un permiso no ve su sección y, si entra por URL, recibe la página 403.
- Las acciones destructivas (desactivar, revocar, bloquear) piden confirmación.

## 7. Componentes, datos y caché

- `features/catalog/{actions.ts,components/CatalogTable,CatalogForm}`, `features/rbac/components/{RoleTable,RoleForm,PermissionPicker,RoleAssignmentsPanel}.tsx`, `features/user/components/{BackofficeUserTable,UserDetail}.tsx`, `features/audit/{contracts,api,model,messages}.ts` y `features/audit/components/{AuditLogTable,AuditTrail}.tsx`.
- Los nombres de personas y empresas de una página (como mucho 20) se resuelven en paralelo con `React.cache` por request.
- Lecturas sin caché del servidor salvo los catálogos públicos, que se invalidan con `updateTag`.

## 8. Accesibilidad y SEO

- Las tablas densas mantienen objetivos de 44 px en sus acciones y un `<caption>` oculto que describe la tabla.
- El JSON de la auditoría va en `<pre>` con `tabindex="0"` para poder desplazarlo con el teclado.
- Todo el backoffice lleva `noindex` y está fuera del sitemap.

## 9. Criterios de aceptación

- **CA-08.1** (RF-08.1) — Un usuario de empresa que abre `/backoffice` recibe la página 404 (`requireInternalUser`). `_nav` con los grants de `operations` incluye Empresas, Clientes y Proveedores y no Catálogos, Roles ni Auditoría; con `*` incluye todo. Un usuario interno sin `audit:read` que abre `/backoffice/audit-logs` recibe la página 403.
- **CA-08.2** (RF-08.2) — La edición de una moneda envía solo `name` y `symbol`, nunca `decimals` ni `isoCode`; desactivar un país pide confirmación y llama a `updateTag('catalog:countries')`. En la E2E, el superadmin crea un tipo de transporte de prueba, lo edita, lo desactiva y deja de verlo en el asistente de solicitud.
- **CA-08.3** (RF-08.3) — El detalle de un rol agrupa sus permisos por módulo con su descripción. El alta de un rol con alcance `company` y dos permisos envía ese cuerpo; la edición no envía el alcance. Al editar un rol de sistema se ve el aviso.
- **CA-08.4** (RF-08.4) — Asignar a un usuario de empresa un rol de alcance `company` envía su `companyId`; uno de alcance `global` no lo envía. Con `ROLE_ASSIGNMENT_ESCALATION` y `ROLE_ASSIGNMENT_LAST_SUPERADMIN` se muestran sus mensajes. Revocar con motivo lo envía recortado.
- **CA-08.5** (RF-08.5) — El listado con `q=ana` llama a `GET /users?q=ana`; un usuario sin empresa muestra «Global 360» en la columna Empresa. El detalle del propio usuario muestra «Eres tú» sin Desactivar ni Bloquear.
- **CA-08.6** (RF-08.6) — `/backoffice/audit-logs?entity=company&entityId=<id>` lista las entradas de esa empresa; una entrada con `actorId: null` muestra «Sistema»; el `after` que contiene `<script>` se muestra como texto. En la E2E, después de validar una empresa por API, su historial muestra la acción `approve`.
- **CA-08.7** (RF-08.7) — El formulario de invitación interna ofrece solo roles de alcance `global` asignables y llama a `POST /users/internal`; en la E2E, el invitado acepta la invitación (spec 04) y llega a `/backoffice` al ingresar.
- **CA-08.8** (RF-08.8) — Crear una categoría con `slug` `Carga Aérea` muestra el mensaje de `SERVICE_CATEGORY_SLUG_INVALID`; con `carga-aerea`, se crea y aparece en el filtro del marketplace tras `updateTag`. El `slug` no se puede editar.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0093 | Layout del backoffice, `_nav.ts` por grants globales e inicio `/backoffice` | impl | F2 | RF-08.1 | G360F-0026, G360F-0053, G360F-0061 | `src/app/backoffice/{layout.tsx,_nav.ts,page.tsx}` |
| G360F-0094 | Administración de países, monedas, tipos de documento y tipos de transporte | impl | F2 | RF-08.2 | G360F-0093, G360F-0012 | `src/app/backoffice/catalogs/page.tsx`, `src/features/catalog/{actions.ts,components/*}` |
| G360F-0095 | Roles: listado, detalle con permisos agrupados, alta, edición y estado | impl | F2 | RF-08.3 | G360F-0093 | `src/app/backoffice/roles/{page.tsx,[id]/page.tsx}`, `src/features/rbac/{actions.ts,components/{RoleTable,RoleForm,PermissionPicker}.tsx}` |
| G360F-0096 | `RoleAssignmentsPanel`: asignaciones de un usuario, asignar y revocar | impl | F2 | RF-08.4 | G360F-0095 | `src/features/rbac/components/RoleAssignmentsPanel.tsx`, `src/features/rbac/{actions,model}.ts` |
| G360F-0097 | Usuarios: listado global con filtros y detalle con estados y asignaciones | impl | F2 | RF-08.5 | G360F-0096 | `src/app/backoffice/users/{page.tsx,[id]/page.tsx}`, `src/features/user/components/{BackofficeUserTable,UserDetail}.tsx` |
| G360F-0098 | Feature `audit`: `/backoffice/audit-logs` con filtros y `AuditTrail` | impl | F2 | RF-08.6 | G360F-0093 | `src/features/audit/*`, `src/app/backoffice/audit-logs/page.tsx` |
| G360F-0099 | Tests de menú, catálogos, roles, asignaciones, usuarios y auditoría | test | F2 | CA-08.1, CA-08.2, CA-08.3, CA-08.4, CA-08.5, CA-08.6 | G360F-0094, G360F-0097, G360F-0098 | `src/app/backoffice/_nav.test.ts`, `src/features/{catalog,rbac,user,audit}/**/*.test.ts(x)` |
| G360F-0100 | E2E del superadmin: catálogo de prueba, rol nuevo asignado y revocado, estado de un usuario y auditoría | test | F2 | CA-08.1, CA-08.2, CA-08.4, CA-08.5 | G360F-0099, G360F-0055 | `e2e/backoffice-platform.spec.ts` |
| G360F-0101 | Invitar personal interno con roles globales asignables | impl | F3 | RF-08.7 | G360F-0097, G360F-0068 | `src/app/backoffice/users/page.tsx`, `src/features/onboarding/{api,actions}.ts` |
| G360F-0102 | Pestaña de categorías de servicio | impl | F3 | RF-08.8 | G360F-0094 | `src/features/catalog/components/ServiceCategoryForm.tsx`, `src/features/catalog/actions.ts` |
| G360F-0103 | Tests y E2E de la invitación interna y de las categorías | test | F3 | CA-08.6, CA-08.7, CA-08.8 | G360F-0101, G360F-0102, G360F-0060 | `src/features/{onboarding,catalog}/**/*.test.ts(x)`, `e2e/backoffice-platform-f3.spec.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Exportar la auditoría y que los administradores de empresa la consulten: post-MVP (`backend/01 §11`).
- Roles de Legal, Tecnología y Personal: F11.
- **Backend/04** — `GET /users` no filtra a los usuarios internos (`companyId` nulo) y no trae los nombres de las personas. Por defecto: un solo listado con la columna Empresa («Global 360» para los internos) y los nombres resueltos con `GET /persons/:id` por fila (20 llamadas en paralelo como mucho); se pide el filtro `internal=true` y `person{firstName, lastName}` en la respuesta.
- **Backend/01** — La auditoría solo trae `actorId`. Por defecto: el correo del actor se resuelve con `GET /users/:id` por fila; se pide incluir el correo del actor en la entrada.
