# Spec 11 — Backoffice: bandeja, reportes y correcciones (`report`)

| | |
|---|---|
| Estado | Borrador (bloqueada por `backend/13`, en Borrador) |
| Features | `src/features/report`, `src/features/{inquiry,quote}` (correcciones) |
| Rutas | `/backoffice` (bandeja), `/backoffice/reports` |
| Backend | `backend/13` (**Borrador**) |
| Depende de | Specs 00, 01, 08, 09 y 10 |

## 1. Resumen y alcance

Es el tablero diario de Operaciones: la bandeja con lo que requiere acción hoy, los reportes de embudo, adquisición y asesores, y las correcciones manuales de estado de solicitudes y cotizaciones (con motivo y auditadas) para los casos no contemplados. Depende por completo de la spec 13 del backend, que está en *Borrador*: esta spec no se aprueba hasta que esa lo esté y fije sus respuestas.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Bandeja: empresas por validar, proveedores por revisar, solicitudes sin asignar, mis solicitudes sin contacto, mis cotizaciones por vencer, mensajes sin respuesta | `backend/13 §3` (RF-13.1) |
| Reporte de embudo con tasas en puntos básicos y mediana del primer contacto | `backend/13 §4` (RF-13.2) |
| Reportes de adquisición y de asesores | `backend/13 §3` (RF-13.3, RF-13.4) |
| Correcciones manuales con motivo y permiso propio | `backend/13 §4` (RF-13.5, RF-13.6); `backend/§10` |
| Rango de fechas de hasta 90 días | `backend/13 §4` |

## 3. Requisitos funcionales

- **RF-11.1** — Bandeja `/backoffice` (`report:read` global). Sustituye al inicio de la spec 08 para quien tiene el permiso: seis contadores, cada uno con su enlace al listado filtrado:
  - empresas por validar → `/backoffice/companies?status=pending_validation`;
  - proveedores por revisar → `/backoffice/providers?status=in_review`;
  - solicitudes sin asignar → `/backoffice/inquiries?tab=unassigned`;
  - mis solicitudes asignadas sin contacto → `/backoffice/inquiries?tab=mine&status=assigned`;
  - mis cotizaciones que vencen en 3 días → `/backoffice/quotes?tab=mine&status=sent`;
  - mensajes de clientes sin respuesta.

  Un contador en 0 se muestra atenuado con «Todo al día».
- **RF-11.2** — Embudo `/backoffice/reports?tab=funnel&from=&to=&corridorId=`.
  - Rango por defecto: los últimos 30 días; más de 90 días o `from` posterior a `to` no se envía y muestra el error en el filtro.
  - Indicadores: empresas registradas y validadas, solicitudes creadas (total y por origen), cotizadas, cotizaciones enviadas, aceptadas, rechazadas y vencidas, clientes consolidados, tasas solicitud → cotización y cotización → aceptación (`formatBps`) y mediana del primer contacto («2 h 15 min», o «—» si es `null`).
  - Barras de embudo hechas con CSS (sin librería de gráficos), con el valor en texto.
- **RF-11.3** — Adquisición (`tab=acquisition`): tabla por fuente con registros, validadas y consolidados; «(sin fuente)» al final.
- **RF-11.4** — Asesores (`tab=advisors`): tabla por asesor (correo) con solicitudes abiertas por estado, cotizaciones enviadas pendientes, aceptadas en el rango y mediana del primer contacto.
- **RF-11.5** — Corrección del estado de una solicitud (`inquiry:override`). En `/backoffice/inquiries/[id]`, «Corregir estado» abre un `Dialog` con el estado destino (cualquiera distinto del actual) y el motivo obligatorio (1 a 500), con el aviso «Es una corrección manual: queda auditada y no envía avisos.», y llama a `POST /inquiries/:id/override-status {status, reason}`.
- **RF-11.6** — Correcciones de una cotización (`quote:override`). En `/backoffice/quotes/[id]`:
  - «Extender vigencia» (`sent` o `expired`): nueva fecha futura y motivo, con `POST /quotes/:id/extend-validity {validUntil, reason}`;
  - «Forzar estado» (`sent`): `rejected` o `expired` y motivo, con `POST /quotes/:id/override-status {status, reason}`.

  La aceptación nunca se fuerza: no hay opción para ello.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/backoffice` | Usuario interno; la bandeja con `report:read` global | — (sin maqueta) | RF-11.1 |
| `/backoffice/reports?tab=funnel\|acquisition\|advisors&from=&to=&corridorId=` | `report:read` global | — | RF-11.2, RF-11.3, RF-11.4 |
| Diálogos de corrección en `/backoffice/inquiries/[id]` y `/backoffice/quotes/[id]` | `inquiry:override` / `quote:override` global | — | RF-11.5, RF-11.6 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /backoffice/inbox` | `backend/13 §4` (respuesta sin definir) | RF-11.1 |
| `GET /reports/funnel?from=&to=&corridorId=` | `backend/13 §4` | RF-11.2 |
| `GET /reports/acquisition?from=&to=` | `backend/13 §4` (respuesta parcial) | RF-11.3 |
| `GET /reports/advisors?from=&to=` | `backend/13 §4` (respuesta sin definir) | RF-11.4 |
| `POST /inquiries/:id/override-status {status, reason}` | `backend/13 §4` (RF-13.5) | RF-11.5 |
| `POST /quotes/:id/extend-validity {validUntil, reason}`, `POST /quotes/:id/override-status {status, reason}` | `backend/13 §4` (RF-13.6) | RF-11.6 |

| Código | Mensaje |
|---|---|
| `INVALID_QUERY` | El rango debe ser de 90 días como máximo y la fecha inicial anterior a la final. |
| `INQUIRY_OVERRIDE_INVALID` / `QUOTE_OVERRIDE_INVALID` | Ese estado o esa fecha no se permiten en una corrección. |
| `INQUIRY_REASON_REQUIRED` / `QUOTE_REASON_REQUIRED` | Escribe el motivo de la corrección. |
| `QUOTE_INVALID_STATUS_TRANSITION` | La vigencia solo se extiende en cotizaciones enviadas o vencidas. |

## 6. Estados y reglas de la interfaz

- Las tasas llegan en puntos básicos enteros y se muestran con `formatBps`; si el denominador es 0, la API da 0 y se muestra «0,00 %».
- Las fechas del filtro son días locales: `from` al inicio del día y `to` al final, en RFC 3339.
- Las correcciones solo aparecen con su permiso y en los estados que admite `backend/13`.

## 7. Componentes, datos y caché

- `features/report/{contracts,api,model,messages}.ts` y `components/{InboxCounters,FunnelReport,AcquisitionReport,AdvisorsReport,DateRangeFilter}.tsx`; `features/inquiry/components/OverrideInquiryStatus.tsx`; `features/quote/components/{ExtendValidity,OverrideQuoteStatus}.tsx`.
- Sin caché del servidor (datos internos por request).

## 8. Accesibilidad y SEO

- Cada barra del embudo tiene su valor como texto y una tabla equivalente para lectores de pantalla.
- `noindex`.

## 9. Criterios de aceptación

- **CA-11.1** (RF-11.1) — Con la bandeja de ejemplo de `backend/13`, cada contador enlaza a su listado filtrado y uno en 0 muestra «Todo al día»; un usuario interno sin `report:read` ve el inicio de la spec 08.
- **CA-11.2** (RF-11.2) — Un rango de 91 días no llama a la API y muestra el error del filtro; sin rango, se piden los últimos 30 días. Con `inquiryToQuoteBps: 4250` se muestra «42,50 %», y con `medianFirstContactMinutes: 135`, «2 h 15 min».
- **CA-11.3** (RF-11.3) — La tabla de adquisición muestra «(sin fuente)» al final.
- **CA-11.4** (RF-11.4) — La tabla de asesores muestra una fila por asesor con su correo.
- **CA-11.5** (RF-11.5) — El diálogo no ofrece el estado actual como destino y no envía sin motivo; en la E2E, corregir una solicitud `lost` a `in_contact` la deja «En conversación» y su historial muestra la corrección.
- **CA-11.6** (RF-11.6) — «Extender vigencia» no aparece en una cotización `accepted`; una fecha pasada muestra el mensaje de `QUOTE_OVERRIDE_INVALID`; «Forzar estado» solo ofrece Rechazada y Vencida.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0125 | Feature `report`: contratos, `api.ts`, modelo (rango, tasas, minutos) y mensajes | impl | F6 | RF-11.1, RF-11.2, RF-11.3, RF-11.4 | G360F-0093, G360F-0013 | `src/features/report/{contracts,api,model,messages}.ts` |
| G360F-0126 | Bandeja en `/backoffice` con contadores y enlaces | impl | F6 | RF-11.1 | G360F-0125 | `src/app/backoffice/page.tsx`, `src/features/report/components/InboxCounters.tsx` |
| G360F-0127 | `/backoffice/reports` con las pestañas de embudo, adquisición y asesores | impl | F6 | RF-11.2, RF-11.3, RF-11.4 | G360F-0125 | `src/app/backoffice/reports/page.tsx`, `src/features/report/components/{FunnelReport,AcquisitionReport,AdvisorsReport,DateRangeFilter}.tsx` |
| G360F-0128 | Correcciones manuales de solicitudes y cotizaciones | impl | F6 | RF-11.5, RF-11.6 | G360F-0120 | `src/features/inquiry/components/OverrideInquiryStatus.tsx`, `src/features/quote/components/{ExtendValidity,OverrideQuoteStatus}.tsx`, `src/features/{inquiry,quote}/actions.ts` |
| G360F-0129 | Tests y E2E de la bandeja, los reportes y las correcciones | test | F6 | CA-11.1, CA-11.2, CA-11.3, CA-11.4, CA-11.5, CA-11.6 | G360F-0126, G360F-0127, G360F-0128 | `src/features/report/**/*.test.ts(x)`, `e2e/backoffice-reports.spec.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Indicadores semanales para gerencia, exportaciones y reportes financieros: F11 (`backend/13 §11`).
- **Backend/13** — La spec está en *Borrador*: no define el JSON de `GET /backoffice/inbox` ni el de `GET /reports/advisors`, y el de `GET /reports/acquisition` es parcial. **Bloquea esta spec.** Por defecto: los contratos de §5 se escriben cuando `backend/13` se apruebe.
- **Backend/13** — No define el formato de `validUntil` en `extend-validity`. Por defecto: RFC 3339 en UTC, como el resto de la API.
