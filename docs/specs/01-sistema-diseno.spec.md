# Spec 01 — Sistema de diseño y layouts (`shared/ui`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/shared/ui`, `src/app/globals.css`, layouts de `src/app/{(site),(auth),(portal),backoffice}` |
| Rutas | `/dev/ui` (solo fuera de producción) |
| Backend | — |
| Depende de | Spec 00 |

## 1. Resumen y alcance

Es el kit de componentes propio sobre HTML nativo y Tailwind 4, con los tokens de la marca, y los cuatro *shells* de la aplicación: sitio público, acceso, portal de empresa y backoffice. Los componentes son de presentación: reciben datos por props y no conocen la API. Qué datos llevan los shells (empresa, permisos, usuario) lo resuelven los layouts de cada superficie en sus specs (03, 04, 05 y 08).

## 2. Origen

| Requisito | Fuente |
|---|---|
| Paleta navy/gold/ivory, Inter + Montserrat, degradado dorado, animación `fade-up` y `.reveal` | `../global360_frontend/app/globals.css` y `app/layout.tsx` |
| Logo SVG, encabezado y pie del sitio | `../global360_frontend/components/{Logo,Header,Footer,WhatsAppLink}.tsx`; artboards `Header`, `Footer`, `MvpHeader` |
| Botones píldora, campos con etiqueta y asterisco, tarjetas de selección, pasos numerados | Artboards `MvpRegistro`, `MvpLogin`, `PortalNuevaSolicitud` |
| Menú lateral del portal con empresa, estado, «Nueva solicitud» y usuario | Artboard `PortalNav` |
| Tablas, filtros, paginación «Página 1 de [n]», insignias de estado, vacíos | Artboards `PortalSolicitudes`, `PortalUsuarios`, `MvpMarketplace` |
| Accesibilidad (objetivos de 44 px, foco, `aria-*`) | Constitución §9; notas de diseño del canvas |

## 3. Requisitos funcionales

- **RF-01.1** — Tokens y tipografía.
  - `globals.css` migra el `@theme` de la landing (colores `navy-*`, `gold-*`, `ivory`, `whatsapp*`, `fade-up`) y añade tokens semánticos para el portal: superficies (`surface`, `surface-muted`, `border`), texto (`ink`, `ink-muted`), tonos de estado (`info`, `success`, `warning`, `danger`, `neutral`, cada uno con fondo y texto que cumplen 4,5:1), radios, sombras y anillo de foco (`focus-ring`, dorado sobre navy y navy sobre claro).
  - Inter (`--font-sans`) y Montserrat (`--font-display`) con `next/font/google`, `display: swap` y subconjunto `latin`.
  - Utilidades `text-gold-gradient` y `text-gold-gradient-deep`, `.reveal` y el bloque `prefers-reduced-motion` de la landing.
- **RF-01.2** — Componentes de acción y de formulario.
  - `Button` y `ButtonLink` (variantes `primary` dorado, `secondary` contorno, `ghost`, `danger`, `whatsapp`; tamaños `md` y `lg`; alto mínimo 44 px; icono opcional) y `SubmitButton`, que usa `useFormStatus` para mostrarse ocupado y deshabilitado mientras envía.
  - `Field` (etiqueta, marca de obligatorio, pista, error con `aria-describedby` y `aria-invalid` en el control), `Input`, `PasswordInput` (mostrar u ocultar), `Textarea` (con contador si tiene `maxLength`), `Select` nativo, `Checkbox`, `RadioCardGroup` (tarjetas seleccionables como «Cliente / Proveedor / Ambos», sobre `<input type="radio">`) y `FieldGroup` (`<fieldset>` con `<legend>`).
  - `FormErrorSummary`: con `aria-live="polite"`, lista los errores del `ActionState` y enlaza cada uno con su campo. `useFocusFirstError` lleva el foco al primer campo inválido tras un envío.
- **RF-01.3** — Componentes de datos y de estado.
  - `Card`, `DescriptionList` (`<dl>`), `Table` (con `<caption>` y desplazamiento horizontal dentro de su caja en móvil), `Pagination` (enlaces «Anterior»/«Siguiente» y «Página X de N» que conservan los demás `searchParams`), `Tabs` por URL (enlaces con `aria-current="page"`), `Breadcrumbs`, `Stepper` (pasos numerados con estado hecho, actual y pendiente), `Avatar` de iniciales y `Timeline` (lista de estados con fecha).
  - `StatusBadge` con `tone` (`info`, `success`, `warning`, `danger`, `neutral`) y texto; nunca solo color.
  - `Alert` (los cuatro tonos, con título, acción opcional y `role="status"` o `role="alert"` según el tono), `EmptyState` (título, texto y acción), `Skeleton` y `Spinner` con texto para lectores de pantalla.
  - `Dialog` sobre `<dialog>` con `showModal()`: foco atrapado, `Escape` cierra, el foco vuelve al disparador; `ConfirmDialog` con motivo opcional u obligatorio (`Textarea` con mínimo 1 y máximo 500) que envía una Server Action.
- **RF-01.4** — Shell del sitio público.
  - `SiteHeader`: logo con enlace al inicio, navegación (Servicios, Cómo funciona, Cobertura, Marketplace, Contacto; anclas en la landing y enlaces fuera de ella), «Ingresar» y «Crear cuenta», o «Ir a mi portal» si el layout indica que hay sesión. En móvil, menú desplegable con `<details>` o `Dialog`. Fijo arriba con el fondo navy translúcido de la maqueta.
  - `SiteFooter` (logo, lema «Tu empresa, sin fronteras.», enlaces legales y redes) y `WhatsAppFloat` (botón fijo con `aria-label`).
  - `SkipLink` («Saltar al contenido») como primer elemento enfocable en los cuatro shells.
- **RF-01.5** — Shell de acceso. `AuthLayout`: fondo navy con el logo, tarjeta central clara con `<h1>`, enlace para volver al sitio y espacio para el texto de ayuda («¿Ya tienes cuenta? Ingresar»).
- **RF-01.6** — Shell del portal.
  - `PortalShell` recibe la empresa (`name`, `statusLabel`, `statusTone`), los elementos del menú (`href`, `label`, `icon`, `current`), la acción principal («Nueva solicitud», con estado deshabilitado y su motivo, p. ej. «Disponible cuando validemos tu empresa»), el usuario (`name` o `email`) y la acción de salir.
  - Escritorio: menú lateral fijo de 280 px como el artboard `PortalNav`. Móvil (< 1024 px): barra superior con botón de menú que abre el lateral en un `Dialog`.
  - El elemento actual lleva `aria-current="page"`.
- **RF-01.7** — Shell del backoffice. `BackofficeShell`: menú lateral agrupado (Operación, Comercial, Administración) con los elementos que recibe, cabecera con el usuario y salir, y una insignia del ambiente («Pruebas», «Desarrollo») cuando no es producción. Densidad mayor que el portal (tablas de 14 px) con los mismos tokens.
- **RF-01.8** — Estados de segmento y catálogo visual.
  - `error.tsx` (con «Reintentar» y el `digest` como código de soporte) y `loading.tsx` (esqueleto del shell) en cada segmento raíz: `(site)`, `(auth)`, `(portal)` y `backoffice`.
  - `/dev/ui`: página con todos los componentes en sus variantes y estados, que responde `notFound()` en producción; la usan las pruebas de accesibilidad.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/dev/ui` | Solo desarrollo y pruebas | — | RF-01.8 |
| Layout de `(site)` | Público | `Header`, `MvpHeader`, `Footer` | RF-01.4 |
| Layout de `(auth)` | Público | `MvpLogin`, `MvpRegistro` | RF-01.5 |
| Layout de `(portal)` | Usuario de empresa | `PortalNav` | RF-01.6 |
| Layout de `backoffice` | Personal interno | — (sin maqueta) | RF-01.7 |

## 5. Contrato consumido

Ninguno: los componentes no llaman a la API.

## 6. Estados y reglas de la interfaz

- Tonos de estado (las specs asignan cada estado a un tono): `info` en curso, `success` completado o activo, `warning` requiere acción o vence pronto, `danger` rechazado o bloqueado, `neutral` terminado sin acción.
- Un botón deshabilitado muestra junto a él el motivo, no solo un *tooltip*.
- Fechas, montos y estados se muestran con `shared/format` y las etiquetas del `model.ts` de cada feature; los componentes no formatean.

## 7. Componentes, datos y caché

- Server Components salvo los interactivos: `SubmitButton`, `PasswordInput`, `Textarea` con contador, `Dialog`, `ConfirmDialog`, `FormErrorSummary`, el menú móvil de los shells.
- Iconos de `lucide-react` (con `aria-hidden`) y banderas de `country-flag-icons` en `CountryFlag`.
- El logo es el SVG de la landing (`Logo.tsx`), con su degradado dorado.

## 8. Accesibilidad y SEO

- Todos los controles cumplen constitución §9; el anillo de foco es visible sobre fondo claro y sobre navy.
- `Table` usa `<th scope>`; `Pagination` va en un `<nav aria-label="Paginación">`; `Tabs` y menús, en `<nav>` con `aria-label`.
- Los shells declaran `header`, `nav`, `main id="contenido"` y `footer`.

## 9. Criterios de aceptación

- **CA-01.1** (RF-01.1) — Dado `globals.css`, entonces define los tokens de la landing y los semánticos de RF-01.1, y cada par fondo/texto de los tonos de estado tiene contraste ≥ 4,5:1 (comprobado en la prueba). Una búsqueda de `#[0-9a-fA-F]{3,6}` y de `-\[[0-9]+px\]` en `src/shared/ui`, `src/features` y `src/app` (salvo `globals.css`) no encuentra nada.
- **CA-01.2** (RF-01.2) — Un `Field` con error muestra el texto, marca el control con `aria-invalid="true"` y lo enlaza con `aria-describedby`; sin error, no tiene ninguno de los dos. `SubmitButton` queda deshabilitado y con `aria-busy` mientras el formulario envía. `RadioCardGroup` se recorre con las flechas y se selecciona con espacio. `FormErrorSummary` anuncia los errores y `useFocusFirstError` lleva el foco al primer campo inválido.
- **CA-01.3** (RF-01.3) — `Pagination` con `page=2`, `pageSize=20`, `total=45` y `?status=new` muestra «Página 2 de 3» y enlaces a `?status=new&page=1` y `?status=new&page=3`; en la última página, «Siguiente» no es un enlace. `Dialog` abierto atrapa el foco, se cierra con `Escape` y devuelve el foco al botón que lo abrió. `ConfirmDialog` con motivo obligatorio no envía con el motivo vacío. `StatusBadge` siempre tiene texto visible.
- **CA-01.4** (RF-01.4) — A 360 px, `SiteHeader` muestra el logo y un botón «Menú» que despliega la navegación con todos sus enlaces; a 1440 px los muestra en línea. El primer `Tab` de la página enfoca «Saltar al contenido», que lleva el foco a `main`.
- **CA-01.5** (RF-01.5) — `AuthLayout` renderiza un único `<h1>` (el título que recibe), el logo con enlace a `/` y el contenido en una tarjeta; pasa axe sin violaciones *serious* ni *critical*.
- **CA-01.6** (RF-01.6) — `PortalShell` con tres elementos (uno actual) los muestra en ese orden, con `aria-current="page"` solo en el actual; con la acción principal deshabilitada, muestra su motivo como texto. A 360 px el menú está oculto tras un botón y se abre en un diálogo; a 1440 px es un lateral fijo.
- **CA-01.7** (RF-01.7) — `BackofficeShell` agrupa los elementos por su grupo, oculta los grupos vacíos y muestra la insignia «Pruebas» cuando el ambiente es `test`; en producción no la muestra.
- **CA-01.8** (RF-01.8) — Un error lanzado dentro de una página de `(portal)` muestra el `error.tsx` del portal con «Reintentar» y el código de soporte, sin el mensaje del error. `/dev/ui` responde 404 con `NODE_ENV=production`, y fuera de producción pasa axe sin violaciones *serious* ni *critical* a 360 y a 1440 px.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0020 | Tokens de la landing y semánticos, fuentes con `next/font` y utilidades en `globals.css` | impl | F1 | RF-01.1 | G360F-0005 | `src/app/globals.css`, `src/app/layout.tsx`, `src/shared/ui/fonts.ts` |
| G360F-0021 | Componentes de acción y de formulario, `FormErrorSummary` y `useFocusFirstError` | impl | F1 | RF-01.2 | G360F-0020, G360F-0007 | `src/shared/ui/{Button,SubmitButton,Field,Input,PasswordInput,Textarea,Select,Checkbox,RadioCardGroup,FieldGroup,FormErrorSummary}.tsx` |
| G360F-0022 | Componentes de datos y de estado, `Dialog` y `ConfirmDialog` | impl | F1 | RF-01.3 | G360F-0020 | `src/shared/ui/{Card,DescriptionList,Table,Pagination,Tabs,Breadcrumbs,Stepper,Avatar,Timeline,StatusBadge,Alert,EmptyState,Skeleton,Dialog,ConfirmDialog}.tsx` |
| G360F-0023 | Shell del sitio: `Logo`, `SiteHeader` con menú móvil, `SiteFooter`, `WhatsAppFloat` y `SkipLink` | impl | F1 | RF-01.4 | G360F-0022 | `src/shared/ui/site/*.tsx` |
| G360F-0024 | Shell de acceso `AuthLayout` | impl | F1 | RF-01.5 | G360F-0022 | `src/shared/ui/auth/AuthLayout.tsx` |
| G360F-0025 | Shell del portal `PortalShell` con menú lateral y versión móvil | impl | F1 | RF-01.6 | G360F-0022 | `src/shared/ui/portal/*.tsx` |
| G360F-0026 | Shell del backoffice `BackofficeShell` con grupos e insignia de ambiente | impl | F1 | RF-01.7 | G360F-0022 | `src/shared/ui/backoffice/*.tsx` |
| G360F-0027 | `error.tsx` y `loading.tsx` de cada segmento raíz y catálogo visual `/dev/ui` | impl | F1 | RF-01.8 | G360F-0023, G360F-0024, G360F-0025, G360F-0026, G360F-0008 | `src/app/*/error.tsx`, `src/app/*/loading.tsx`, `src/app/dev/ui/page.tsx` |
| G360F-0028 | Tests de componentes de formulario, datos y diálogos | test | F1 | CA-01.2, CA-01.3 | G360F-0021, G360F-0022 | `src/shared/ui/*.test.tsx` |
| G360F-0029 | Tests de los cuatro shells (orden, actual, móvil, grupos, ambiente) | test | F1 | CA-01.4, CA-01.5, CA-01.6, CA-01.7 | G360F-0027 | `src/shared/ui/{site,auth,portal,backoffice}/*.test.tsx` |
| G360F-0030 | E2E de `/dev/ui` con axe a 360 y 1440 px, prueba de contraste de tonos y búsqueda de hex y tamaños arbitrarios | test | F1 | CA-01.1, CA-01.8 | G360F-0027 | `e2e/ui-kit.spec.ts`, `src/shared/ui/tokens.test.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Modo oscuro: fuera del MVP. Los tokens semánticos lo dejan preparado.
- Notificaciones tipo *toast*: no hay en el MVP; las confirmaciones son un `Alert` en la propia pantalla.
- **Pregunta:** ¿el backoffice usa la misma marca o una más sobria? Por defecto, los mismos tokens con mayor densidad y fondo `surface`.
- **Backend/03** — `GET /me/grants` no trae los nombres de los roles del usuario, y la maqueta muestra «Administrador» u «Operativo» en el menú; `client_operator` no tiene `role:read` para pedirlos. Por defecto: el menú muestra el nombre del usuario y su email, sin el rol.
