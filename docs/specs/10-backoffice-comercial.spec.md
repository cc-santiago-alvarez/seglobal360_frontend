# Spec 10 — Backoffice comercial: solicitudes y cotizador (`inquiry`, `quote`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/inquiry`, `src/features/quote` (vistas internas) |
| Rutas | `/backoffice/inquiries`, `/backoffice/inquiries/[id]`, `/backoffice/quotes`, `/backoffice/quotes/[id]` |
| Backend | `backend/11` (Implementada), `backend/12` (Aprobada; capa HTTP en curso, G360-0149), `backend/09` (Implementada) |
| Depende de | Specs 00, 01, 06, 08 y 09 |

## 1. Resumen y alcance

Es el puesto de trabajo del asesor de Global 360: ver las solicitudes nuevas y las suyas, tomarlas o asignarlas, conversar con el cliente (con notas internas y mensajes compartidos), armar la cotización con sus conceptos, enviarla, revisarla y ver la respuesta del cliente. También permite crear una solicitud a nombre de un cliente. Las rutas `/backoffice/inquiries/[id]` y `/backoffice/quotes/[id]` son el destino de los emails `inquiry_received`, `inquiry_assigned`, `inquiry_message_to_advisor`, `quote_accepted` y `quote_rejected`.

La bandeja de trabajo, los reportes y las correcciones manuales son de la spec 11.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Criterio de F5 (asesor asignado, contacto, cotización versionada, aceptación) | `backend/CLAUDE.md`, *Alcance y fases* |
| Asignar, tomar, cancelar, cerrar como perdida; quién puede cada cosa | `backend/11 §4` y §5 (RF-11.2, RF-11.4) |
| Interacciones: canales, visibilidad, `occurredAt`, paso a `in_contact` | `backend/11 §4` y §5 (RF-11.3) |
| Solicitud creada por el personal (`requestedBy`, `source: backoffice`) | `backend/11 §4` (RF-11.1) |
| Cotización: crear con moneda, borrador que reemplaza la versión, enviar, revisar, versiones inmutables, vista interna | `backend/12 §4` y §5 (RF-12.1 a RF-12.4, RF-12.7, RF-12.8) |
| Enlaces de los emails al backoffice | `backend/06`, `backend/11`, `backend/12` |

## 3. Requisitos funcionales

- **RF-10.1** — Vistas internas y menú.
  - `features/inquiry` añade `assignInquiry`, `claimInquiry` y `closeInquiryAsLost`, y la creación con `requestedBy`. `features/quote` añade el esquema de la **vista interna** (versión actual con componentes, subtotal, comisión `{ruleVersion, type, rateBps, amount}`, total, vigencia, fechas y versiones anteriores, según lo que publique G360-0149; ver §11) y `createQuote`, `saveQuoteDraft`, `sendQuote` y `reviseQuote`.
  - `backoffice/_nav.ts` añade Solicitudes (`inquiry:read`) y Cotizaciones (`quote:read`) al grupo Operación.
- **RF-10.2** — Solicitudes `/backoffice/inquiries` (`inquiry:read` global).
  - Pestañas: «Sin asignar» (`status=new`), «Mías» (`advisorId=me`) y Todas; filtros de estado, ruta, origen (`source`) y rango de fechas.
  - Tabla: código, empresa (nombre), ruta, transporte, origen (Marketplace, Directa, Backoffice), estado, asesor (correo o «Sin asignar»), creada y primer contacto. Orden de la API (más recientes primero).
- **RF-10.3** — Detalle `/backoffice/inquiries/[id]` (`inquiry:read` global).
  - Cabecera con código, estado, empresa (enlace a `/backoffice/companies/[id]`), ruta, transporte y origen; datos completos de la solicitud (como la spec 06, con el solicitante y el servicio de partida); línea de tiempo con fechas; `AuditTrail`.
  - Acciones según el estado y los permisos:
    - «Tomar» (`new`, `inquiry:advise`): `POST /inquiries/:id/claim`;
    - «Asignar» o «Reasignar» (`new`, `assigned`, `in_contact` o `quoted`, con `inquiry:assign`): busca un usuario interno por correo y llama a `POST /inquiries/:id/assign {advisorId}`; la API valida que sea asesor (`INQUIRY_ADVISOR_INVALID`);
    - «Cerrar como perdida» (`in_contact` o `quoted`): motivo obligatorio;
    - «Cancelar» (`new`, `assigned` o `in_contact`): motivo obligatorio.

    Las de cerrar y cancelar se muestran al asesor asignado y a quien tiene `inquiry:manage`; la API decide.
  - Panel de la cotización: sin cotización y en `in_contact`, «Crear cotización» (RF-10.5); con cotización, su código, estado efectivo, versión, total y enlace a `/backoffice/quotes/[id]`.
- **RF-10.4** — Conversación del asesor.
  - Todas las interacciones, internas y compartidas, de la más antigua a la más reciente (la API las da al revés), con su canal, autor («Cliente» o el asesor), fecha y la insignia «Interna» o «Compartida con el cliente».
  - Redactor: canal (`phone`, `email`, `whatsapp`, `meeting`, `video_call`, `note`), fecha y hora en que ocurrió (por defecto, ahora; no puede ser futura), visibilidad (por defecto «Interna»; «Compartida con el cliente» avisa por correo al cliente) y resumen (1 a 2000). Llama a `POST /inquiries/:id/interactions`.
  - Pista: «La primera interacción que no sea una nota interna pasa la solicitud a En conversación.». En `won`, `lost` o `cancelled` el redactor se deshabilita.
- **RF-10.5** — Crear la cotización. «Crear cotización» pide la moneda (una de las del corredor) y llama a `POST /inquiries/:inquiryId/quotes {currency}`; con 201, lleva a `/backoffice/quotes/[id]`. `QUOTE_ALREADY_EXISTS` enlaza a la existente; `QUOTE_INQUIRY_NOT_QUOTABLE`: «Solo se cotiza una solicitud en conversación.».
- **RF-10.6** — Cotizador `/backoffice/quotes/[id]` (`quote:read` global).
  - Cabecera: código, estado efectivo, solicitud (enlace), empresa, asesor, moneda, versión actual y vigencia.
  - En `draft`, con `quote:create`, editor de la versión actual:
    - conceptos (1 a 50 filas: concepto 1–120, descripción hasta 500, proveedor y servicio opcionales, monto en la moneda de la cotización con `parseMoneyInput`), con «Agregar concepto» y «Quitar»;
    - notas para el cliente y notas internas (hasta 2000 cada una).

    «Guardar borrador» llama a `PUT /quotes/:id/draft`, que **reemplaza la versión entera**, y muestra el subtotal, la comisión y el total que devuelve la API («Calculado con la regla vigente; se recalcula al enviar»). El front no suma montos.
  - «Enviar al cliente» (`draft` con al menos un concepto, `quote:send`): `ConfirmDialog` con el total del último borrador y la vigencia del corredor («Vencerá [n] días después del envío»); llama a `POST /quotes/:id/send`.
  - «Crear versión nueva» (`sent`, `rejected` o `expired`, `quote:create`): `POST /quotes/:id/revise`, que copia la versión anterior en un borrador nuevo. Aviso: «Mientras la nueva versión esté en borrador, el cliente no verá ninguna cotización.».
  - Respuesta del cliente: aceptada (versión y fecha) o rechazada (versión, fecha y motivo).
  - Historial de versiones anteriores en solo lectura: conceptos con montos, subtotal, comisión (tipo, tasa o monto y versión de la regla), total, envío y vigencia.
- **RF-10.7** — Cotizaciones `/backoffice/quotes` (`quote:read` global). Pestañas «Mías» (`advisorId=me`) y Todas, y filtros de estado efectivo, ruta y fechas; tabla con código, solicitud, empresa, estado, versión, total de la versión actual, vigencia y asesor.
- **RF-10.8** — Solicitud a nombre de un cliente. En `/backoffice/companies/[id]` de una empresa cliente activa, con `inquiry:manage`, «Crear solicitud» abre el asistente de la spec 06 con un paso previo «Solicitante» (un usuario activo de esa empresa) y envía `requestedBy`. Con 201 lleva al detalle del backoffice.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/backoffice/inquiries?tab=&status=&corridorId=&source=&from=&to=&page=` | `inquiry:read` global | — (sin maqueta) | RF-10.2 |
| `/backoffice/inquiries/[id]` | `inquiry:read` global (enlace de los emails) | — | RF-10.3, RF-10.4, RF-10.5 |
| `/backoffice/quotes?tab=&status=&corridorId=&from=&to=&page=` | `quote:read` global | — | RF-10.7 |
| `/backoffice/quotes/[id]` | `quote:read` global (enlace de los emails) | — | RF-10.6 |
| `/backoffice/companies/[id]/inquiries/new` | `inquiry:manage` global | `PortalNuevaSolicitud` (reutilizado) | RF-10.8 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /inquiries?status=&corridorId=&source=&advisorId=&companyId=&from=&to=&page=&pageSize=`, `GET /inquiries/:id` | `backend/11 §4` | RF-10.2, RF-10.3 |
| `POST /inquiries/:id/claim`, `POST /inquiries/:id/assign {advisorId}` | `backend/11 §4` (RF-11.2) | RF-10.3 |
| `POST /inquiries/:id/close-lost {reason}`, `POST /inquiries/:id/cancel {reason}` | `backend/11 §4` (RF-11.4) | RF-10.3 |
| `GET /inquiries/:id/interactions`, `POST /inquiries/:id/interactions {channel, summary, occurredAt, visibility}` | `backend/11 §4` (RF-11.3) | RF-10.4 |
| `POST /companies/:id/inquiries` (con `requestedBy`) | `backend/11 §4` (RF-11.1) | RF-10.8 |
| `POST /inquiries/:inquiryId/quotes {currency}` | `backend/12 §4` (RF-12.1) | RF-10.5 |
| `GET /quotes?…`, `GET /quotes/:id` (vista interna) | `backend/12 §4` (RF-12.7, RF-12.8) | RF-10.3, RF-10.6, RF-10.7 |
| `PUT /quotes/:id/draft {components, clientNotes, internalNotes}` | `backend/12 §4` (RF-12.2) | RF-10.6 |
| `POST /quotes/:id/send`, `POST /quotes/:id/revise` | `backend/12 §4` (RF-12.3, RF-12.4) | RF-10.6 |
| `GET /users?q=`, `GET /users/:id`, `GET /companies/:id` | `backend/04 §4` | Asesores, autores y empresas por fila |
| `GET /providers`, `GET /providers/:id/services` | `backend/08 §4` | Proveedor y servicio opcionales de un concepto |

| Código | Mensaje |
|---|---|
| `INQUIRY_ADVISOR_INVALID` | Esa persona no es un asesor activo de Global 360. |
| `INQUIRY_INVALID_STATUS_TRANSITION` | La solicitud ya cambió de estado (otra persona pudo tomarla). Recarga la página. |
| `INQUIRY_REASON_REQUIRED` | Escribe el motivo (hasta 500 caracteres). |
| `INQUIRY_INTERACTION_INVALID` | Revisa el canal y el resumen (hasta 2000 caracteres); la fecha no puede ser futura. |
| `INQUIRY_REQUESTER_INVALID` | El solicitante debe ser un usuario activo de esa empresa. |
| `FORBIDDEN` (al escribir, cerrar o cancelar) | Solo el asesor asignado o un administrador pueden hacer esto. |
| `QUOTE_ALREADY_EXISTS` | Esta solicitud ya tiene una cotización: ábrela. |
| `QUOTE_INQUIRY_NOT_QUOTABLE` | Solo se cotiza una solicitud en conversación. |
| `QUOTE_CURRENCY_INVALID` | Elige una moneda de la ruta. |
| `QUOTE_COMPONENTS_INVALID` | Revisa los conceptos: de 1 a 50, con nombre de hasta 120 caracteres y montos sin negativos. |
| `QUOTE_CURRENCY_MISMATCH` | Todos los montos van en la moneda de la cotización. |
| `QUOTE_NOTES_INVALID` | Las notas admiten hasta 2000 caracteres. |
| `QUOTE_NOT_EDITABLE` | Esta versión ya se envió: crea una versión nueva para cambiarla. |
| `QUOTE_INVALID_STATUS_TRANSITION` | La cotización ya cambió de estado, o el borrador no tiene conceptos. |
| `QUOTE_TERMS_INVALID`, `CORRIDOR_NOT_ACTIVE`, `COMMISSION_RULE_NOT_FOUND`, `COMMISSION_RULE_CURRENCY_NOT_COVERED` | No se puede enviar: la ruta no está activa o no tiene una regla de comisión vigente para esta moneda. |
| `QUOTE_INQUIRY_CLOSED` | La solicitud está cerrada. |
| `MONEY_AMOUNT_OVERFLOW` | Un monto es demasiado grande. |

## 6. Estados y reglas de la interfaz

| Estado efectivo de la cotización (vista interna) | Etiqueta | Tono |
|---|---|---|
| `draft` | Borrador | `neutral` |
| `sent` | Enviada | `info` |
| `accepted` | Aceptada | `success` |
| `rejected` | Rechazada | `danger` |
| `expired` | Vencida | `warning` |

- Estados de la solicitud: los de la spec 06. Origen: `marketplace` Marketplace, `direct` Directa, `backoffice` Backoffice. Canales: `phone` Llamada, `email` Correo, `whatsapp` WhatsApp, `meeting` Reunión, `video_call` Videollamada, `note` Nota, `portal_message` Mensaje del portal.
- La comisión y los montos por concepto solo se muestran aquí, al personal con `quote:read` interno (`backend/12 RF-12.8`).
- Ninguna cifra la calcula el front: subtotal, comisión, total y vigencia vienen de la API.

## 7. Componentes, datos y caché

- `features/inquiry/components/{BackofficeInquiryTable,AdvisorActions,AssignAdvisor,AdvisorConversation,InteractionComposer,QuoteSummary}.tsx`; `features/quote/components/{QuoteEditor,ComponentRows,QuoteTotals,SendQuote,ReviseQuote,QuoteVersions,BackofficeQuoteTable}.tsx`.
- `ComponentRows` es un Client Component con filas dinámicas que serializa un `components` JSON en un campo oculto; la Server Action lo parsea con zod y convierte cada monto a unidades menores.
- Nombres de empresa, asesor y autores resueltos por página con `React.cache`. Tras cada acción, `refresh()`.

## 8. Accesibilidad y SEO

- Las filas de conceptos tienen etiquetas por fila («Concepto 2: monto») y «Quitar» con nombre accesible.
- La insignia «Interna» o «Compartida» va en texto, no solo en color.
- `noindex`.

## 9. Criterios de aceptación

- **CA-10.1** (RF-10.1) — `_nav` con los grants de `operations` incluye Solicitudes y Cotizaciones; con los de `finance`, solo Cotizaciones. El esquema interno de la cotización acepta el ejemplo de `backend/12 §4` y rechaza uno sin `version.total`.
- **CA-10.2** (RF-10.2) — La pestaña «Mías» llama a `GET /inquiries?advisorId=me` y «Sin asignar», a `status=new`. Una solicitud sin asesor muestra «Sin asignar» y una de origen `marketplace`, «Marketplace».
- **CA-10.3** (RF-10.3) — Una solicitud `new` ofrece Tomar y Asignar; tras Tomar queda `assigned` con el asesor actual. Asignar a un usuario que no es asesor muestra el mensaje de `INQUIRY_ADVISOR_INVALID`. Cerrar como perdida sin motivo no envía. El enlace del email `inquiry_assigned` abre el detalle.
- **CA-10.4** (RF-10.4) — Con las interacciones de la API en orden descendente, la conversación las muestra en orden ascendente con su insignia. El redactor envía por defecto `visibility: "internal"` y `occurredAt` ahora; una fecha futura no se envía. Un mensaje compartido del asesor aparece en la conversación del cliente (spec 06).
- **CA-10.5** (RF-10.5) — Crear la cotización en una solicitud `assigned` muestra el mensaje de `QUOTE_INQUIRY_NOT_QUOTABLE`; en `in_contact`, crea el borrador y lleva al cotizador. Con `QUOTE_ALREADY_EXISTS`, se ofrece el enlace a la existente.
- **CA-10.6** (RF-10.6) — Guardar un borrador con dos conceptos de «1500» y «300,50» USD envía `components` con montos 150000 y 30050 y muestra el subtotal, la comisión y el total que devuelve la API, sin calcularlos. «Enviar al cliente» no aparece con cero conceptos. Tras enviar, el estado es «Enviada» y la solicitud, «Cotizada»; «Crear versión nueva» deja la versión 2 en borrador con los conceptos copiados y la 1 en el historial. En la E2E, un cliente acepta (spec 06) y el cotizador muestra «Aceptada» con la versión.
- **CA-10.7** (RF-10.7) — `/backoffice/quotes?tab=mine&status=sent` llama a `GET /quotes?advisorId=me&status=sent`; una cotización `sent` vencida aparece como «Vencida» (el estado efectivo de la API).
- **CA-10.8** (RF-10.8) — La solicitud a nombre de un cliente envía `requestedBy` con el usuario elegido y, con 201, lleva a `/backoffice/inquiries/[id]`, que muestra el origen «Backoffice».

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0115 | Vistas internas de `inquiry` y `quote` (contratos, `api.ts`, modelos, mensajes) y entradas del menú | impl | F5 | RF-10.1 | G360F-0072, G360F-0073, G360F-0093 | `src/features/{inquiry,quote}/{contracts,api,model,messages}.ts`, `src/app/backoffice/_nav.ts` |
| G360F-0116 | `/backoffice/inquiries`: pestañas, filtros y tabla con nombres | impl | F5 | RF-10.2 | G360F-0115 | `src/app/backoffice/inquiries/page.tsx`, `src/features/inquiry/components/BackofficeInquiryTable.tsx` |
| G360F-0117 | Detalle de la solicitud: datos, línea de tiempo, tomar, asignar, cerrar, cancelar e historial | impl | F5 | RF-10.3 | G360F-0116, G360F-0098 | `src/app/backoffice/inquiries/[id]/page.tsx`, `src/features/inquiry/{actions.ts,components/{AdvisorActions,AssignAdvisor,QuoteSummary}.tsx}` |
| G360F-0118 | Conversación del asesor con canal, fecha y visibilidad | impl | F5 | RF-10.4 | G360F-0117, G360F-0078 | `src/features/inquiry/components/{AdvisorConversation,InteractionComposer}.tsx` |
| G360F-0119 | Crear la cotización con la moneda de la ruta | impl | F5 | RF-10.5 | G360F-0117 | `src/features/quote/{actions.ts,components/CreateQuote.tsx}` |
| G360F-0120 | Cotizador: editor de conceptos, borrador, totales de la API, envío, versión nueva, respuesta e historial | impl | F5 | RF-10.6 | G360F-0119 | `src/app/backoffice/quotes/[id]/page.tsx`, `src/features/quote/components/{QuoteEditor,ComponentRows,QuoteTotals,SendQuote,ReviseQuote,QuoteVersions}.tsx` |
| G360F-0121 | `/backoffice/quotes`: pestañas, filtros y tabla | impl | F5 | RF-10.7 | G360F-0115 | `src/app/backoffice/quotes/page.tsx`, `src/features/quote/components/BackofficeQuoteTable.tsx` |
| G360F-0122 | Solicitud a nombre de un cliente con el paso «Solicitante» | impl | F5 | RF-10.8 | G360F-0117, G360F-0076, G360F-0105 | `src/app/backoffice/companies/[id]/inquiries/new/page.tsx`, `src/features/inquiry/components/InquiryWizard.tsx` |
| G360F-0123 | Tests de menú, contratos, acciones por estado, redactor, filas de conceptos y conversión de montos | test | F5 | CA-10.1, CA-10.2, CA-10.3, CA-10.4, CA-10.5, CA-10.6, CA-10.7, CA-10.8 | G360F-0118, G360F-0120, G360F-0121, G360F-0122 | `src/features/{inquiry,quote}/**/*.test.ts(x)`, `src/app/backoffice/_nav.test.ts` |
| G360F-0124 | E2E del asesor: tomar, conversar, cotizar, enviar, revisar y ver la aceptación del cliente | test | F5 | CA-10.3, CA-10.4, CA-10.5, CA-10.6, CA-10.7 | G360F-0123, G360F-0083 | `e2e/inquiry-quote-advisor.spec.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Asignación automática de asesores: no hay en el MVP (`backend/11 §11`).
- PDF de la cotización y vista del proveedor: post-MVP (`backend/12 §11`).
- **Pregunta:** si se reasigna la solicitud después de crear la cotización, la cotización conserva el asesor original (`backend/12 §11`). Por defecto: el cotizador muestra el asesor de la cotización y avisa si es distinto del de la solicitud.
- **Backend/12** — La vista interna de la cotización está pendiente de G360-0149: falta confirmar cómo se exponen las versiones anteriores, si incluye `inquiryId`, `advisorId`, `acceptedVersion`, `rejectionReason` y las fechas, y si `PUT /quotes/:id/draft` devuelve el subtotal, la comisión y el total calculados. Esta spec no pasa a *Aprobada* hasta confirmarlo. Por defecto: si el borrador no trae los totales, se muestra «Se calcula al enviar».
- **Backend/04** — No hay forma de listar a los asesores (usuarios internos con `inquiry:advise`). Por defecto: asignar busca usuarios por correo y la API valida que sea asesor; se pide un filtro `permission=inquiry:advise` en `GET /users`.
- **Backend/11** — La solicitud y sus interacciones no traen el nombre de la empresa, del asesor ni del autor. Por defecto: se resuelven por fila (`GET /companies/:id`, `GET /users/:id`); se pide incluirlos en la respuesta.
