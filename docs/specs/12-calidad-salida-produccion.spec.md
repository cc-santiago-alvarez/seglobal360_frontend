# Spec 12 — Calidad y salida a producción

| | |
|---|---|
| Estado | Borrador |
| Features | `e2e/`, `Dockerfile`, `.dockerignore`, `.github/workflows/`, `src/app/api/vitals`, `src/shared/lib/web-vitals.ts`; infraestructura fuera del repositorio |
| Rutas | `/api/vitals` |
| Backend | `backend/14` (Borrador), `backend/00` (`TRUSTED_PROXIES`, `CORS_ALLOWED_ORIGINS`), `backend/06` (`APP_PUBLIC_URL`) |
| Depende de | Specs 00 a 11 |

## 1. Resumen y alcance

Reúne lo que hace falta para poner el MVP en producción con confianza: la E2E de punta a punta por la interfaz, la accesibilidad, los presupuestos de rendimiento, el contenedor, la canalización de CI, el monitoreo y las alertas, la migración del dominio www.seglobal360.com desde la landing anterior y la checklist de go-live coordinada con el backend. La E2E de la API (`backend/14`) no prueba la interfaz: esta spec sí.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Criterio de F6: E2E y matriz de autorización en verde, alertas activas, go-live: MVP en producción | `backend/CLAUDE.md`, *Alcance y fases* |
| Flujo E2E de la API, ambientes, alertas (5xx > 1 % en 5 min, `/health` en 503 > 2 min), checklist de go-live (`APP_PUBLIC_URL`, CORS, HTTPS, SPF y DKIM) | `backend/14 §3` |
| Accesibilidad, rendimiento, despliegue en contenedor junto a la API, logs y alertas del front | Constitución §9, §11 y §14 |
| Landing actual en Vercel y su dominio | `../global360_frontend/README.md` |

## 3. Requisitos funcionales

- **RF-12.1** — E2E de punta a punta por la interfaz (Playwright, contra el ambiente de pruebas con la semilla del backend y `NOTIFIER=file`):
  1. El superadmin crea la regla de comisión de CO-CR y activa el corredor (spec 09).
  2. Una empresa proveedora se registra, verifica su correo, completa y envía su perfil; Global 360 la valida, aprueba y publica el perfil; el proveedor publica un servicio y Global 360 lo habilita en CO-CR (specs 04, 07 y 09).
  3. Una empresa cliente llega por la landing con UTM, se registra, verifica su correo y Global 360 la valida (specs 03, 04 y 09).
  4. El cliente encuentra el servicio en el marketplace y crea la solicitud desde él (specs 02 y 06).
  5. Un asesor la toma, envía un mensaje compartido, arma y envía la cotización (spec 10).
  6. El cliente lee el mensaje, acepta la cotización, y la empresa aparece como «Consolidado» en `/backoffice/clients`, con la fuente de su UTM; el embudo cuenta la aceptación (specs 06, 09 y 11).
- **RF-12.2** — Accesibilidad.
  - Axe en cada pantalla que recorre la E2E, sin violaciones *serious* ni *critical*.
  - Recorrido solo con teclado de los flujos críticos: registro, login, nueva solicitud, aceptar la cotización y enviar la cotización desde el backoffice.
  - Una revisión manual con lector de pantalla (NVDA o VoiceOver) de esos mismos flujos, registrada en el PR.
- **RF-12.3** — Rendimiento.
  - `useReportWebVitals` envía LCP, CLS, INP, FCP y TTFB a `POST /api/vitals` (route handler con un cuerpo de hasta 2 KB, sin datos personales), que los escribe en el log con la plantilla de la ruta.
  - Presupuestos de constitución §14: LCP < 2,5 s y CLS < 0,1 en `/` y `/marketplace` (móvil, p75), INP < 200 ms en el portal, y JS inicial de `/` y `/marketplace` de menos de 200 KB comprimido según la salida de `pnpm build`.
- **RF-12.4** — Contenedor.
  - `Dockerfile` en varias etapas (`node:22-alpine`, pnpm con `--frozen-lockfile`, `next build` con `output: 'standalone'`), que corre como usuario no root, expone `PORT`, tiene `HEALTHCHECK` sobre `/api/health` y no copia ningún `.env`.
  - `.dockerignore` excluye `node_modules`, `.next`, `.env*`, `e2e`, `coverage` y `.git`.
- **RF-12.5** — Integración continua. Un flujo de CI corre en cada PR: `pnpm install --frozen-lockfile`, `lint`, `typecheck`, `format:check`, las dos comprobaciones de constitución §15, `test`, `build`, `pnpm audit --prod` (alta o crítica falla) y la E2E contra el ambiente de pruebas en `main`. El despliegue a pruebas es automático desde `main`, y el de producción, por promoción manual (como `backend/14`).
- **RF-12.6** — Monitoreo y alertas. Los logs del front llegan al mismo destino que los del backend, unidos por el `requestId`. Alertas antes del go-live:
  - tasa de 5xx del front > 1 % en 5 minutos;
  - `/api/health` en 503 durante más de 2 minutos;
  - cualquier `CONTRACT_MISMATCH`, que significa que el front y la API se separaron;
  - `NETWORK_ERROR` hacia la API > 1 % en 5 minutos.
- **RF-12.7** — Dominio y salida de la landing anterior.
  - www.seglobal360.com y `seglobal360.com` (con redirección 308 a `www`) apuntan al proxy TLS del front.
  - El backend se configura con `APP_PUBLIC_URL=https://www.seglobal360.com`, `TRUSTED_PROXIES` con el CIDR del front y `CORS_ALLOWED_ORIGINS=https://www.seglobal360.com`.
  - Las URL públicas de la landing anterior (`/` y sus anclas) siguen funcionando, y las imágenes de Open Graph se mantienen.
  - Tras el cambio de DNS, el proyecto de Vercel de `global360_frontend` se retira y su repositorio se archiva.
- **RF-12.8** — Go-live. Antes de abrir el piloto, una checklist firmada en el PR de salida:
  - criterios de salida de F0–F6 cumplidos;
  - los **Pendientes con el backend** de `docs/tasks.md` resueltos o aceptados por escrito, y el consentimiento de datos del registro resuelto (bloqueante, spec 04);
  - textos legales publicados, número de WhatsApp y redes reales;
  - SMTP con SPF y DKIM verificado con un registro real;
  - política de comisión aprobada y responsable de Operaciones asignado;
  - alertas probadas;
  - plan de vuelta atrás (DNS de vuelta a la landing anterior durante 7 días).

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/api/vitals` | Público (solo `POST` desde la app) | — | RF-12.3 |
| Todas las pantallas de las specs 02 a 11 | Las de cada spec | Todos los `Mvp*` y `Portal*` | RF-12.1, RF-12.2 |

## 5. Contrato consumido

La E2E usa todas las rutas de las specs 02 a 11 por la interfaz, más la API directamente solo para preparar datos que no tienen pantalla en ese momento y para leer los emails de `tmp/mail/`. `GET /health` del backend lo usa `/api/health` (spec 00).

## 6. Estados y reglas de la interfaz

- La E2E no depende del orden de otras pruebas: cada corrida crea sus empresas, usuarios y servicios con sufijos únicos.
- Un fallo de axe o de un presupuesto bloquea el merge a `main`.

## 7. Componentes, datos y caché

- `src/shared/lib/web-vitals.ts` (Client Component del layout raíz con `useReportWebVitals`) y `src/app/api/vitals/route.ts`.
- `e2e/support/` con los helpers de API para preparar datos, de correo (`.eml`) y de axe.

## 8. Accesibilidad y SEO

- RF-12.2.
- Tras migrar el dominio, el sitemap se envía a Google Search Console y se verifica que `/` conserva su título, su descripción y su Open Graph.

## 9. Criterios de aceptación

- **CA-12.1** (RF-12.1) — La E2E de RF-12.1 termina en verde dos veces seguidas contra el ambiente de pruebas, y al final la empresa cliente figura como «Consolidado», con su fuente, en `/backoffice/clients`.
- **CA-12.2** (RF-12.2) — Axe no reporta violaciones *serious* ni *critical* en ninguna pantalla de la E2E; los cinco flujos críticos se completan solo con teclado (prueba de Playwright que usa solo `Tab`, `Shift+Tab`, `Enter`, `Espacio` y las flechas).
- **CA-12.3** (RF-12.3) — `POST /api/vitals` con un cuerpo de 3 KB responde 413 y con uno válido escribe una línea de log sin la URL completa; en el ambiente de pruebas, el p75 de LCP de `/` en móvil es < 2,5 s y el JS inicial de `/` cumple el presupuesto.
- **CA-12.4** (RF-12.4) — La imagen construida con el `Dockerfile` arranca con las variables del ambiente de pruebas, su `HEALTHCHECK` pasa a sano, el proceso corre con un usuario distinto de root y la imagen no contiene ningún archivo `.env`.
- **CA-12.5** (RF-12.5) — Un PR con un comentario de 3 líneas, una página privada sin `requireSession` o una dependencia con vulnerabilidad crítica hace fallar la CI.
- **CA-12.6** (RF-12.6) — Con la API apagada en pruebas, la alerta de `/api/health` se dispara en menos de 3 minutos; una respuesta de la API que no cumple su esquema genera un `CONTRACT_MISMATCH` que dispara su alerta.
- **CA-12.7** (RF-12.7) — En pruebas, con el dominio de ensayo: el login de un usuario deja en la auditoría del backend la IP real del navegador (no la del front), el rate limit del login es por IP real (dos navegadores con IP distinta no comparten cupo) y los enlaces de los emails apuntan al dominio del front. Las cookies de sesión llevan el prefijo `__Host-`, y toda respuesta trae CSP, HSTS y `frame-ancestors 'none'`.
- **CA-12.8** (RF-12.8) — El ensayo general en pruebas recorre la checklist de RF-12.8 punto por punto y deja constancia de cada uno; ningún pendiente con el backend queda sin resolver ni aceptar.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0130 | Ambiente de E2E en pruebas: backend con la semilla, buzón de `NOTIFIER=file` accesible, helpers de datos, de correo y de axe, y datos con sufijos únicos | ops | F6 | RF-12.1, RF-12.2 | G360F-0124, G360F-0114, G360F-0110 | `e2e/support/*.ts`, `playwright.config.ts`, infraestructura de pruebas |
| G360F-0131 | E2E de punta a punta del MVP por la interfaz | test | F6 | CA-12.1 | G360F-0130 | `e2e/mvp-end-to-end.spec.ts` |
| G360F-0132 | Barrido de axe y recorridos solo con teclado de los flujos críticos | test | F6 | CA-12.2 | G360F-0131 | `e2e/a11y.spec.ts`, `e2e/keyboard.spec.ts` |
| G360F-0133 | Web Vitals: `useReportWebVitals` y `POST /api/vitals` al log | impl | F6 | RF-12.3 | G360F-0014 | `src/shared/lib/web-vitals.ts`, `src/app/api/vitals/route.ts` |
| G360F-0134 | Verificación de los presupuestos de rendimiento y del límite de `/api/vitals` | test | F6 | CA-12.3 | G360F-0133, G360F-0050 | `src/app/api/vitals/route.test.ts`, `e2e/performance.spec.ts` |
| G360F-0135 | `Dockerfile` standalone no root con `HEALTHCHECK` y `.dockerignore` | ops | F6 | RF-12.4 | G360F-0014 | `Dockerfile`, `.dockerignore` |
| G360F-0136 | CI: lint, tipos, formato, comprobaciones de §15, tests, build, auditoría y E2E; despliegue a pruebas y promoción a producción | ops | F6 | RF-12.5 | G360F-0135, G360F-0005 | `.github/workflows/ci.yml`, `.github/workflows/deploy.yml` |
| G360F-0137 | Envío de logs y alertas del front (5xx, health, `CONTRACT_MISMATCH`, `NETWORK_ERROR`) | ops | F6 | RF-12.6 | G360F-0135 | Infraestructura (fuera del repositorio), `README.md` |
| G360F-0138 | Plan de migración del dominio, configuración del backend (`APP_PUBLIC_URL`, `TRUSTED_PROXIES`, `CORS_ALLOWED_ORIGINS`) y retiro de la landing anterior | ops | F6 | RF-12.7 | G360F-0135, G360F-0050 | Infraestructura, `README.md`, `../global360_frontend/README.md` |
| G360F-0139 | Ensayo general en pruebas: contenedor, CI, alertas, IP real y rate limit por IP, enlaces de emails, cookies y cabeceras, y checklist de go-live | test | F6 | CA-12.4, CA-12.5, CA-12.6, CA-12.7, CA-12.8 | G360F-0136, G360F-0137, G360F-0138, G360F-0132, G360F-0134, G360F-0129 | `e2e/deployment.spec.ts`, PR de ensayo |
| G360F-0140 | Salida a producción: cambio de DNS, piloto abierto y checklist de go-live firmada | ops | F6 | RF-12.7, RF-12.8 | G360F-0139 | Infraestructura, PR de salida |

## 11. Fuera de alcance y preguntas abiertas

- Varias instancias del front (escalado horizontal): fuera del MVP (constitución §6 y §11).
- Automatizar Lighthouse en la CI exige aprobar una dependencia nueva (`@lhci/cli`, constitución §1). Por defecto: los presupuestos se verifican con la E2E de rendimiento y una medición manual registrada en el PR.
- **Pregunta:** ¿dónde se envían los logs y cómo se definen las alertas (proveedor de infraestructura)? Por defecto: el mismo destino y el mismo sistema que el backend (`backend/14 §11`).
- **Pregunta:** ¿qué analítica de producto se usará al retirar Vercel Analytics? Por defecto: ninguna en el MVP, solo Web Vitals al log; añadir una es una enmienda (dependencia, CSP y aviso de cookies).
- **Backend/14** — No dice nada del frontend ni de dónde se despliega. Por defecto: el front va en un contenedor en la misma red que el backend, detrás del mismo proxy TLS, y la API no se expone a internet; se pide reflejarlo en `backend/14` junto con `TRUSTED_PROXIES` y `CORS_ALLOWED_ORIGINS` del front.
