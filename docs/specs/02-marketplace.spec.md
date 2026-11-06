# Spec 02 — Marketplace público (`marketplace`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/marketplace` |
| Rutas | `/marketplace`, `/marketplace/services/[id]`, `/marketplace/providers/[id]` |
| Backend | `backend/10` (Aprobada; código implementado), `backend/02` y `backend/08` (catálogos, Implementadas) |
| Depende de | Specs 00 y 01 |

## 1. Resumen y alcance

El marketplace público lista los proveedores publicados y sus servicios, con búsqueda y filtros, y muestra el detalle de cada servicio y el perfil de cada proveedor. No hay precios ni datos de contacto del proveedor: todo contacto y toda cotización pasan por un asesor de Global 360. Desde el detalle de un servicio se inicia la solicitud de cotización (spec 06).

Los bloques de la landing que leen el marketplace (rutas activas, proveedores aprobados, buscador) son de la spec 03 y usan las lecturas de esta feature.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Listado con pestañas Servicios/Proveedores, filtros, conteo, «Sin precios publicados», paginación | Artboard `MvpMarketplace` y nota `nota-marketplace` |
| Detalle del servicio, botón según `canRequestQuote`, «Aún no se puede solicitar en línea», prellenado | Artboard `MvpServicio` y nota `nota-servicio` |
| Perfil del proveedor sin web ni contacto, 404 genérico | Artboard `MvpProveedor` y nota `nota-proveedor` |
| Rutas, parámetros, límites (`pageSize` ≤ 50, `q` ≤ 100), proyecciones públicas, visibilidad, corredor inactivo → lista vacía | `backend/10 §4` (RF-10.1 a RF-10.7) |
| Nombres de categorías, países y transportes desde los catálogos | `backend/10 §4`, `backend/02`, `backend/08` |
| Rate limit compartido por las seis rutas del marketplace | `backend/00` (RF-00.11) y `backend/10 §4` |

## 3. Requisitos funcionales

- **RF-02.1** — Lecturas del marketplace.
  - `api.ts` expone `listCorridors()`, `listServices(filters, page)`, `getService(id)`, `listProviders(filters, page)`, `getProvider(id)` y `listProviderServices(id, filters, page)` sobre `backend/10 §4`, todas con `apiPublic`, `'use cache'`, `cacheLife` = `PUBLIC_REVALIDATE` y `cacheTag('marketplace')` (más `marketplace:service:<id>` o `marketplace:provider:<id>` en los detalles).
  - `contracts.ts` replica las proyecciones públicas exactas de `backend/10 §4`: corredor (`_id, code, name, originCountryId, destinationCountryId, transportTypeCodes, currencyCodes`), tarjeta y perfil de proveedor (con `logoUrl` y `yearsInOperation` que pueden ser `null`, `servicesCount`, `publishedAt`), servicio en lista y detalle (con `estimatedTransitDays` nulo, `provider{…}`, `canRequestQuote` e `inquiryPrefill{serviceId, providerId, corridorIds, transportTypeCodes}`).
  - `MARKETPLACE_SERVICE_NOT_FOUND` y `MARKETPLACE_PROVIDER_NOT_FOUND` se traducen en `notFound()`; `RATE_LIMITED`, `NETWORK_ERROR` y 5xx en el estado de error de RF-02.6.
- **RF-02.2** — Listado `/marketplace`.
  - Pestañas por URL: Servicios (por defecto) y Proveedores (`?tab=providers`).
  - Buscador `q` y filtros en un formulario `GET` que funciona sin JS: categoría (`categoryId`), ruta (`corridorId`, con las rutas de `listCorridors()`), tipo de transporte (`transportType`); en servicios, además origen (`originCountryId`) y destino (`destinationCountryId`); en proveedores, país de cobertura (`countryId`). «Limpiar» vuelve a `/marketplace` conservando la pestaña.
  - Los `searchParams` se validan con zod antes de llamar a la API: un ID que no es UUID o un `transportType` fuera de `^[a-z_]{2,30}$` se descarta, `q` se recorta a 100 caracteres y `page` inválido es 1. `pageSize` fijo de 12.
  - Encabezado de resultados «[n] servicios» o «[n] proveedores» y el aviso «Sin precios publicados: el valor sale de tu cotización».
  - Tarjeta de servicio: categoría, nombre (enlace al detalle), «por [proveedor]», orígenes → destinos (nombres de país), tipos de transporte y «Tránsito estimado: [min]–[max] días» si existe. Tarjeta de proveedor: logo o iniciales, nombre (enlace al perfil), categorías, «[n] servicios · [n] años en operación», resumen y cobertura.
  - Sin resultados: estado vacío «No encontramos resultados con estos filtros», con «Limpiar filtros» y «Hablar con un asesor» (WhatsApp).
- **RF-02.3** — Detalle del servicio `/marketplace/services/[id]`.
  - Migas (Marketplace / categoría / servicio), categoría, nombre, «por [proveedor]» (enlace a su perfil), transporte, origen, destino, tránsito, descripción y condiciones (si existen), y «Rutas habilitadas» con el nombre de cada corredor de `inquiryPrefill.corridorIds`.
  - Tarjeta del proveedor con su resumen y «Ver perfil».
  - Panel de cotización: con `canRequestQuote`, «Solicitar cotización» enlaza a `/inquiries/new?serviceId=<id>` (sin sesión, `proxy.ts` lleva a `/login?next=…` con ese destino) y explica los tres pasos (un asesor revisa, te escribe en la plataforma, recibes el total y su vigencia). Sin `canRequestQuote`: «Aún no se puede solicitar en línea» y «Hablar con un asesor» por WhatsApp con el nombre del servicio en el mensaje.
- **RF-02.4** — Perfil del proveedor `/marketplace/providers/[id]`.
  - Logo (o iniciales), insignia «Aprobado por Global 360», nombre, resumen, años en operación (si no es `null`), cobertura, «En el marketplace desde [mes año]» (`publishedAt`) y categorías.
  - Secciones «Acerca de» (`description`), «Capacidades» y «Certificaciones» (se ocultan si están vacías) y el llamado «¿Quieres trabajar con este proveedor?» con «Ver sus servicios» (ancla a la lista) y «Hablar con un asesor».
  - Lista paginada de sus servicios (`listProviderServices`) con «[n] servicios publicados».
  - No muestra web, email ni teléfono del proveedor (`backend/10 §11`).
- **RF-02.5** — SEO.
  - `generateMetadata` en los detalles: título «[nombre] · Marketplace · SEGlobal 360», descripción con el resumen o la descripción recortados a 160 caracteres, `canonical` sin parámetros y Open Graph.
  - JSON-LD `Service` en el detalle de servicio y `Organization` en el perfil, con `<` escapado.
  - `/marketplace` con filtros (`q`, `categoryId`…) lleva `robots: noindex, follow` y `canonical` a `/marketplace` (o `?tab=providers`).
  - `listSitemapEntries()` devuelve las URLs de todos los proveedores y servicios publicados (paginando de 50 en 50, en caché) para el `sitemap.ts` de la spec 03.
- **RF-02.6** — Errores y rate limit.
  - Con `RATE_LIMITED`, `NETWORK_ERROR` o 5xx, el listado y los detalles muestran un estado de error dentro del shell («No pudimos cargar el marketplace. Inténtalo en un minuto o escríbenos por WhatsApp»), no el `error.tsx` genérico, y la respuesta no se cachea.
  - La caché de RF-02.1 hace que las visitas no consuman el cupo por IP de la API: solo lo consume la revalidación.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/marketplace` (`?tab=`, `q`, filtros, `page`) | Público | `MvpMarketplace` | RF-02.1, RF-02.2, RF-02.5, RF-02.6 |
| `/marketplace/services/[id]` | Público | `MvpServicio` | RF-02.1, RF-02.3, RF-02.5, RF-02.6 |
| `/marketplace/providers/[id]` | Público | `MvpProveedor` | RF-02.1, RF-02.4, RF-02.5, RF-02.6 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /marketplace/corridors` | `backend/10 §4` (RF-10.1) | Filtro de ruta y nombres de los corredores habilitados |
| `GET /marketplace/services?categoryId=&corridorId=&transportType=&originCountryId=&destinationCountryId=&providerId=&q=&page=&pageSize=` | `backend/10 §4` (RF-10.4) | Pestaña Servicios |
| `GET /marketplace/services/:id` | `backend/10 §4` (RF-10.5) | Detalle del servicio |
| `GET /marketplace/providers?categoryId=&countryId=&corridorId=&transportType=&q=&page=&pageSize=` | `backend/10 §4` (RF-10.2) | Pestaña Proveedores |
| `GET /marketplace/providers/:id` | `backend/10 §4` (RF-10.3) | Perfil |
| `GET /marketplace/providers/:id/services` | `backend/10 §4` (RF-10.4) | Servicios del perfil |
| Catálogos (`countries`, `transport-types`, `service-categories`) | `backend/02 §4`, `backend/08 §4` | Nombres (feature `catalog`, spec 00) |

| Código | Comportamiento |
|---|---|
| `MARKETPLACE_SERVICE_NOT_FOUND`, `MARKETPLACE_PROVIDER_NOT_FOUND`, `INVALID_ID` | `notFound()` genérico |
| `INVALID_QUERY` | No debería llegar (RF-02.2); si llega, se muestra la lista sin filtros |
| `RATE_LIMITED`, `NETWORK_ERROR`, 5xx | Estado de error de RF-02.6 |

## 6. Estados y reglas de la interfaz

- Una ruta (corredor) se nombra «[país de origen] → [país de destino]» con los nombres del catálogo; su `code` (`CO-CR`) solo aparece como texto secundario.
- Un servicio con varios países de origen o destino los lista separados por comas.
- Las listas de capacidades, certificaciones y categorías respetan el orden que da la API.
- No se muestra ningún precio, comisión ni dato de contacto del proveedor (constitución §8).

## 7. Componentes, datos y caché

- Páginas Server Components; el único Client Component es el envío automático del formulario de filtros al cambiar un `<select>` (con botón «Buscar» para quien no tiene JS).
- Lecturas con caché pública (RF-02.1). Los catálogos se piden en paralelo con los datos.
- Logos con `<img>` según constitución §11.

## 8. Accesibilidad y SEO

- Pestañas como enlaces con `aria-current`; filtros en un `<form role="search">` con etiquetas visibles; el conteo de resultados en una región `aria-live` tras filtrar.
- Las tarjetas son artículos con su título como enlace (un solo enlace por tarjeta, más «Ver»).
- SEO según RF-02.5.

## 9. Criterios de aceptación

- **CA-02.1** (RF-02.1) — Los esquemas de `contracts.ts` aceptan los ejemplos de `backend/10 §4` (incluidos `logoUrl: null`, `yearsInOperation: 0` y `estimatedTransitDays: null`) y rechazan un detalle de servicio sin `canRequestQuote`. Un 404 `MARKETPLACE_SERVICE_NOT_FOUND` en `getService` termina en `notFound()`.
- **CA-02.2** (RF-02.2) — `/marketplace?tab=providers&categoryId=no-uuid&q=<120 caracteres>&page=0` llama a `listProviders` sin `categoryId`, con `q` de 100 caracteres y `page=1`. Con la semilla de la E2E (un proveedor publicado con dos servicios en CO-CR), la pestaña Servicios muestra «2 servicios», filtrar por la ruta CO-CR los mantiene y filtrar por una categoría sin servicios muestra el estado vacío con «Limpiar filtros». El formulario funciona con JS deshabilitado.
- **CA-02.3** (RF-02.3) — Con `canRequestQuote: true`, el detalle muestra «Solicitar cotización» con enlace a `/inquiries/new?serviceId=<id>` y la lista «Rutas habilitadas» con «Colombia → Costa Rica»; con `false`, muestra «Aún no se puede solicitar en línea» y el enlace de WhatsApp con el nombre del servicio. Sin sesión, seguir el enlace lleva a `/login?next=%2Finquiries%2Fnew%3FserviceId%3D<id>`.
- **CA-02.4** (RF-02.4) — El perfil de un proveedor publicado muestra su nombre, «Aprobado por Global 360» y sus servicios; con `capabilities: []` no muestra la sección «Capacidades»; no aparece ningún email, teléfono ni web del proveedor. Un proveedor no publicado responde la página 404 genérica.
- **CA-02.5** (RF-02.5) — El detalle de un servicio tiene `<title>` «[nombre] · Marketplace · SEGlobal 360», `canonical` sin parámetros y un JSON-LD válido sin `<` sin escapar. `/marketplace?q=flete` lleva `noindex, follow`. `listSitemapEntries()` con 60 servicios pide dos páginas de 50 y devuelve 60 URLs de servicio.
- **CA-02.6** (RF-02.6) — Con la API respondiendo 429, `/marketplace` muestra el estado de error dentro del shell con el enlace de WhatsApp y responde con status 200 de la página; una segunda visita con la API ya sana muestra los resultados (el error no quedó en caché). Dos visitas seguidas a `/marketplace` con la API sana hacen una sola llamada a `/marketplace/services` dentro de `PUBLIC_REVALIDATE`.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0031 | Contratos y lecturas cacheadas del marketplace, con traducción de 404 y errores | impl | F4 | RF-02.1, RF-02.6 | G360F-0012 | `src/features/marketplace/{contracts,api,messages}.ts` |
| G360F-0032 | Modelo: filtros desde `searchParams`, nombres de rutas, tránsito y textos de tarjetas | impl | F4 | RF-02.2, RF-02.3 | G360F-0031, G360F-0013 | `src/features/marketplace/model.ts` |
| G360F-0033 | Listado `/marketplace`: pestañas, buscador y filtros, tarjetas, conteo, paginación, vacío y estado de error | impl | F4 | RF-02.2, RF-02.6 | G360F-0032, G360F-0027 | `src/app/(site)/marketplace/page.tsx`, `src/features/marketplace/components/{MarketplaceFilters,ServiceCard,ProviderCard,MarketplaceError}.tsx` |
| G360F-0034 | Detalle del servicio con panel de cotización según `canRequestQuote` | impl | F4 | RF-02.3 | G360F-0033 | `src/app/(site)/marketplace/services/[id]/page.tsx`, `src/features/marketplace/components/{ServiceDetail,QuotePanel}.tsx` |
| G360F-0035 | Perfil del proveedor con sus servicios paginados | impl | F4 | RF-02.4 | G360F-0033 | `src/app/(site)/marketplace/providers/[id]/page.tsx`, `src/features/marketplace/components/ProviderProfile.tsx` |
| G360F-0036 | Metadatos, JSON-LD, `noindex` de listados filtrados y `listSitemapEntries` | impl | F4 | RF-02.5 | G360F-0034, G360F-0035 | `src/features/marketplace/{seo,api}.ts`, `generateMetadata` de las páginas |
| G360F-0037 | Tests de contratos, filtros y modelo | test | F4 | CA-02.1, CA-02.2 | G360F-0032 | `src/features/marketplace/*.test.ts` |
| G360F-0038 | Tests de componentes: panel de cotización, perfil sin secciones vacías y estado de error | test | F4 | CA-02.3, CA-02.4, CA-02.6 | G360F-0035 | `src/features/marketplace/components/*.test.tsx` |
| G360F-0039 | Tests de SEO y de `listSitemapEntries` | test | F4 | CA-02.5 | G360F-0036 | `src/features/marketplace/seo.test.ts` |
| G360F-0040 | E2E del marketplace contra el backend de desarrollo (proveedor publicado, corredor activo) con axe y caché | test | F4 | CA-02.2, CA-02.3, CA-02.4, CA-02.6 | G360F-0036 | `e2e/marketplace.spec.ts`, `e2e/support/seed-marketplace.ts` |

## 11. Fuera de alcance y preguntas abiertas

- URLs amigables con *slug*, destacados, orden por relevancia, calificaciones y reseñas: post-MVP (`backend/10 §11`). Las URLs públicas van por UUID.
- Mapa de cobertura interactivo: post-MVP.
- **Pregunta:** ¿la búsqueda ignora las tildes? La API las distingue («marítimo» ≠ «maritimo»). Por defecto: se envía el texto tal cual y el estado vacío sugiere probar sin tildes o con otras palabras.
- **Backend/10** — La búsqueda distingue tildes y los visitantes suelen escribir sin ellas. Por defecto: se envía el texto tal cual; se propone a la API una comparación insensible a tildes (collation `es` con fuerza 1).
- **Backend/10** — `GET /marketplace/corridors` no informa cuántos servicios tiene cada ruta, y el bloque de rutas de la landing no puede decir «[n] servicios». Por defecto: no se muestra el conteo por ruta.
