# Spec 06 — Portal: solicitudes y cotizaciones (`inquiry`, `quote`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/inquiry`, `src/features/quote` |
| Rutas | `/inquiries`, `/inquiries/new`, `/inquiries/[id]`, `/quotes/[id]` |
| Backend | `backend/11` (Implementada), `backend/12` (Aprobada; capa HTTP en curso, G360-0149), `backend/10` (Aprobada) |
| Depende de | Specs 00, 01, 02 y 05 |

## 1. Resumen y alcance

Es el corazón del MVP para el cliente: crear una solicitud de cotización (directa o desde un servicio del marketplace), seguir su estado, conversar con el asesor de Global 360 y aceptar o rechazar en línea la cotización que este le envía. Incluye el bloque del inicio del portal con las cotizaciones por responder y las últimas solicitudes, y la página `/quotes/[id]` a la que enlaza el email `quote_sent`.

Lo que hace el asesor (tomar la solicitud, escribir notas internas, armar y enviar la cotización) está en la spec 10.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Inicio con cotizaciones por responder, «¿Qué necesitas mover?» y últimas solicitudes | Artboard `PortalInicio` y nota `nota-portal-flujo` |
| Listado con filtros de estado, ruta y fechas, columnas y paginación | Artboard `PortalSolicitudes` |
| Asistente de nueva solicitud en cuatro pasos, prellenado desde el marketplace, volumen en litros enteros | Artboard `PortalNuevaSolicitud` y nota `nota-portal-flujo` |
| Detalle: estado, cancelación con motivo, línea de tiempo, cotización con sus estados, conversación, asesor, datos | Artboard `PortalSolicitud` y nota `nota-portal-flujo` |
| Huecos del backend detectados en la maqueta (nombre del asesor, enlace de `quote_sent`, borradores, avisos, nombres de compañeros) | Nota `nota-portal-huecos` |
| Cuerpo de la solicitud, estados, interacciones y visibilidad, cancelación | `backend/11 §4` y §5 (RF-11.1, RF-11.3, RF-11.4, RF-11.6) |
| Vista del cliente de la cotización, estado efectivo, aceptar y rechazar con versión, idempotencia | `backend/12 §4` y §5 (RF-12.5 a RF-12.8) |
| Corredores activos e `inquiryPrefill` | `backend/10 §4` (RF-10.1, RF-10.5) |

## 3. Requisitos funcionales

- **RF-06.1** — Contratos y lecturas.
  - `features/inquiry`: esquemas de la solicitud y de la interacción tal como las da `backend/11 §4` (todos los campos, con los `null` de los vacíos y `desiredShipDate` en `AAAA-MM-DD`), `INQUIRY_LIMITS` (descripción 1000, notas 2000, ciudad 100, dirección 200, HS 20, resumen de interacción 2000, motivo 500) y `api.ts` con `listInquiries`, `getInquiry`, `createInquiry`, `listInteractions`, `createInteraction` y `cancelInquiry`.
  - `features/quote`: esquema de la **vista del cliente** de `backend/12 §4` (`_id, code, status, currentVersion, concepts[{concept, description}], total{amount, currency}, validUntil, clientNotes`, más los campos que confirme G360-0149; ver §11) y `api.ts` con `listQuotes`, `getQuote`, `acceptQuote` y `rejectQuote`.
  - Todo sin caché del servidor.
- **RF-06.2** — Menú e inicio del portal.
  - `_nav.ts` añade Solicitudes (`/inquiries`, con `inquiry:read` en la empresa) y la acción principal «Nueva solicitud» (spec 05, RF-05.1).
  - El inicio añade, para quien tiene `quote:read`, el bloque «Cotizaciones por responder ([n])» con `GET /quotes?status=sent&companyId=` (código, versión, total, vigencia y enlace a `/quotes/[id]`; vacío: «Aún no tienes cotizaciones. Llegan aquí cuando tu asesor responde una solicitud.»).
  - Y, con `inquiry:read`, «¿Qué necesitas mover?» (las rutas activas y «Nueva solicitud», deshabilitado con su motivo si la empresa no está activa) y «Últimas solicitudes» (`GET /inquiries?pageSize=5`: código, ruta, transporte, estado y fecha; vacío: «Aún no has creado solicitudes.»).
- **RF-06.3** — Listado `/inquiries` (`inquiry:read` en la empresa).
  - Filtros por URL: estado, ruta (corredores del marketplace) y rango de creación «Desde»/«Hasta» (fechas locales convertidas a RFC 3339 al inicio y al final del día en la zona del usuario).
  - Tabla de la más reciente a la más antigua: código (enlace al detalle), ruta, transporte, carga (descripción recortada a 60 caracteres), estado, cotización (derivada del estado: `quoted` → «Por responder», `won` → «Aceptada», si no «—») y fecha de creación. Paginación de 20.
  - «Nueva solicitud» con `inquiry:create`. Vacío: «Aún no has creado solicitudes.» o, con filtros, «No hay solicitudes con estos filtros».
- **RF-06.4** — Nueva solicitud `/inquiries/new?serviceId=` (`inquiry:create` en la empresa).
  - Si la empresa no está `active`, la página muestra el aviso de validación de la spec 05 en lugar del formulario.
  - Asistente en cuatro pasos sobre un único `<form>` (el Client Component muestra un paso a la vez con «Atrás» y «Siguiente»; sin JS se ven todos):
    1. **Ruta y transporte:** ruta entre los corredores activos (`GET /marketplace/corridors`) y tipo de transporte entre los de esa ruta. «Solo aparecen las rutas activas en la plataforma.»
    2. **Tu carga:** descripción*, bultos*, peso total (kg), volumen (m³), código arancelario (HS), valor declarado opcional (monto y moneda, entre las monedas de la ruta), mercancía peligrosa y refrigeración.
    3. **Origen y destino:** el país lo fija la ruta (se muestra); ciudad* y dirección de recogida y de entrega.
    4. **Detalles:** Incoterm (con «No lo sé todavía»), fecha deseada de despacho (mínimo hoy) y notas para el asesor.
  - Resumen lateral (ruta, transporte, servicio) y «Qué pasa después».
  - **Desde el marketplace:** con `serviceId`, la página pide `GET /marketplace/services/:id` y muestra «Desde el marketplace: [servicio] de [proveedor]. La ruta y el transporte ya vienen cargados.» con «Cambiar servicio» (quita el `serviceId`). Las rutas se limitan a `inquiryPrefill.corridorIds` y los transportes a los de `inquiryPrefill.transportTypeCodes` que también tenga la ruta; con una sola opción, viene seleccionada. Un `serviceId` inválido o sin `canRequestQuote` se ignora con un aviso.
  - La Server Action construye el cuerpo exacto de `backend/11 §4`: convierte el volumen a litros enteros y el valor declarado a unidades menores (constitución §10), envía `incoterm` vacío si es «No lo sé todavía» y `desiredShipDate` vacío si no hay fecha, y no envía `requestedBy`, `providerId` ni el país.
  - Con 201, muestra «Solicitud enviada — [código]. Te enviamos la confirmación por correo. Un asesor de Global 360 la tomará y te escribirá en la conversación de la solicitud.» con «Ver la solicitud» y «Volver al inicio». Con un error de campo, el asistente vuelve al paso de ese campo.
- **RF-06.5** — Detalle `/inquiries/[id]`.
  - Un usuario interno es redirigido a `/backoffice/inquiries/[id]`.
  - Cabecera: código, estado y «Creada el [fecha] · [ruta] · [transporte]».
  - Línea de tiempo Recibida → Asignada → En conversación → Cotizada → Aceptada con las fechas de `createdAt`, `assignedAt`, `firstContactAt`, `quotedAt` y `closedAt`; en `lost` o `cancelled`, el último paso es Cerrada o Cancelada.
  - «Cancelar solicitud» (con `inquiry:create` y estado `new`, `assigned` o `in_contact`) abre `ConfirmDialog` con «¿Por qué cancelas la solicitud? (obligatorio)» y llama a `POST /inquiries/:id/cancel {reason}`. Cancelada: «Cancelaste esta solicitud. Si necesitas mover la carga más adelante, crea una nueva.».
  - «Datos de la solicitud» (`DescriptionList`): servicio y proveedor (si vino del marketplace, con su nombre del marketplace), carga, bultos, peso, volumen (en m³), valor declarado, origen, destino, Incoterm, fecha deseada y notas; los vacíos se omiten.
  - Tarjeta del asesor: sin `advisorId`, «Aún no hay un asesor asignado. Un asesor de Global 360 tomará tu solicitud pronto.»; con `advisorId`, «Tu asesor de Global 360» (ver §11).
- **RF-06.6** — Conversación con el asesor.
  - `GET /inquiries/:id/interactions` (la API da solo las `shared` al cliente, de la más reciente a la más antigua): se muestran de la más antigua a la más reciente, con «Ver mensajes anteriores» para cargar la página siguiente.
  - Autor: `advisor` → «Tu asesor · Asesor de Global 360»; `client` con mi `userId` → «Tú»; `client` de otro usuario → «Tu empresa». Fecha y hora de `occurredAt`.
  - Las interacciones del asesor que no son mensajes se muestran como tarjetas con su canal: `phone` «Llamada con tu asesor», `email` «Correo de tu asesor», `whatsapp` «WhatsApp con tu asesor», `meeting` «Reunión con tu asesor», `video_call` «Videollamada con tu asesor», `note` «Nota de tu asesor».
  - Redactor «Escribe a tu asesor» (1 a 2000 caracteres) que envía `POST /inquiries/:id/interactions {channel: "portal_message", summary}` y recarga la conversación. En `won`, `lost` o `cancelled`, el redactor se sustituye por «La solicitud está cerrada: ya no se pueden enviar mensajes.».
  - Sin tiempo real: un enlace «Actualizar» recarga la conversación; los mensajes nuevos del asesor se avisan por correo (`inquiry_message_to_client`).
- **RF-06.7** — Cotización en el detalle (`#cotizacion`).
  - `GET /quotes?inquiryId=` con la vista del cliente (sin borradores). Estados del panel:
    - sin cotización y la solicitud en `new`, `assigned` o `in_contact`: «Tu asesor está preparando la cotización. Te avisaremos por correo cuando esté lista. Mientras tanto puedes escribirle abajo.»;
    - sin cotización visible y la solicitud en `quoted`: «Tu asesor está actualizando la cotización. Te avisaremos cuando la envíe.» (una versión revisada vuelve a `draft`, §11);
    - `sent`: código, versión, conceptos (concepto y descripción, **sin montos**), total, «Vigente hasta el [fecha y hora]» y notas del asesor; con `quote:respond` en la empresa, «Aceptar cotización» y «Rechazar»; sin él, «Solo un administrador de tu empresa puede aceptar o rechazar esta cotización.»;
    - `accepted`: «Aceptaste la versión [n]. Tu asesor te contactará para coordinar la operación.»;
    - `expired`: «Esta cotización venció. Pídele a tu asesor una versión actualizada en la conversación.»;
    - `rejected`: «Rechazaste esta versión. Tu asesor la revisará y puede enviarte una nueva.».
  - Aceptar abre `ConfirmDialog` («Vas a aceptar la versión [n] por [total]. ¿Confirmas?») y llama a `POST /quotes/:id/accept {version}` con la versión que se mostraba; rechazar pide el motivo (1 a 500, «se lo enviamos a tu asesor») y llama a `POST /quotes/:id/reject {version, reason}`. Tras responder, se recargan la solicitud y la cotización.
  - `QUOTE_VERSION_MISMATCH` recarga el panel con «Tu asesor envió una versión nueva. Revísala antes de responder.»; `QUOTE_EXPIRED`, con el estado vencido. Aceptar dos veces la misma versión no muestra error (la API es idempotente).
- **RF-06.8** — `/quotes/[id]` (enlace del email `quote_sent`).
  - Un usuario interno es redirigido a `/backoffice/quotes/[id]`.
  - Si la vista del cliente trae `inquiryId`, redirige a `/inquiries/[inquiryId]#cotizacion`; si no, muestra la cotización con el mismo panel de RF-06.7 y «Ver mis solicitudes».
  - `QUOTE_NOT_FOUND` (también un borrador tras una revisión): «Esta cotización no está disponible ahora. Puede que tu asesor la esté actualizando; te avisaremos por correo.» con «Ver mis solicitudes».

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/portal` (bloques de solicitudes y cotizaciones) | `inquiry:read` / `quote:read` en su empresa | `PortalInicio` | RF-06.2 |
| `/inquiries?status=&corridorId=&from=&to=&page=` | `inquiry:read` en su empresa | `PortalSolicitudes` | RF-06.3 |
| `/inquiries/new?serviceId=` | `inquiry:create` en su empresa | `PortalNuevaSolicitud` | RF-06.4 |
| `/inquiries/[id]` | `inquiry:read` (la API aísla por empresa) | `PortalSolicitud` | RF-06.5, RF-06.6, RF-06.7 |
| `/quotes/[id]` | `quote:read` (la API aísla por empresa) | — | RF-06.8 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /inquiries?status=&corridorId=&from=&to=&page=&pageSize=` | `backend/11 §4` (RF-11.6) | RF-06.2, RF-06.3 |
| `POST /companies/:id/inquiries` → 201 | `backend/11 §4` (RF-11.1) | RF-06.4 |
| `GET /inquiries/:id` | `backend/11 §4` | RF-06.5 |
| `POST /inquiries/:id/cancel {reason}` | `backend/11 §4` (RF-11.4) | RF-06.5 |
| `GET /inquiries/:id/interactions?page=&pageSize=`, `POST /inquiries/:id/interactions {channel, summary}` | `backend/11 §4` (RF-11.3) | RF-06.6 |
| `GET /quotes?status=&inquiryId=&companyId=&page=&pageSize=`, `GET /quotes/:id` | `backend/12 §4` (RF-12.7, RF-12.8) | RF-06.2, RF-06.7, RF-06.8 |
| `POST /quotes/:id/accept {version}`, `POST /quotes/:id/reject {version, reason}` | `backend/12 §4` (RF-12.5, RF-12.6) | RF-06.7 |
| `GET /marketplace/corridors`, `GET /marketplace/services/:id` | `backend/10 §4` | RF-06.2, RF-06.4 (vía `marketplace`) |
| `GET /currencies`, `/countries`, `/transport-types` | `backend/02 §4` | Nombres y formato de montos (vía `catalog`) |

| Código | Campo o lugar | Mensaje |
|---|---|---|
| `INQUIRY_COMPANY_NOT_ACTIVE` | — | Tu empresa aún no está validada. Podrás crear solicitudes cuando Global 360 la habilite. |
| `INQUIRY_COMPANY_NOT_CLIENT` | — | Tu empresa no está registrada como cliente. Escríbenos para habilitarla. |
| `INQUIRY_CORRIDOR_INVALID` | `corridorId` (paso 1) | Esa ruta ya no está activa. Elige otra. |
| `INQUIRY_TRANSPORT_TYPE_INVALID` | `transportTypeCode` (paso 1) | Elige un tipo de transporte de esta ruta. |
| `INQUIRY_SERVICE_NOT_AVAILABLE` | aviso del servicio | Este servicio ya no se puede solicitar en esta ruta. Quítalo o elige otra ruta. |
| `INQUIRY_CARGO_INVALID` | `cargo.*` (paso 2) | Revisa los datos de la carga: descripción hasta 1000 caracteres, al menos un bulto y valores sin negativos. |
| `INQUIRY_LOCATION_INVALID` | `origin.city` / `destination.city` (paso 3) | Escribe la ciudad (hasta 100) y la dirección (hasta 200). |
| `INQUIRY_INCOTERM_INVALID` | `incoterm` (paso 4) | Elige un Incoterm de la lista. |
| `INQUIRY_DATE_INVALID` | `desiredShipDate` (paso 4) | La fecha deseada no puede ser anterior a hoy. |
| `INQUIRY_NOTES_INVALID` | `notes` (paso 4) | Las notas admiten hasta 2000 caracteres. |
| `INQUIRY_INTERACTION_INVALID` | redactor | Escribe un mensaje de hasta 2000 caracteres. |
| `INQUIRY_REASON_REQUIRED` | `reason` | Escribe el motivo. |
| `INQUIRY_INVALID_STATUS_TRANSITION` | — | La solicitud ya cambió de estado. Recarga la página. |
| `QUOTE_VERSION_MISMATCH` | panel | Tu asesor envió una versión nueva. Revísala antes de responder. |
| `QUOTE_EXPIRED` | panel | Esta cotización venció. Pídele una nueva a tu asesor. |
| `QUOTE_INQUIRY_CLOSED` | panel | La solicitud está cerrada y ya no se puede responder la cotización. |
| `QUOTE_INVALID_STATUS_TRANSITION` | panel | Esta cotización ya no se puede responder. Recarga la página. |
| `QUOTE_REASON_REQUIRED` | `reason` | Cuéntale a tu asesor por qué la rechazas. |
| `INQUIRY_NOT_FOUND`, `COMPANY_NOT_FOUND` | — | `notFound()` |
| `QUOTE_NOT_FOUND` | — | Página de RF-06.8 |

## 6. Estados y reglas de la interfaz

| Estado de la solicitud | Etiqueta | Tono |
|---|---|---|
| `new` | Recibida | `info` |
| `assigned` | Asignada | `info` |
| `in_contact` | En conversación | `info` |
| `quoted` | Cotizada | `warning` |
| `won` | Aceptada | `success` |
| `lost` | Cerrada | `neutral` |
| `cancelled` | Cancelada | `neutral` |

| Estado efectivo de la cotización (vista del cliente) | Etiqueta | Tono |
|---|---|---|
| `sent` | Por responder | `warning` |
| `accepted` | Aceptada | `success` |
| `rejected` | Rechazada | `neutral` |
| `expired` | Vencida | `danger` |

- El cliente **no ve montos por concepto, subtotal ni comisión**: solo el total (`backend/12 RF-12.8`). El front no calcula nada (constitución §10).
- Incoterm se muestra con su código (EXW, FOB…) y una ayuda con su significado en el selector.
- La fecha deseada se muestra sin conversión de zona (`formatPlainDate`).

## 7. Componentes, datos y caché

- `features/inquiry/components/{InquiryTable,InquiryFilters,InquiryWizard,InquiryHeader,InquiryTimeline,InquiryDetails,AdvisorCard,Conversation,MessageComposer,CancelInquiryButton}.tsx`; `features/quote/components/{QuotePanel,QuoteRespondActions,PendingQuotesBlock}.tsx`.
- La página de detalle pide en paralelo la solicitud, la primera página de interacciones, su cotización, los corredores y los catálogos; la composición entre `inquiry` y `quote` la hace la página (constitución §2).
- Tras cada acción, `refresh()`. Nada se cachea en el servidor.

## 8. Accesibilidad y SEO

- El asistente anuncia el paso actual («Paso 2 de 4: Tu carga») y lleva el foco a su título al cambiar de paso.
- La conversación es una lista (`<ol>`) con el autor y la fecha de cada mensaje como texto; el redactor tiene su etiqueta y el contador de caracteres.
- El total y la vigencia se leen juntos («Total US$ 2.800,00, vigente hasta el 5 de diciembre a las 10:00»).
- Rutas privadas: `noindex`.

## 9. Criterios de aceptación

- **CA-06.1** (RF-06.1) — Los esquemas aceptan los ejemplos de `backend/11 §4` y `backend/12 §4` (solicitud con `serviceId: null`, `declaredValue: null` e interacciones `advisor` y `client`) y rechazan una cotización del cliente sin `total`. `INQUIRY_LIMITS` coincide con los límites de `backend/11 §4`.
- **CA-06.2** (RF-06.2) — Con dos cotizaciones `sent`, el inicio muestra «Cotizaciones por responder (2)» con sus enlaces a `/quotes/[id]`; sin ninguna, el texto vacío. Con la empresa `pending_validation`, «Nueva solicitud» aparece deshabilitado con su motivo. Un usuario de una empresa solo proveedora no ve el menú Solicitudes ni estos bloques.
- **CA-06.3** (RF-06.3) — `/inquiries?status=quoted&from=2026-11-01` llama a la API con `status=quoted` y `from` al inicio del 1 de noviembre en la zona del usuario, en RFC 3339; un `status` desconocido se descarta. Una solicitud `won` muestra «Aceptada» en la columna Cotización y una `new`, «—».
- **CA-06.4** (RF-06.4) — Con `serviceId` de un servicio habilitado solo en CO-CR para `sea` y `air`, y CO-CR con los cinco transportes, el paso 1 ofrece solo CO-CR (seleccionada) y los transportes `sea` y `air`. La acción con «1,25» m³, «2800,50» USD y «No lo sé todavía» envía `volumeLiters: 1250`, `declaredValue: {amount: 280050, currency: "USD"}` e `incoterm` vacío, sin `providerId` ni `requestedBy`. Con `INQUIRY_LOCATION_INVALID`, el asistente vuelve al paso 3 con el error en la ciudad. En la E2E, con la empresa activa, la solicitud se crea y muestra su código `SOL-…`; con la empresa en validación, la página muestra el aviso y no el formulario.
- **CA-06.5** (RF-06.5) — Una solicitud `in_contact` muestra la línea de tiempo con tres pasos hechos y «Cancelar solicitud»; una `quoted` no ofrece cancelar. Cancelar sin motivo no envía; con motivo, la solicitud pasa a «Cancelada» con su aviso. Un usuario interno que abre `/inquiries/[id]` es redirigido a `/backoffice/inquiries/[id]`; una solicitud de otra empresa muestra la página 404.
- **CA-06.6** (RF-06.6) — Con interacciones `[i3, i2, i1]` de la API, la conversación las muestra `i1, i2, i3`. Un mensaje del usuario actual dice «Tú», uno de un compañero «Tu empresa» y una llamada compartida del asesor «Llamada con tu asesor». Enviar un mensaje lo agrega al final; en una solicitud `won`, el redactor no aparece y se muestra el aviso de cerrada.
- **CA-06.7** (RF-06.7) — Con una cotización `sent` de versión 2 y un `client_admin`, el panel muestra los conceptos sin montos, el total formateado y los dos botones; aceptar envía `{version: 2}`. Con un `client_operator`, el panel muestra el aviso y no los botones. Con `QUOTE_VERSION_MISMATCH`, el panel se recarga con el aviso de versión nueva. Con la solicitud `quoted` y sin cotización visible, el texto «Tu asesor está actualizando la cotización». En la E2E, el cliente acepta la cotización y la solicitud queda «Aceptada».
- **CA-06.8** (RF-06.8) — `/quotes/[id]` de una cotización del cliente con `inquiryId` redirige a `/inquiries/[inquiryId]#cotizacion`; sin `inquiryId`, muestra el panel; con `QUOTE_NOT_FOUND`, la página de «no está disponible ahora»; con un usuario interno, redirige a `/backoffice/quotes/[id]`.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0072 | Feature `inquiry`: contratos, límites, `api.ts`, modelo (etiquetas, línea de tiempo, autores, orden) y mensajes | impl | F5 | RF-06.1 | G360F-0011, G360F-0013 | `src/features/inquiry/{contracts,api,model,messages}.ts` |
| G360F-0073 | Feature `quote` (vista del cliente): contratos, `api.ts`, modelo del panel y mensajes | impl | F5 | RF-06.1 | G360F-0011, G360F-0013 | `src/features/quote/{contracts,api,model,messages}.ts` |
| G360F-0074 | Menú Solicitudes, acción «Nueva solicitud» y bloques del inicio | impl | F5 | RF-06.2 | G360F-0072, G360F-0073, G360F-0062 | `src/app/(portal)/{_nav.ts,portal/page.tsx}`, `src/features/quote/components/PendingQuotesBlock.tsx`, `src/features/inquiry/components/RecentInquiries.tsx` |
| G360F-0075 | `/inquiries`: filtros por URL, tabla y paginación | impl | F5 | RF-06.3 | G360F-0072, G360F-0062 | `src/app/(portal)/inquiries/page.tsx`, `src/features/inquiry/components/{InquiryTable,InquiryFilters}.tsx` |
| G360F-0076 | `/inquiries/new`: asistente de cuatro pasos, prellenado desde el marketplace, conversiones y acción | impl | F5 | RF-06.4 | G360F-0075, G360F-0031 | `src/app/(portal)/inquiries/new/page.tsx`, `src/features/inquiry/{actions.ts,components/InquiryWizard.tsx}` |
| G360F-0077 | `/inquiries/[id]`: cabecera, línea de tiempo, datos, asesor y cancelación | impl | F5 | RF-06.5 | G360F-0075 | `src/app/(portal)/inquiries/[id]/page.tsx`, `src/features/inquiry/components/{InquiryHeader,InquiryTimeline,InquiryDetails,AdvisorCard,CancelInquiryButton}.tsx` |
| G360F-0078 | Conversación con el asesor y redactor | impl | F5 | RF-06.6 | G360F-0077 | `src/features/inquiry/components/{Conversation,MessageComposer}.tsx`, `src/features/inquiry/actions.ts` |
| G360F-0079 | Panel de la cotización con aceptar y rechazar por versión | impl | F5 | RF-06.7 | G360F-0077, G360F-0073 | `src/features/quote/{actions.ts,components/{QuotePanel,QuoteRespondActions}.tsx}` |
| G360F-0080 | `/quotes/[id]`: redirección a la solicitud, panel propio y «no disponible» | impl | F5 | RF-06.8 | G360F-0079 | `src/app/(portal)/quotes/[id]/page.tsx` |
| G360F-0081 | Tests de contratos y modelos (etiquetas, línea de tiempo, autores, orden, estados del panel, fechas de filtros, prellenado) | test | F5 | CA-06.1, CA-06.3, CA-06.6, CA-06.7 | G360F-0072, G360F-0073 | `src/features/{inquiry,quote}/*.test.ts` |
| G360F-0082 | Tests de las acciones y componentes (crear con conversiones, mensajes, cancelar, aceptar y rechazar con sus errores, redirecciones) | test | F5 | CA-06.2, CA-06.4, CA-06.5, CA-06.6, CA-06.7, CA-06.8 | G360F-0074, G360F-0076, G360F-0078, G360F-0080 | `src/features/{inquiry,quote}/**/*.test.ts(x)` |
| G360F-0083 | E2E del flujo del cliente: crear desde el marketplace, conversar y aceptar (los pasos del asesor, por API) | test | F5 | CA-06.2, CA-06.4, CA-06.5, CA-06.6, CA-06.7, CA-06.8 | G360F-0082, G360F-0040, G360F-0071 | `e2e/inquiry-quote-client.spec.ts`, `e2e/support/advisor-api.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Adjuntos en la solicitud y en la conversación: F8. Mensajería en tiempo real y WhatsApp: F12.
- PDF de la cotización: post-MVP (`backend/12 §11`).
- **Pregunta:** ¿el cliente ve la comisión o los montos por concepto? Es la política de comisión pendiente de gerencia y bloquea F5 (`backend/09`, `backend/12 §11`). Por defecto: solo el total, como define `backend/12 RF-12.8`.
- **Backend/11** — La solicitud solo trae `advisorId` y el cliente no puede consultar usuarios internos: no hay forma de mostrar el nombre del asesor. Por defecto: «Tu asesor de Global 360»; se pide un `advisor{firstName}` en la vista del cliente.
- **Backend/11** — Las interacciones no traen el nombre del autor, y `client_operator` no tiene `user:read` para resolverlo. Por defecto: «Tú», «Tu empresa» y «Tu asesor»; se pide `author{firstName}` en la respuesta.
- **Backend/12** — La vista del cliente de la cotización está pendiente de G360-0149 y la maqueta necesita `inquiryId` (para que `/quotes/[id]` lleve a la solicitud), `respondedAt` y `acceptedVersion` (para «Aceptaste la versión [n] el [fecha]») y el código de la solicitud con su ruta (bloque del inicio). Por defecto: página propia de la cotización, textos sin fecha y bloque sin datos de la solicitud.
- **Backend/12** — Tras `revise`, la cotización vuelve a `draft` y desaparece para el cliente, así que el enlace del email anterior responde 404. Por defecto: «Tu asesor está actualizando la cotización» en el detalle y la página «no está disponible ahora» en `/quotes/[id]`.
