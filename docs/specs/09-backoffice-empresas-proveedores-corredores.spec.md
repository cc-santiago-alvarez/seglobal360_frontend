# Spec 09 — Backoffice: empresas, proveedores y corredores (`company`, `client`, `provider`, `service`, `corridor`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/{company,client,provider,service,corridor}` |
| Rutas | `/backoffice/companies`, `/backoffice/companies/new`, `/backoffice/companies/[id]`, `/backoffice/clients`, `/backoffice/providers`, `/backoffice/providers/[id]`, `/backoffice/corridors`, `/backoffice/corridors/new`, `/backoffice/corridors/[id]` |
| Backend | `backend/04`, `backend/07`, `backend/08` y `backend/09` (Implementadas) |
| Depende de | Specs 00, 01, 05, 07 y 08 |

## 1. Resumen y alcance

Es la parte del backoffice con la que Global 360 da de alta y valida a las empresas, revisa y publica a los proveedores y modera sus servicios, sigue a sus clientes y configura los corredores con sus servicios habilitados y sus reglas de comisión. Se reparte en tres fases:
- **F2:** empresas (listado, detalle, alta y edición).
- **F3:** validación y estados de las empresas, clientes y proveedores.
- **F4:** corredores, servicios habilitados y comisiones.

`/backoffice/companies/[id]` es el destino del email `company_registered` (constitución, *Rutas que fija el backend*).

## 2. Origen

| Requisito | Fuente |
|---|---|
| Criterios de salida de F2, F3 y F4 | `backend/CLAUDE.md`, *Alcance y fases* |
| Empresas: campos, edición por Global 360, razón social con motivo, estados con motivo, aviso al validar o rechazar | `backend/04 §4` y §5 (RF-04.2 a RF-04.4) |
| Enlace del email `company_registered` | `backend/07 §5`, `backend/06` |
| Clientes: etapa, consolidación, adquisición | `backend/07 §4` (RF-07.10) |
| Proveedores: revisión, aprobación, rechazo con notas, publicación, suspensión; moderación de servicios con motivo obligatorio para el personal | `backend/08 §4` y §5 (RF-08.3, RF-08.7) |
| Corredores: campos, activación con regla vigente (`CORRIDOR_NOT_READY`), servicios habilitados y elegibilidad, reglas versionadas, preview | `backend/09 §4` y §5 (RF-09.1 a RF-09.7) |
| La comisión solo la ve el personal con `commission:read` | `backend/09`, `backend/12 RF-12.8` |

## 3. Requisitos funcionales

- **RF-09.1** — Empresas `/backoffice/companies` (`company:read` global).
  - Pestañas rápidas por URL: «Por validar» (`status=pending_validation`), Todas, Activas, Suspendidas, Inactivas.
  - Filtros de tipo, país y búsqueda por prefijo (`q`: razón social, nombre comercial o documento).
  - Tabla: razón social (y nombre comercial), documento, país, tipo, estado y fecha de registro, de la más reciente a la más antigua; enlace al detalle.
- **RF-09.2** — Detalle `/backoffice/companies/[id]` (`company:read`).
  - Datos (razón social, nombre comercial, documento, país, tipo, moneda, contacto), estado con su motivo, validación (fecha y quién), usuarios de la empresa (`GET /users?companyId=`, con enlace a `/backoffice/users/[id]`), perfil de cliente si es `client` o `both` (RF-09.5), enlace al proveedor si es `provider` o `both` y `AuditTrail` de la empresa (spec 08).
  - Con `company:manage`: edición de nombre comercial, moneda y contacto (`PATCH /companies/:id`) y «Corregir razón social» con motivo obligatorio (`PATCH /companies/:id/legal-name {legalName, reason}`).
- **RF-09.3** — Alta `/backoffice/companies/new` (`company:manage`). Formulario con los campos de empresa de `backend/04 §4` (como el bloque «Datos de la empresa» del registro) que llama a `POST /companies` y lleva al detalle. La empresa nace `pending_validation` y sin usuarios: el detalle ofrece invitar a su administrador con el formulario de la spec 05.
- **RF-09.4** — Validación y estados (`company:validate`). En el detalle, según el estado:
  - `pending_validation` → «Validar» (confirmación: «Se avisará por correo a los administradores de la empresa.») y «Rechazar» (motivo obligatorio: «Se envía por correo a la empresa.»);
  - `active` → «Suspender» y «Desactivar»;
  - `suspended` → «Reactivar» y «Desactivar»;
  - `inactive` → «Reactivar».

  Todas salvo validar piden el motivo (1 a 500) en `ConfirmDialog`. Tras la acción, el estado y el historial se recargan.
- **RF-09.5** — Clientes `/backoffice/clients` (`client:read`).
  - Listado de `GET /clients` con filtros de etapa (`registered`, `consolidated`) y fuente (`source`): empresa (nombre y enlace a su detalle), etapa, fecha de consolidación, fuente, medio y campaña de adquisición, y fecha de registro.
  - En el detalle de la empresa, el perfil comercial (`GET /clients/:id`) en solo lectura, o editable con `client:manage` (mismo formulario de la spec 05).
- **RF-09.6** — Proveedores `/backoffice/providers` y `/backoffice/providers/[id]` (`provider:read`).
  - Listado con pestañas «Por revisar» (`in_review`), Aprobados, Publicados, Todos, filtros de categoría y país y búsqueda (`q`), y columnas nombre visible, empresa, categorías, cobertura, estado y última actualización.
  - Detalle con el perfil completo (también lo interno: sitio web, contacto operativo, notas de revisión y motivo del estado), la empresa (enlace) y «Ver en el marketplace» si está publicado.
  - Acciones según el estado:
    - `in_review` → «Aprobar» y «Rechazar» (motivo obligatorio, que llega al proveedor como notas de revisión), con `provider:validate`;
    - `approved` o `unpublished` → «Publicar», con `provider:publish` (`PROVIDER_COMPANY_NOT_ACTIVE`: «La empresa no está activa: valídala primero.»);
    - `published` → «Despublicar» (con motivo), con `provider:publish`;
    - `approved`, `published` o `unpublished` → «Suspender» (con motivo), con `provider:validate`;
    - `suspended` → «Restablecer», con `provider:validate` (vuelve a `approved` y hay que publicar de nuevo).
  - Con `provider:manage`, edición del perfil con el `ProviderForm` de la spec 07.
  - Servicios del proveedor (`GET /providers/:id/services`) con moderación (`service:manage`): «Despublicar» (motivo **obligatorio** para el personal) y «Archivar» (confirmación). Tras publicar, despublicar o moderar, `updateTag('marketplace')`.
- **RF-09.7** — Corredores `/backoffice/corridors`, `/new` y `/[id]` (`corridor:read`).
  - Listado (`GET /corridors?status=`): código, nombre, origen → destino, monedas, tipos de transporte, vigencia de la cotización y estado.
  - Alta con `corridor:manage`: código (`^[A-Z]{2}-[A-Z]{2}$`, se escribe en mayúsculas), nombre, país de origen y de destino (distintos, inmutables después), monedas y tipos de transporte (casillas desde los catálogos) y vigencia en días (1 a 90, por defecto 15).
  - Detalle: edición de nombre, monedas, transportes y vigencia (`PATCH`; las listas se envían enteras), «Activar» (`CORRIDOR_NOT_READY`: «Crea una regla de comisión vigente antes de activar el corredor.») y «Desactivar» («El corredor desaparece del marketplace y no admite solicitudes nuevas.»). Tras activar o desactivar, `updateTag('marketplace')`.
- **RF-09.8** — Servicios habilitados (en el detalle del corredor).
  - Tabla paginada de `GET /corridors/:id/services` con filtro habilitados/deshabilitados: servicio y proveedor (nombres resueltos por fila, §11), estado, quién y cuándo lo habilitó y fecha de deshabilitación.
  - Con `corridor:manage`: «Habilitar un servicio» (elegir un proveedor publicado y uno de sus servicios publicados; la API decide si es elegible: `CORRIDOR_SERVICE_NOT_ELIGIBLE` → «El servicio no cubre el origen y el destino de este corredor o no comparte ningún tipo de transporte con él.») y «Deshabilitar» por fila. Tras cada cambio, `updateTag('marketplace')`.
- **RF-09.9** — Reglas de comisión (en el detalle del corredor, `commission:read`).
  - Versiones (`GET /corridors/:id/commission-rules`), de la más reciente a la más antigua: versión, tipo, tasa (`formatBps`) o montos fijos, mínimos, vigente desde, notas, quién y cuándo; la vigente ahora (`GET …/active`) lleva la insignia «Vigente» y una futura, «Programada».
  - Con `commission:manage`, «Nueva versión»:
    - tipo `percentage` (tasa en % con hasta 2 decimales, convertida a puntos básicos sin `float`: «12,5» → 1250; mínimos opcionales, uno por moneda del corredor) o `fixed` (un monto obligatorio por **cada** moneda del corredor);
    - vigente desde (fecha y hora local convertida a RFC 3339; vacío = ahora) y notas.

    Aviso fijo: «Las reglas no se editan: un cambio crea una versión nueva y cada cotización guarda la versión que usó.»
  - **Simulador** (`POST …/commission-rules/preview`): subtotal y moneda → versión aplicada, comisión y total, con `formatMoney`.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/backoffice/companies?status=&type=&countryId=&q=&page=` | `company:read` global | — (sin maqueta) | RF-09.1 |
| `/backoffice/companies/[id]` | `company:read` global (enlace de `company_registered`) | — | RF-09.2, RF-09.4, RF-09.5 |
| `/backoffice/companies/new` | `company:manage` global | — | RF-09.3 |
| `/backoffice/clients?stage=&source=&page=` | `client:read` global | — | RF-09.5 |
| `/backoffice/providers?status=&categoryId=&countryId=&q=&page=`, `/backoffice/providers/[id]` | `provider:read` global | — | RF-09.6 |
| `/backoffice/corridors`, `/backoffice/corridors/new`, `/backoffice/corridors/[id]` | `corridor:read` global (`/new`: `corridor:manage`) | — | RF-09.7, RF-09.8, RF-09.9 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /companies?status=&type=&countryId=&q=&page=&pageSize=`, `GET /companies/:id` | `backend/04 §4` | RF-09.1, RF-09.2 |
| `POST /companies`, `PATCH /companies/:id`, `PATCH /companies/:id/legal-name {legalName, reason}` | `backend/04 §4` | RF-09.2, RF-09.3 |
| `POST /companies/:id/validate`, `/reject {reason}`, `/suspend {reason}`, `/reactivate {reason}`, `/deactivate {reason}` | `backend/04 §4` | RF-09.4 |
| `GET /clients?stage=&source=&page=&pageSize=`, `GET/PATCH /clients/:id` | `backend/07 §4` | RF-09.5 |
| `GET /providers?status=&categoryId=&countryId=&q=&page=&pageSize=`, `GET/PATCH /providers/:id` | `backend/08 §4` | RF-09.6 |
| `POST /providers/:id/approve`, `/reject {reason}`, `/publish`, `/unpublish {reason}`, `/suspend {reason}`, `/reinstate` | `backend/08 §4` | RF-09.6 |
| `GET /providers/:id/services`, `GET /services?providerId=&status=`, `GET /services/:id`, `POST /services/:id/unpublish {reason}`, `/archive` | `backend/08 §4` | RF-09.6, RF-09.8 |
| `GET /corridors?status=`, `GET/POST/PATCH /corridors[/:id]`, `POST /corridors/:id/activate`, `/deactivate` | `backend/09 §4` | RF-09.7 |
| `GET /corridors/:id/services?status=`, `POST /corridors/:id/services {serviceId}`, `POST /corridors/:id/services/:serviceId/disable` | `backend/09 §4` | RF-09.8 |
| `GET /corridors/:id/commission-rules`, `GET …/active?at=`, `POST …/commission-rules`, `POST …/commission-rules/preview {subtotal}` | `backend/09 §4` | RF-09.9 |

| Código | Mensaje |
|---|---|
| `COMPANY_REASON_REQUIRED` / `PROVIDER_REASON_REQUIRED` / `SERVICE_REASON_REQUIRED` | Escribe el motivo (hasta 500 caracteres). |
| `COMPANY_INVALID_STATUS_TRANSITION` / `PROVIDER_INVALID_STATUS_TRANSITION` / `CORRIDOR_INVALID_STATUS_TRANSITION` | El estado ya cambió. Recarga la página. |
| `COMPANY_ALREADY_EXISTS` | Ya hay una empresa con ese tipo y número de documento en ese país. |
| `PROVIDER_COMPANY_NOT_ACTIVE` | La empresa no está activa: valídala primero. |
| `PROVIDER_PROFILE_INCOMPLETE` | Al perfil le faltan datos obligatorios. |
| `CORRIDOR_CODE_INVALID` | El código tiene la forma `CO-CR`: dos letras, guion y dos letras, en mayúsculas. |
| `CORRIDOR_COUNTRIES_INVALID` | Elige dos países activos y distintos. |
| `CORRIDOR_CURRENCY_INVALID`, `CORRIDOR_TRANSPORT_TYPE_INVALID`, `CORRIDOR_QUOTE_VALIDITY_INVALID`, `CORRIDOR_NAME_REQUIRED` | Revisa el campo (texto por código en `corridor/messages.ts`). |
| `CORRIDOR_ALREADY_EXISTS` | Ya existe un corredor con ese código. |
| `CORRIDOR_NOT_READY` | Crea una regla de comisión vigente antes de activar el corredor. |
| `CORRIDOR_SERVICE_NOT_ELIGIBLE` | El servicio no cubre el origen y el destino del corredor o no comparte un tipo de transporte con él. |
| `CORRIDOR_SERVICE_ALREADY_ENABLED` / `CORRIDOR_SERVICE_ALREADY_DISABLED` | El servicio ya estaba habilitado / deshabilitado. |
| `COMMISSION_RULE_INVALID` | Revisa la regla: la tasa va de 0 % a 100 %, y una regla fija lleva un monto por cada moneda del corredor. |
| `COMMISSION_RULE_EFFECTIVE_FROM_INVALID` | La fecha de vigencia no puede ser anterior a ahora ni a la de la versión anterior. |
| `COMMISSION_RULE_CURRENCY_NOT_COVERED` | La regla vigente no cubre todas las monedas del corredor: crea una versión nueva. |
| `COMMISSION_RULE_ALREADY_EXISTS` | Otra persona creó una versión al mismo tiempo. Inténtalo de nuevo. |
| `COMMISSION_RULE_NOT_FOUND` | El corredor aún no tiene una regla vigente. |
| `COMMISSION_RULE_SUBTOTAL_INVALID`, `MONEY_AMOUNT_OVERFLOW` | Revisa el subtotal del simulador. |

## 6. Estados y reglas de la interfaz

| Concepto | Valores → etiqueta (tono) |
|---|---|
| Empresa | Los de la spec 05 |
| Etapa del cliente | `registered` Registrado (`info`) · `consolidated` Consolidado (`success`) |
| Proveedor y servicio | Los de la spec 07 |
| Corredor | `draft` Borrador (`neutral`) · `active` Activo (`success`) · `inactive` Inactivo (`neutral`) |
| Servicio en el corredor | `enabled` Habilitado (`success`) · `disabled` Deshabilitado (`neutral`) |
| Regla de comisión | Vigente (`success`) · Programada (`info`) · Anterior (`neutral`) |

- Qué acciones aparecen en cada estado sale del `model.ts` de la feature, a partir de las transiciones de `backend/04 §5`, `backend/08 §5` y `backend/09 §5`; si la API responde otra cosa, manda la API.
- La comisión (tasa, mínimos, montos, simulador) solo se muestra con `commission:read`.
- Un monto se escribe con `parseMoneyInput` y los decimales de su moneda (constitución §10).

## 7. Componentes, datos y caché

- `features/company/components/{CompanyTable,CompanyDetail,CompanyAdminForm,CompanyStatusActions,LegalNameForm}.tsx`, `features/client/components/ClientTable.tsx`, `features/provider/components/{ProviderTable,ProviderReview,ProviderStatusActions}.tsx`, `features/service/components/ServiceModeration.tsx` y `features/corridor/{contracts,api,model,messages,actions}.ts` con `components/{CorridorTable,CorridorForm,CorridorStatusActions,CorridorServices,EnableServiceForm,CommissionRules,CommissionRuleForm,CommissionPreview}.tsx`.
- `corridor/model.ts`: `percentToBps("12,5")` → 1250 sin `float`, la etiqueta de la regla (vigente, programada o anterior) y las monedas que exige una regla fija.
- Los nombres por fila (servicio y proveedor del corredor, empresa del cliente) se resuelven en paralelo por página con `React.cache`.

## 8. Accesibilidad y SEO

- Las acciones de estado se agrupan en una barra con el estado actual anunciado («Estado: En revisión»).
- El simulador anuncia su resultado en una región `aria-live`.
- Todo el backoffice lleva `noindex`.

## 9. Criterios de aceptación

- **CA-09.1** (RF-09.1) — `/backoffice/companies?status=pending_validation&q=acm` llama a `GET /companies` con esos filtros; un `status` desconocido se descarta. La pestaña «Por validar» queda marcada como actual.
- **CA-09.2** (RF-09.2) — El detalle de una empresa `both` muestra su perfil de cliente y el enlace al proveedor; «Corregir razón social» sin motivo no envía. Un usuario interno sin `company:manage` ve el detalle sin formularios de edición. El enlace del email `company_registered` (`/backoffice/companies/<id>`) abre el detalle de esa empresa.
- **CA-09.3** (RF-09.3) — El alta envía los campos de empresa de `backend/04` sin `status` ni fechas, y con 201 lleva al detalle, que ofrece invitar a su administrador.
- **CA-09.4** (RF-09.4) — Una empresa `pending_validation` ofrece Validar y Rechazar; una `active`, Suspender y Desactivar; una `inactive`, solo Reactivar. Rechazar sin motivo no envía. En la E2E, una empresa registrada con el flujo de la spec 04 se valida desde el backoffice, su historial muestra la acción y su administrador ya puede abrir `/inquiries/new` sin el aviso de validación.
- **CA-09.5** (RF-09.5) — `/backoffice/clients?stage=consolidated` lista solo los consolidados con el nombre de su empresa; una empresa `provider` no muestra la sección de perfil de cliente.
- **CA-09.6** (RF-09.6) — Un proveedor `in_review` ofrece Aprobar y Rechazar; uno `approved`, Publicar y Suspender; uno `suspended`, Restablecer. Publicar con `PROVIDER_COMPANY_NOT_ACTIVE` muestra su mensaje. Despublicar un servicio sin motivo no envía. En la E2E, un proveedor enviado a revisión (spec 07) se aprueba y se publica desde el backoffice y aparece en `/marketplace`.
- **CA-09.7** (RF-09.7) — El alta con código `co-cr` lo envía como `CO-CR`; la edición no envía `code` ni los países. Activar sin regla vigente muestra el mensaje de `CORRIDOR_NOT_READY`.
- **CA-09.8** (RF-09.8) — La tabla de servicios habilitados muestra el nombre del servicio y del proveedor de cada fila. Habilitar un servicio no elegible muestra el mensaje de `CORRIDOR_SERVICE_NOT_ELIGIBLE`; deshabilitar uno lo deja «Deshabilitado».
- **CA-09.9** (RF-09.9) — `percentToBps("12,5")` da 1250, `"12,345"` es error y `"100"` da 10000. Una regla `fixed` en un corredor con USD, COP y CRC exige los tres montos antes de enviar. El simulador con 2.500,00 USD sobre una regla del 12 % muestra comisión US$ 300,00 y total US$ 2.800,00 (los que da la API). Sin `commission:read`, el detalle del corredor no muestra la sección. En la E2E, el superadmin crea la regla de CO-CR, activa el corredor y habilita un servicio, y la ruta aparece en la landing y en el filtro del marketplace.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0104 | Empresas: listado con pestañas y filtros, y detalle con usuarios e historial | impl | F2 | RF-09.1, RF-09.2 | G360F-0093, G360F-0098 | `src/app/backoffice/companies/{page.tsx,[id]/page.tsx}`, `src/features/company/components/{CompanyTable,CompanyDetail}.tsx` |
| G360F-0105 | Empresas: edición, corrección de la razón social con motivo y alta | impl | F2 | RF-09.2, RF-09.3 | G360F-0104 | `src/app/backoffice/companies/new/page.tsx`, `src/features/company/{actions.ts,components/{CompanyAdminForm,LegalNameForm}.tsx}` |
| G360F-0106 | Tests y E2E del listado, el detalle, la edición y el alta de empresas | test | F2 | CA-09.1, CA-09.2, CA-09.3 | G360F-0105, G360F-0100 | `src/features/company/**/*.test.ts(x)`, `e2e/backoffice-companies.spec.ts` |
| G360F-0107 | Validación y estados de la empresa con motivo y confirmación | impl | F3 | RF-09.4 | G360F-0105 | `src/features/company/{actions,model}.ts`, `src/features/company/components/CompanyStatusActions.tsx` |
| G360F-0108 | Clientes: listado y perfil comercial en el detalle de la empresa | impl | F3 | RF-09.5 | G360F-0105, G360F-0066 | `src/app/backoffice/clients/page.tsx`, `src/features/client/{api.ts,components/ClientTable.tsx}` |
| G360F-0109 | Proveedores: listado, detalle, acciones de revisión y publicación, edición y moderación de servicios | impl | F3 | RF-09.6 | G360F-0104, G360F-0089 | `src/app/backoffice/providers/{page.tsx,[id]/page.tsx}`, `src/features/provider/{actions,model}.ts`, `src/features/provider/components/{ProviderTable,ProviderReview,ProviderStatusActions}.tsx`, `src/features/service/components/ServiceModeration.tsx` |
| G360F-0110 | Tests y E2E de validación de empresas, clientes y revisión de proveedores | test | F3 | CA-09.2, CA-09.4, CA-09.5, CA-09.6 | G360F-0107, G360F-0108, G360F-0109, G360F-0060, G360F-0092 | `src/features/{company,client,provider,service}/**/*.test.ts(x)`, `e2e/backoffice-validation.spec.ts` |
| G360F-0111 | Feature `corridor` y corredores: listado, alta, detalle, edición y estado | impl | F4 | RF-09.7 | G360F-0093, G360F-0012 | `src/features/corridor/*`, `src/app/backoffice/corridors/{page.tsx,new/page.tsx,[id]/page.tsx}` |
| G360F-0112 | Servicios habilitados del corredor: tabla con nombres, habilitar y deshabilitar | impl | F4 | RF-09.8 | G360F-0111, G360F-0109 | `src/features/corridor/components/{CorridorServices,EnableServiceForm}.tsx`, `src/features/corridor/actions.ts` |
| G360F-0113 | Reglas de comisión: versiones, nueva versión porcentual o fija, simulador y `percentToBps` | impl | F4 | RF-09.9 | G360F-0111, G360F-0013 | `src/features/corridor/components/{CommissionRules,CommissionRuleForm,CommissionPreview}.tsx`, `src/features/corridor/{model,actions}.ts` |
| G360F-0114 | Tests y E2E de corredores, servicios habilitados y comisiones, hasta ver la ruta en la landing y el marketplace | test | F4 | CA-09.7, CA-09.8, CA-09.9 | G360F-0112, G360F-0113, G360F-0050 | `src/features/corridor/**/*.test.ts(x)`, `e2e/backoffice-corridors.spec.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Validar el documento de la empresa contra RUES o Hacienda: manual en el MVP (`backend/04 §11`).
- Tarifas y cálculo automático por corredor: F12. Documentos requeridos e hitos por corredor: F8 y F7.
- **Pregunta:** política de comisión (modelo, monedas y quién la ve). La define gerencia y bloquea la activación del corredor en F4 (`backend/09 §11`). Por defecto: la pantalla admite los dos tipos de regla de `backend/09`.
- **Backend/09** — Las filas de `GET /corridors/:id/services` no traen el nombre del servicio ni el del proveedor, y no hay una lectura de servicios elegibles para un corredor. Por defecto: los nombres se resuelven con `GET /services/:id` por fila y el alta se hace eligiendo proveedor y servicio; se piden los nombres en la fila y un filtro `eligibleForCorridorId` en `GET /services`.
- **Backend/07** — `GET /clients` no trae el nombre de la empresa. Por defecto: se resuelve con `GET /companies/:id` por fila; se pide incluir `companyName` en la fila del cliente.
