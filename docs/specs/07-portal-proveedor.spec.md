# Spec 07 — Portal del proveedor (`provider`, `service`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/provider`, `src/features/service` |
| Rutas | `/provider`, `/provider/services`, `/provider/services/new`, `/provider/services/[id]` |
| Backend | `backend/08` (Implementada), `backend/10` (Aprobada) |
| Depende de | Specs 00, 01, 02 y 05 |

## 1. Resumen y alcance

Permite a una empresa `provider` o `both` completar su perfil de proveedor, enviarlo a revisión de Global 360, ver en qué estado está y gestionar sus servicios (crear, editar, publicar, despublicar y archivar). La aprobación, la publicación y la suspensión del perfil las hace Global 360 desde el backoffice (spec 09), igual que habilitar un servicio en una ruta.

No hay maqueta de estas pantallas: se construyen con el kit y los patrones del portal del cliente (constitución §8).

## 2. Origen

| Requisito | Fuente |
|---|---|
| Pasos del proveedor: registrarse, completar el perfil (cobertura, categorías, capacidades, certificaciones), revisión y publicación | Artboard `MvpSoyProveedor` |
| Lo que el marketplace muestra del proveedor y del servicio | Artboards `MvpProveedor` y `MvpServicio` |
| Campos del perfil, límites, `PATCH` parcial, estados editables y transiciones | `backend/08 §4` y §5 (RF-08.2, RF-08.3) |
| Campos del servicio, límites, estados, publicar solo con el proveedor publicado | `backend/08 §4` y §5 (RF-08.6 a RF-08.8) |
| El proveedor se crea en borrador al registrarse (`_id` = `companyId`) | `backend/07 §4` y `backend/08` |
| Rutas habilitadas de un servicio publicado (`inquiryPrefill.corridorIds`) | `backend/10 §4` (RF-10.5) |

## 3. Requisitos funcionales

- **RF-07.1** — Contratos y lecturas.
  - `features/provider`: esquema del perfil interno de `backend/08 §4` (con `operationalContact` siempre objeto, `reviewNotes`, `statusReason` y fechas nulas), `PROVIDER_LIMITS` (nombre 120, resumen 300, descripción 3000, URL 300, años 0–200, 50 países, 20 categorías, 20 capacidades y certificaciones de 1 a 80) y `api.ts` con `getProvider`, `updateProvider` y `submitProvider`.
  - `features/service`: esquema del servicio, `SERVICE_LIMITS` (nombre 120, descripción 2000, condiciones 1000, 1–10 transportes, 1–50 países, tránsito 1–365) y `api.ts` con `listProviderServices`, `getService`, `createService`, `updateService`, `publishService`, `unpublishService` y `archiveService`.
  - El ID del proveedor es el `companyId` del usuario.
- **RF-07.2** — Menú e inicio.
  - `_nav.ts` añade «Perfil de proveedor» (`/provider`, `provider:read`) y «Servicios» (`/provider/services`, `service:read`) en un grupo «Proveedor».
  - El inicio del portal añade, con `provider:read`, el bloque del perfil con su estado y el siguiente paso: `draft` «Completa tu perfil y envíalo a revisión»; `in_review` «Global 360 está revisando tu perfil»; `approved` «Tu perfil fue aprobado. Global 360 lo publicará pronto.»; `published` «Tu perfil está publicado en el marketplace» con «Ver mi perfil público»; `unpublished` y `suspended` con su `statusReason`. Si un rechazo dejó `reviewNotes`, «Global 360 pidió cambios: [notas]».
- **RF-07.3** — Perfil `/provider` (`provider:read`).
  - Con `provider:manage` y el perfil en `draft`, `approved`, `published` o `unpublished`, formulario con: nombre visible*, resumen* (contador de 300), descripción* (contador de 3000), sitio web (`https://`, «No se muestra en el marketplace»), URL del logo (`https://`, con vista previa), años en operación, países de cobertura* y categorías* (casillas desde los catálogos), capacidades y certificaciones (`TagsInput`, spec 05) y contacto operativo (nombre, correo, teléfono; «Solo lo ve Global 360»).
  - En `in_review` o `suspended`, o sin `provider:manage`, los mismos datos en solo lectura con su motivo («Tu perfil está en revisión: no se puede editar hasta que Global 360 responda.»).
  - La Server Action envía solo los campos que cambiaron (`PATCH` parcial); un opcional vaciado va como `""` (o `[]`, o `operationalContact: {}`). En `published` se avisa: «Los cambios se publican de inmediato en el marketplace.».
- **RF-07.4** — Enviar a revisión.
  - En `draft`, con `provider:manage`, «Enviar a revisión» llama a `POST /providers/:id/submit`; con éxito, el estado pasa a «En revisión».
  - Como pista (no bloquea el botón; la API decide), una lista «Para enviar a revisión completa:» con los obligatorios vacíos de `backend/08` (nombre, resumen, descripción, al menos un país y una categoría). `PROVIDER_PROFILE_INCOMPLETE` muestra «Completa los datos obligatorios del perfil antes de enviarlo.».
- **RF-07.5** — Servicios `/provider/services` (`service:read`).
  - Tabla paginada de `GET /providers/:id/services` con filtro de estado: nombre (enlace a la edición), categoría, orígenes → destinos, transportes, estado y última actualización.
  - «Nuevo servicio» con `service:manage`. Si el perfil no está `published`: «Podrás publicar servicios cuando tu perfil esté publicado. Mientras tanto puedes dejarlos en borrador.».
  - Vacío: «Aún no tienes servicios. Crea el primero para que las empresas puedan pedir una cotización.».
- **RF-07.6** — Crear y editar un servicio.
  - `/provider/services/new` y `/provider/services/[id]` con el mismo formulario: categoría*, nombre*, descripción, tipos de transporte* (casillas), países de origen* y de destino* (casillas), tránsito estimado mínimo y máximo (opcionales, los dos o ninguno) y condiciones.
  - Alta: `POST /providers/:id/services` y redirección a `/provider/services/[id]` con «Servicio creado en borrador.». Edición: `PATCH /services/:id` con los campos cambiados (tránsito vaciado como `{}`, descripción y condiciones como `""`). Un servicio `archived` se muestra en solo lectura.
  - Con el servicio y el perfil publicados, «Ver en el marketplace» y «Rutas habilitadas» (nombres de los corredores de `inquiryPrefill.corridorIds` de `GET /marketplace/services/:id`), con la nota «Para que se pueda cotizar en línea, Global 360 habilita el servicio en una ruta activa.».
- **RF-07.7** — Estado del servicio. Acciones según el estado y `service:manage`: «Publicar» (`draft` o `unpublished`), «Despublicar» (`published`, motivo opcional en `ConfirmDialog`) y «Archivar» (`draft`, `published` o `unpublished`; `ConfirmDialog`: «Archivar es definitivo: el servicio deja de verse y no se puede volver a publicar.»).

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/portal` (bloque del proveedor) | `provider:read` en su empresa | — | RF-07.2 |
| `/provider` | `provider:read` en su empresa | — (sin maqueta) | RF-07.3, RF-07.4 |
| `/provider/services` | `service:read` en su empresa | — | RF-07.5 |
| `/provider/services/new` | `service:manage` en su empresa | — | RF-07.6 |
| `/provider/services/[id]` | `service:read` (la API aísla por empresa) | — | RF-07.6, RF-07.7 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /providers/:id`, `PATCH /providers/:id` | `backend/08 §4` (RF-08.2, RF-08.4) | RF-07.2, RF-07.3 |
| `POST /providers/:id/submit` | `backend/08 §4` (RF-08.3) | RF-07.4 |
| `GET /providers/:id/services?status=&categoryId=&page=&pageSize=`, `POST /providers/:id/services` | `backend/08 §4` (RF-08.6, RF-08.8) | RF-07.5, RF-07.6 |
| `GET /services/:id`, `PATCH /services/:id` | `backend/08 §4` | RF-07.6 |
| `POST /services/:id/publish`, `/unpublish {reason?}`, `/archive` | `backend/08 §4` (RF-08.7) | RF-07.7 |
| `GET /marketplace/services/:id` | `backend/10 §4` | Rutas habilitadas (RF-07.6, vía `marketplace`) |
| `GET /countries`, `/transport-types`, `/service-categories` | `backend/02 §4`, `backend/08 §4` | Opciones (vía `catalog`) |

| Código | Campo o lugar | Mensaje |
|---|---|---|
| `PROVIDER_PROFILE_INVALID` | el campo correspondiente | Revisa el dato: supera el largo permitido o la URL no empieza por https://. |
| `PROVIDER_COUNTRY_INVALID` / `PROVIDER_CATEGORY_INVALID` | `coverageCountryIds` / `categoryIds` | Hay un país o una categoría que ya no está disponible: quítalo. |
| `PROVIDER_PROFILE_INCOMPLETE` | — | Completa los datos obligatorios del perfil antes de enviarlo. |
| `PROVIDER_NOT_EDITABLE` | — | Tu perfil no se puede editar en su estado actual. |
| `PROVIDER_INVALID_STATUS_TRANSITION` | — | El perfil ya cambió de estado. Recarga la página. |
| `SERVICE_NAME_REQUIRED` | `name` | Escribe el nombre del servicio (hasta 120 caracteres). |
| `SERVICE_DESCRIPTION_INVALID` / `SERVICE_CONDITIONS_INVALID` | `description` / `conditions` | Hasta 2000 / 1000 caracteres. |
| `SERVICE_TRANSIT_DAYS_INVALID` | `estimatedTransitDays` | El tránsito va de 1 a 365 días y el mínimo no puede superar al máximo. |
| `SERVICE_CATEGORY_INVALID`, `SERVICE_TRANSPORT_TYPE_INVALID`, `SERVICE_COUNTRY_INVALID` | el campo correspondiente | Elige opciones de la lista. |
| `SERVICE_PROVIDER_NOT_PUBLISHED` | — | Podrás publicar el servicio cuando tu perfil esté publicado. |
| `SERVICE_NOT_EDITABLE` | — | Un servicio archivado no se puede editar. |
| `SERVICE_INVALID_STATUS_TRANSITION` | — | El servicio ya cambió de estado. Recarga la página. |
| `PROVIDER_NOT_FOUND`, `SERVICE_NOT_FOUND` | — | `notFound()` |

## 6. Estados y reglas de la interfaz

| Estado del proveedor | Etiqueta | Tono |
|---|---|---|
| `draft` | Borrador | `neutral` |
| `in_review` | En revisión | `info` |
| `approved` | Aprobado | `info` |
| `published` | Publicado | `success` |
| `unpublished` | Despublicado | `warning` |
| `suspended` | Suspendido | `danger` |

| Estado del servicio | Etiqueta | Tono |
|---|---|---|
| `draft` | Borrador | `neutral` |
| `published` | Publicado | `success` |
| `unpublished` | Despublicado | `warning` |
| `archived` | Archivado | `neutral` |

- Qué estados se editan y qué acción hay en cada estado sale de `backend/08 §5`, en `model.ts`; si la API responde distinto, manda la API.
- El perfil del proveedor nunca muestra precios.

## 7. Componentes, datos y caché

- `features/provider/components/{ProviderStatusBlock,ProviderForm,SubmitForReview}.tsx`; `features/service/components/{ServiceTable,ServiceForm,ServiceStatusActions,EnabledRoutes}.tsx`.
- Tras publicar o despublicar un servicio, o editar un perfil publicado, la acción llama a `updateTag('marketplace')` para que el marketplace se actualice.
- Logo con `<img>` (constitución §11).

## 8. Accesibilidad y SEO

- Las listas de casillas (países, categorías, transportes) van en `<fieldset>` con `<legend>` y un contador de seleccionados.
- La vista previa del logo tiene `alt` con el nombre del proveedor.
- Rutas privadas: `noindex`.

## 9. Criterios de aceptación

- **CA-07.1** (RF-07.1) — Los esquemas aceptan los ejemplos de `backend/08 §4` (perfil con `website: null` y `operationalContact` con `null` en sus campos; servicio con `estimatedTransitDays: null`). `PROVIDER_LIMITS` y `SERVICE_LIMITS` coinciden con los de `backend/08 §4`.
- **CA-07.2** (RF-07.2) — `_nav` con los grants de `provider_admin` incluye el grupo Proveedor y no Solicitudes; una empresa `both` con `client_admin` y `provider_admin` ve los dos. El bloque del inicio de un perfil rechazado muestra «Global 360 pidió cambios» con las notas.
- **CA-07.3** (RF-07.3) — Con el perfil `in_review`, `/provider` se muestra en solo lectura con su aviso; con `provider_operator`, también. La acción que solo cambia el resumen envía `{summary}` y nada más; vaciar el sitio web envía `website: ""`.
- **CA-07.4** (RF-07.4) — Con el perfil en `draft` sin categorías, la pista lista «al menos una categoría» y el botón sigue activo; con `PROVIDER_PROFILE_INCOMPLETE`, el mensaje de §5. Un envío correcto deja el perfil «En revisión».
- **CA-07.5** (RF-07.5) — Con el perfil no publicado, la lista muestra el aviso de publicación; sin servicios, el estado vacío; con `service:manage`, «Nuevo servicio».
- **CA-07.6** (RF-07.6) — El formulario con solo el tránsito mínimo no envía (los dos o ninguno) y con los dos los envía como `{min, max}`; al editar, vaciarlos envía `estimatedTransitDays: {}`. Un alta correcta redirige a `/provider/services/[id]` con «Servicio creado en borrador.». Un servicio publicado de un proveedor publicado muestra «Ver en el marketplace» y sus rutas habilitadas.
- **CA-07.7** (RF-07.7) — Un servicio `draft` ofrece Publicar y Archivar; uno `published`, Despublicar y Archivar; uno `archived`, ninguna acción. Publicar con `SERVICE_PROVIDER_NOT_PUBLISHED` muestra su mensaje. Archivar pide confirmación. En la E2E, un proveedor registrado completa y envía su perfil, Global 360 lo aprueba y lo publica por API, el proveedor crea y publica un servicio y este aparece en `/marketplace`.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0084 | Features `provider` y `service`: contratos, límites, `api.ts`, modelos (etiquetas, estados editables, acciones por estado, pista de obligatorios) y mensajes | impl | F3 | RF-07.1 | G360F-0011, G360F-0012 | `src/features/{provider,service}/{contracts,api,model,messages}.ts` |
| G360F-0085 | Menú del grupo Proveedor y bloque del perfil en el inicio | impl | F3 | RF-07.2 | G360F-0084, G360F-0062 | `src/app/(portal)/{_nav.ts,portal/page.tsx}`, `src/features/provider/components/ProviderStatusBlock.tsx` |
| G360F-0086 | `/provider`: formulario del perfil con `PATCH` parcial, solo lectura por estado o permiso, y envío a revisión | impl | F3 | RF-07.3, RF-07.4 | G360F-0084, G360F-0066 | `src/app/(portal)/provider/page.tsx`, `src/features/provider/{actions.ts,components/{ProviderForm,SubmitForReview}.tsx}` |
| G360F-0087 | `/provider/services`: tabla con filtro de estado, avisos y vacío | impl | F3 | RF-07.5 | G360F-0084, G360F-0062 | `src/app/(portal)/provider/services/page.tsx`, `src/features/service/components/ServiceTable.tsx` |
| G360F-0088 | Alta y edición de un servicio, con rutas habilitadas si está publicado | impl | F3 | RF-07.6 | G360F-0087 | `src/app/(portal)/provider/services/{new,[id]}/page.tsx`, `src/features/service/{actions.ts,components/{ServiceForm,EnabledRoutes}.tsx}` |
| G360F-0089 | Acciones de estado del servicio con confirmaciones y `updateTag('marketplace')` | impl | F3 | RF-07.7 | G360F-0088 | `src/features/service/{actions.ts,components/ServiceStatusActions.tsx}` |
| G360F-0090 | Tests de contratos y modelos de proveedor y servicio | test | F3 | CA-07.1, CA-07.4, CA-07.7 | G360F-0084 | `src/features/{provider,service}/*.test.ts` |
| G360F-0091 | Tests de acciones y componentes (permisos, solo lectura, `PATCH` parcial, tránsito, errores de publicación) | test | F3 | CA-07.2, CA-07.3, CA-07.5, CA-07.6, CA-07.7 | G360F-0085, G360F-0086, G360F-0089 | `src/features/{provider,service}/**/*.test.tsx`, `src/app/(portal)/_nav.test.ts` |
| G360F-0092 | E2E del proveedor: perfil, revisión y publicación (backoffice por API), servicio publicado visible en el marketplace | test | F3 | CA-07.3, CA-07.4, CA-07.6, CA-07.7 | G360F-0091, G360F-0060 | `e2e/provider-portal.spec.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Desempeño y calificación del proveedor, y ver las solicitudes o cotizaciones en las que participa: post-MVP (`backend/08 §11`, `backend/12 §11`).
- Revisión de servicios por Global 360 antes de publicarlos: no existe; Global 360 puede despublicarlos (`backend/08 §11`).
- **Pregunta:** ¿el proveedor puede ver en qué rutas está habilitado un servicio antes de publicarlo? Solo hay un dato público para servicios publicados. Por defecto: «Rutas habilitadas» solo en servicios publicados.
- **Backend/08** — El logo es una URL `https` externa (la carga de archivos llega en F8). Por defecto: el formulario pide la URL y muestra una vista previa.
- **Backend/08** — No hay lectura de las rutas en que está habilitado un servicio para su propio proveedor (la fila de `corridor_services` es interna). Por defecto: se usa `inquiryPrefill.corridorIds` del marketplace, solo para servicios publicados.
