# Spec 03 — Sitio público y landing (`site`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/site`, `src/app/(site)`, `src/app/{robots,sitemap}.ts`, `src/shared/lib/acquisition.ts` |
| Rutas | `/`, `/legal/terms`, `/legal/privacy`, `/get-quote` |
| Backend | `backend/10` (Aprobada), `backend/08` (categorías, Implementada), `backend/07` (adquisición, Implementada) |
| Depende de | Specs 00, 01 y 02 |

## 1. Resumen y alcance

Es la landing informativa de SEGlobal 360, por la que llegan clientes y proveedores (`backend/CLAUDE.md`, *Alcance y fases*). Se hace en dos pasos:

1. **F1:** se migra a este repositorio la landing que hoy está publicada (`../global360_frontend`), con el mismo contenido, el mismo aspecto y el mismo SEO. Se añaden las páginas legales, la captura de la adquisición y los llamados a cotizar.
2. **F4:** se añaden los bloques del MVP de la maqueta, que conectan con el marketplace: el buscador del hero, «Cómo funciona», las rutas con cotización en línea, los proveedores aprobados, «¿Eres proveedor?» y el contacto con cotización.

La landing nunca se rompe: si la API falla, los bloques con datos se ocultan y el resto se sirve igual.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Secciones actuales (Inicio, Servicios, Logística, Cobertura, Contacto), contenido, imágenes, OG, JSON-LD, `robots`, `sitemap` | `../global360_frontend/{app,components,lib}`; artboards `Main`, `Inicio`, `Servicios`, `Logistica`, `Cobertura`, `Contacto`, `Header`, `Footer` |
| Orden de la landing del MVP y sus bloques nuevos | Artboards `MvpLanding`, `MvpHeader`, `MvpInicio`, `MvpComoFunciona`, `MvpRutas`, `MvpProveedores`, `MvpSoyProveedor`, `MvpContacto` |
| De dónde sale cada dato de los bloques y que se ocultan si vienen vacíos | Nota `nota-bloques` del canvas |
| «Solicitar cotización» va a `/register` sin sesión y a `/inquiries/new` con sesión | Nota `nota-bloques` |
| UTM y `document.referrer` en `acquisition` de `POST /registrations` | Nota `nota-bloques`; `backend/07 §4` y §11 (los UTM los conserva el front) |
| Casilla de términos y política de datos en el registro | Artboard `MvpRegistro` |

## 3. Requisitos funcionales

- **RF-03.1** — Migración de la landing actual.
  - Las secciones de `../global360_frontend/components` (Hero, Services, InternationalLogistics, LogisticsSolutions, Categories, Coverage, RouteLines, CtaBanner, SectionHeading) pasan a `features/site/components`, y su contenido (`lib/content.ts`) a `features/site/content.ts`, con el mismo texto (incluidos los subtítulos en inglés) y adaptadas a los tokens y al kit de la spec 01.
  - Los datos de contacto de `lib/site.ts` pasan a `features/site/site.ts`; el número y el mensaje de WhatsApp salen de `public-env.ts`.
  - `public/images/hero.jpg`, `opengraph-image.jpg` (con su `alt`) e `icon.svg` se copian tal cual, con los créditos del README de la landing.
  - La página `/` (Server Component estático) renderiza las secciones en el orden de la landing actual, con `SiteHeader` (anclas `#inicio`, `#servicios`, `#logistica`, `#cobertura`, `#contacto`), `SiteFooter` y `WhatsAppFloat`.
- **RF-03.2** — SEO.
  - Metadatos de la landing: título «SEGlobal 360 | Soluciones Logísticas Globales», descripción, palabras clave, `canonical: /`, Open Graph `es_CO` y Twitter `summary_large_image`, `themeColor` navy, con `metadataBase` = `NEXT_PUBLIC_SITE_URL`.
  - JSON-LD `Organization` (nombre, URL, logo, lema, `contactPoint` con WhatsApp, `sameAs` con las redes) con `<` escapado.
  - `robots.ts`: permite todo salvo `/portal`, `/account`, `/company`, `/inquiries`, `/quotes`, `/provider`, `/backoffice`, `/session`, `/api`, `/dev`, `/get-quote` y las páginas de acceso con token; enlaza el sitemap.
  - `sitemap.ts`: `/`, `/marketplace` y las páginas legales.
- **RF-03.3** — Páginas legales. `/legal/terms` (términos y condiciones) y `/legal/privacy` (política de tratamiento de datos personales), con el texto que entregue gerencia, la fecha de vigencia y su versión, enlazadas desde el pie y desde el registro (spec 04). Mientras no haya texto, la página muestra «[Texto pendiente de gerencia]» y lleva `noindex`.
- **RF-03.4** — Captura de la adquisición.
  - En la primera visita (sin la cookie `g360_acq`), `proxy.ts` guarda en una cookie `httpOnly`, `SameSite=Lax`, de 90 días, `{source, medium, campaign, referrer}`: `utm_source`, `utm_medium` y `utm_campaign` de la URL, y el **origen** de la cabecera `Referer` si es de otro sitio. Cada valor se recorta a 100 caracteres; si no hay ningún dato, no se escribe la cookie.
  - La primera atribución gana: una visita posterior con otros UTM no la cambia.
  - El registro (spec 04) la lee y la envía en `acquisition`.
- **RF-03.5** — Llamados a la acción.
  - `GET /get-quote` (route handler que solo redirige): con cookie de sesión, a `/inquiries/new`; sin ella, a `/register?next=%2Finquiries%2Fnew`. Todos los «Solicitar cotización» de la landing apuntan ahí.
  - «Crear cuenta» va a `/register`; «Ingresar», a `/login`; «Registrarme como proveedor», a `/register?type=provider`.
  - Los enlaces de WhatsApp usan `whatsappUrl(mensaje)` con `NEXT_PUBLIC_WHATSAPP_NUMBER`, abren en otra pestaña con `rel="noopener noreferrer"` y llevan texto accesible.
- **RF-03.6** — Bloques del MVP.
  - La landing pasa al orden de `MvpLanding`: hero con buscador, Servicios, Cómo funciona, Logística, Rutas, Cobertura, Proveedores, ¿Eres proveedor?, Contacto. `SiteHeader` usa la navegación de `MvpHeader` (Servicios, Cómo funciona, Cobertura, Marketplace, Contacto, «Ingresar» y «Crear cuenta»).
  - **Hero con buscador:** formulario `GET` a `/marketplace` con `q` y la categoría (`categoryId`, desde `GET /service-categories`), con el aviso «Sin precios publicados: tu cotización la arma un asesor».
  - **Cómo funciona** (`#como-funciona`): los cinco pasos estáticos de la maqueta y los botones «Crear cuenta de empresa» y WhatsApp.
  - **Rutas:** una tarjeta por corredor de `GET /marketplace/corridors` con «[origen] → [destino]», el código, los tipos de transporte y las monedas (nombres del catálogo) y «Ver servicios en esta ruta» (`/marketplace?corridorId=`), más «¿Tu ruta no aparece?» con WhatsApp. **Si no hay corredores activos, el bloque no se muestra.**
  - **Proveedores aprobados:** los cuatro primeros de `GET /marketplace/providers?pageSize=4` (orden alfabético de la API) como tarjetas, con «Ver todo el marketplace». **Si viene vacío, el bloque no se muestra.**
  - **¿Eres proveedor?:** los tres pasos, las categorías del catálogo y las rutas activas como texto («Rutas disponibles hoy: …»; se omite la frase si no hay).
  - **Contacto:** «Solicitar cotización» (`/get-quote`), WhatsApp y el aviso «Para cotizar en línea necesitas una cuenta de empresa validada por Global 360».
  - Cada bloque con datos va en su `<Suspense>` con un esqueleto; si su lectura falla (`NETWORK_ERROR`, `RATE_LIMITED`, 5xx), el bloque no se renderiza y se loguea una vez.
- **RF-03.7** — Sitemap del marketplace. `sitemap.ts` añade las URLs de `listSitemapEntries()` (spec 02), y si la API falla devuelve solo las URLs fijas.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/` | Público | `Main` (F1); `MvpLanding` y sus bloques (F4) | RF-03.1, RF-03.2, RF-03.5, RF-03.6 |
| `/legal/terms`, `/legal/privacy` | Público | — | RF-03.3 |
| `/get-quote` | Público (solo redirige) | — | RF-03.5 |
| `/robots.txt`, `/sitemap.xml` | Público | — | RF-03.2, RF-03.7 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /service-categories` | `backend/08 §4` | Buscador del hero y «¿Eres proveedor?» (vía `catalog`) |
| `GET /marketplace/corridors` | `backend/10 §4` | Bloque de rutas (vía `marketplace`) |
| `GET /marketplace/providers?pageSize=4` | `backend/10 §4` | Bloque de proveedores (vía `marketplace`) |
| `POST /registrations` (`acquisition`) | `backend/07 §4` | Destino de la cookie de RF-03.4 (lo envía la spec 04) |

Los errores de la API no llegan al usuario en la landing: un bloque que falla se oculta (RF-03.6).

## 6. Estados y reglas de la interfaz

- El hero ocupa la primera pantalla con la imagen del buque y el degradado navy; en móvil, el buscador se apila (texto, categoría y botón a lo ancho).
- Los bloques ocultos no dejan títulos ni espacios vacíos.
- La landing no muestra precios ni comisiones.

## 7. Componentes, datos y caché

- La página es estática; los bloques con datos son Server Components con `'use cache'` (por la feature `marketplace`), así que la landing entera se prerenderiza y se revalida cada `PUBLIC_REVALIDATE`.
- Imagen del hero con `next/image` (`priority`, `sizes="100vw"`), que es el LCP.
- Animación `.reveal` solo con CSS, sin JS.

## 8. Accesibilidad y SEO

- Un `<h1>` (el del hero), secciones con `aria-labelledby` y anclas con `scroll-padding-top` para el encabezado fijo.
- El buscador del hero tiene etiquetas visibles o accesibles en sus dos campos y un `<form role="search">`.
- SEO según RF-03.2 y RF-03.7.

## 9. Criterios de aceptación

- **CA-03.1** (RF-03.1) — La página `/` muestra las cinco secciones de la landing actual con sus títulos y textos (comparados con `lib/content.ts` de `../global360_frontend`), la imagen del hero, el botón flotante de WhatsApp con el número de `NEXT_PUBLIC_WHATSAPP_NUMBER`, y pasa axe sin violaciones *serious* ni *critical* a 360 y a 1440 px.
- **CA-03.2** (RF-03.2) — `/` tiene el `<title>`, la `description`, el `canonical` y las etiquetas Open Graph de RF-03.2 y un JSON-LD `Organization` válido. `robots.txt` niega `/portal`, `/backoffice` y `/api`, y `sitemap.xml` incluye `/`, `/marketplace` y las páginas legales.
- **CA-03.3** (RF-03.3) — `/legal/privacy` sin texto de gerencia muestra «[Texto pendiente de gerencia]» con `noindex`; con texto, lo muestra con su versión y fecha, y el pie enlaza a las dos páginas.
- **CA-03.4** (RF-03.4) — Una primera visita a `/?utm_source=meta_ads&utm_medium=cpc&utm_campaign=lanzamiento` con `Referer: https://www.instagram.com/p/xyz` crea `g360_acq` con `{source: meta_ads, medium: cpc, campaign: lanzamiento, referrer: https://www.instagram.com}`; una segunda visita con `utm_source=google` no la cambia; una visita sin UTM ni `Referer` externo no crea la cookie; un `utm_campaign` de 150 caracteres se guarda con 100.
- **CA-03.5** (RF-03.5) — `GET /get-quote` con cookie de sesión redirige a `/inquiries/new`; sin ella, a `/register?next=%2Finquiries%2Fnew`. Todos los «Solicitar cotización» de `/` apuntan a `/get-quote` y todos los enlaces de WhatsApp llevan `rel="noopener noreferrer"`.
- **CA-03.6** (RF-03.6) — Con CO-CR activo y dos proveedores publicados, `/` muestra el bloque de rutas con «Colombia → Costa Rica» y su enlace a `/marketplace?corridorId=<id>`, y el de proveedores con dos tarjetas. Con los dos corredores en `draft`, el bloque de rutas no aparece (ni su título) y «¿Eres proveedor?» omite la frase de rutas. Con la API caída, `/` responde 200 con el resto de las secciones. El buscador del hero envía `q` y `categoryId` a `/marketplace`.
- **CA-03.7** (RF-03.7) — Con dos servicios y un proveedor publicados, `sitemap.xml` incluye sus tres URLs; con la API caída, incluye solo las URLs fijas y responde 200.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0041 | Migración de las secciones, el contenido, las imágenes y los datos de contacto de la landing actual | impl | F1 | RF-03.1 | G360F-0023 | `src/features/site/{content,site}.ts`, `src/features/site/components/*.tsx`, `src/app/(site)/page.tsx`, `public/images/*` |
| G360F-0042 | Metadatos, JSON-LD `Organization`, `robots.ts` y `sitemap.ts` con las URLs fijas | impl | F1 | RF-03.2 | G360F-0041 | `src/app/(site)/layout.tsx`, `src/app/{robots,sitemap}.ts`, `src/app/opengraph-image.jpg`, `src/app/icon.svg` |
| G360F-0043 | Páginas legales con versión y fecha, y `noindex` mientras no haya texto | impl | F1 | RF-03.3 | G360F-0023 | `src/app/(site)/legal/{terms,privacy}/page.tsx`, `src/features/site/legal.ts` |
| G360F-0044 | Captura de la adquisición en `proxy.ts` con la cookie `g360_acq` | impl | F1 | RF-03.4 | G360F-0010 | `src/shared/lib/acquisition.ts`, `proxy.ts` |
| G360F-0045 | `/get-quote` y enlaces de WhatsApp | impl | F1 | RF-03.5 | G360F-0041, G360F-0009 | `src/app/(site)/get-quote/route.ts`, `src/features/site/whatsapp.ts` |
| G360F-0046 | Tests de adquisición, `/get-quote`, `robots` y `sitemap` fijos | test | F1 | CA-03.2, CA-03.4, CA-03.5 | G360F-0042, G360F-0044, G360F-0045 | `src/shared/lib/acquisition.test.ts`, `src/app/(site)/get-quote/route.test.ts`, `src/app/{robots,sitemap}.test.ts` |
| G360F-0047 | E2E de la landing migrada y de las páginas legales con axe a 360 y 1440 px | test | F1 | CA-03.1, CA-03.3 | G360F-0043, G360F-0045 | `e2e/landing.spec.ts` |
| G360F-0048 | Bloques del MVP: hero con buscador, Cómo funciona, Rutas, Proveedores, ¿Eres proveedor? y Contacto, con `Suspense` y ocultación ante error o vacío | impl | F4 | RF-03.6 | G360F-0031, G360F-0041 | `src/features/site/components/{HeroSearch,HowItWorks,RoutesBlock,ProvidersBlock,ProviderCallout,QuoteContact}.tsx`, `src/app/(site)/page.tsx` |
| G360F-0049 | Sitemap con las URLs del marketplace y respaldo si la API falla | impl | F4 | RF-03.7 | G360F-0036, G360F-0042 | `src/app/sitemap.ts` |
| G360F-0050 | Tests de los bloques (vacío, error, contenido) y E2E de la landing con datos y del sitemap | test | F4 | CA-03.6, CA-03.7 | G360F-0048, G360F-0049 | `src/features/site/components/*.test.tsx`, `e2e/landing-mvp.spec.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Formulario público de leads (contacto sin cuenta): F10 (épica de CRM).
- Versión en inglés del sitio: F12. Los subtítulos en inglés de la landing actual se conservan como están.
- **Pregunta:** ¿la cookie de adquisición necesita aviso o consentimiento? No guarda datos personales ni es de terceros. Por defecto: se informa en la política de datos, sin banner.
- **Pregunta:** perfiles reales de Instagram y LinkedIn (`lib/site.ts` tiene marcadores) y textos legales. Por defecto: las redes se omiten del pie y del JSON-LD hasta tener las URL; los legales muestran el marcador de RF-03.3.
- **Pregunta:** ¿cuándo se apaga `../global360_frontend`? Por defecto: al migrar el dominio en el go-live (spec 12); hasta entonces la landing nueva solo se publica en el ambiente de pruebas.
- **Backend/10** — La proyección pública del corredor no trae `quoteValidityDays`, y la maqueta muestra «Vigencia de la cotización: 15 días» en el bloque de rutas. Por defecto: la tarjeta no muestra la vigencia.
- **Backend/07** — `acquisition` acepta texto libre de hasta 100 caracteres y marketing no ha fijado la lista de `source`. Por defecto: se envía `utm_source` tal cual llega.
