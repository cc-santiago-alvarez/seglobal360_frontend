# Spec 04 — Registro y acceso (`auth`, `onboarding`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/auth`, `src/features/onboarding`, `src/app/(auth)` |
| Rutas | `/login`, `/register`, `/verify-email`, `/forgot-password`, `/reset-password`, `/accept-invitation` |
| Backend | `backend/05` (Implementada), `backend/07` (Implementada), `backend/04` (Implementada) |
| Depende de | Specs 00, 01 y 03 (cookie de adquisición) |

## 1. Resumen y alcance

Cubre la entrada y la salida de la plataforma: el login y el logout (F2), y el registro de una empresa con su administrador, la verificación del correo, el reenvío del enlace, la recuperación y el restablecimiento de la contraseña y la aceptación de una invitación (F3). Las tres páginas con token son las que enlazan los emails del backend (constitución, *Rutas que fija el backend*).

Las invitaciones se **envían** desde el portal (spec 05) y desde el backoffice (spec 08); aquí solo se **aceptan**.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Formulario de ingreso, error genérico, aviso de correo sin verificar con «reenvíalo» | Artboard `MvpLogin` y nota `nota-login` |
| Formulario de registro en tres bloques, tipo de empresa, términos, «Mínimo 12 caracteres», pasos 1-2-3 | Artboard `MvpRegistro` y nota `nota-registro` |
| Pantallas tras el registro, verificación correcta y enlace vencido | Artboard `MvpVerificacion` y nota `nota-verificacion` |
| Login, refresh, logout, `INVALID_CREDENTIALS` genérico, `EMAIL_NOT_VERIFIED`, bloqueo temporal | `backend/05 §4` (RF-05.1, RF-05.4) |
| `POST /registrations`, verificación, reenvío, recuperación, restablecimiento, invitaciones, anti-enumeración, vidas de los tokens | `backend/07 §4` y §5 (RF-07.1 a RF-07.4, RF-07.7) |
| Política de contraseña (12 a 128 caracteres) | `backend/04` (`USER_WEAK_PASSWORD`) |

## 3. Requisitos funcionales

- **RF-04.1** — Ingreso `/login`.
  - Formulario con correo y contraseña (`autocomplete="username"` y `"current-password"`), «¿Olvidaste tu contraseña?» y «Crear cuenta de empresa» (los dos conservan `next`).
  - La Server Action llama a `signIn` de `shared/auth` (spec 00: `POST /auth/login` y `setSession`) y redirige a `next` si es una ruta relativa válida; si no, según el claim `cid` del access token: vacío (personal interno) → `/backoffice`, con empresa → `/portal`. Un `next` de backoffice para un usuario de empresa (o al revés) se ignora.
  - `INVALID_CREDENTIALS` muestra «El correo o la contraseña no son correctos.» sin señalar un campo (cubre también el usuario bloqueado y el bloqueo temporal, a propósito). `EMAIL_NOT_VERIFIED` muestra el aviso «Aún no has verificado tu correo» con el reenvío de RF-04.5. `RATE_LIMITED`, el texto transversal.
  - La contraseña nunca vuelve en el `ActionState`; el correo sí, para no tener que escribirlo de nuevo.
- **RF-04.2** — Salida. `LogoutButton` (en los shells del portal y del backoffice) envía una Server Action que llama a `signOut` de `shared/auth` (`POST /auth/logout {refreshToken}`, ignora su resultado y borra las cookies) y redirige a `/`.
- **RF-04.3** — Registro `/register`.
  - Tipo de empresa con `RadioCardGroup`: Cliente («Solicitar cotizaciones para mover mi carga»), Proveedor («Publicar mis servicios logísticos») y Ambos; `?type=provider` lo preselecciona. Por defecto, Cliente.
  - **Datos de la empresa:** razón social*, nombre comercial, país*, tipo de documento* (los de ese país con titular `company`), número de documento*, moneda de facturación*, correo y teléfono de contacto.
  - **Tus datos** (el administrador de la cuenta): nombres*, apellidos*, país del documento*, tipo de documento* (titular `person`), número*, teléfono.
  - **Acceso:** correo*, contraseña* («Mínimo 12 caracteres») y confirmación* (comprobación propia del front, constitución §5).
  - **Consentimiento:** casilla obligatoria «Acepto los términos y condiciones y la política de tratamiento de datos personales de Global 360», con enlaces a `/legal/terms` y `/legal/privacy` (spec 03).
  - Los tipos de documento de todos los países activos se cargan con la página y un Client Component filtra las opciones al cambiar el país; sin JS, se muestran agrupados por país.
  - La Server Action construye el cuerpo exacto de `backend/07 §4` (`company`, `person`, `account`, `acquisition` desde la cookie `g360_acq`), sin la confirmación ni la casilla, y llama a `POST /registrations`. Con 201, la misma página muestra el panel «Revisa tu correo» con el correo registrado y el reenvío (RF-04.5); el correo no va en la URL.
  - Cada código de error de `backend/07 §4` se muestra en su campo según la tabla de §5.
- **RF-04.4** — Verificación `/verify-email?token=`.
  - La página no llama a la API al renderizar. Un Client Component envía el token con una Server Action al montarse (con un botón «Confirmar mi correo» si no hay JS) y después lo quita de la URL con `history.replaceState`.
  - 204: «Correo verificado. Tu empresa está en validación. Te avisaremos por correo cuando Global 360 la habilite para solicitar cotizaciones. Mientras tanto ya puedes ingresar y explorar el marketplace.», con «Ingresar», «Explorar el marketplace» y WhatsApp.
  - `ACTION_TOKEN_INVALID` (o sin token): «Este enlace ya no sirve. Pide uno nuevo con el correo con el que registraste tu empresa.» con el formulario de reenvío. `USER_INVALID_STATUS_TRANSITION`: «Tu correo ya está verificado o tu cuenta no está activa. Intenta ingresar.» con «Ingresar».
- **RF-04.5** — Reenvío del enlace de verificación. `ResendVerificationForm` (correo) llama a `POST /auth/verify-email/resend` y **siempre** muestra «Si el correo está registrado y sin verificar, te enviamos un nuevo enlace.», también con `INVALID_BODY`. Se usa en el panel posterior al registro, en `/verify-email` con enlace inválido y en el aviso `EMAIL_NOT_VERIFIED` del login (con el correo ya escrito).
- **RF-04.6** — Recuperación `/forgot-password`. Formulario con el correo que llama a `POST /auth/password/forgot` y siempre muestra «Si el correo corresponde a una cuenta activa, te enviamos un enlace para crear una nueva contraseña. Vence en 1 hora.»
- **RF-04.7** — Restablecimiento `/reset-password?token=`.
  - La página lee el token, se lo pasa al formulario y lo quita de la URL al montarse.
  - Formulario con la contraseña nueva y su confirmación; la Server Action llama a `POST /auth/password/reset {token, newPassword}`. 204: «Listo, tu contraseña se actualizó.» con «Ingresar» (las sesiones anteriores se cierran solas).
  - `USER_WEAK_PASSWORD` va al campo y permite reintentar con el mismo enlace. `ACTION_TOKEN_INVALID`: «El enlace venció o ya se usó.» con un enlace a `/forgot-password`.
- **RF-04.8** — Invitación `/accept-invitation?token=`.
  - Igual que RF-04.7, con el título «Crea tu contraseña para entrar a Global 360» y la Server Action `POST /auth/invitations/accept {token, password}`.
  - 204: «Tu cuenta está lista.» con «Ingresar». `ACTION_TOKEN_INVALID`: «La invitación venció o ya se usó. Pide a quien te invitó que te escriba o recupera tu contraseña.» `USER_INVALID_STATUS_TRANSITION`: «Tu cuenta ya está activa: ingresa o recupera tu contraseña.»
- **RF-04.9** — Sesión ya iniciada. `/login` y `/register` con una sesión válida (`getCurrentUser` no nulo) redirigen al inicio del usuario (`/portal` o `/backoffice`). Las páginas con token funcionan con o sin sesión.

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| `/login?next=` | Público | `MvpLogin` | RF-04.1, RF-04.5, RF-04.9 |
| `/register?type=&next=` | Público | `MvpRegistro`, `MvpVerificacion` (paso 1) | RF-04.3, RF-04.5, RF-04.9 |
| `/verify-email?token=` | Público (enlace del email) | `MvpVerificacion` (pasos 2 y 3) | RF-04.4, RF-04.5 |
| `/forgot-password` | Público | — | RF-04.6 |
| `/reset-password?token=` | Público (enlace del email) | — | RF-04.7 |
| `/accept-invitation?token=` | Público (enlace del email) | — | RF-04.8 |
| Botón «Salir» (portal y backoffice) | Con sesión | `PortalNav` | RF-04.2 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `POST /auth/login {email, password}` → `{accessToken, refreshToken, tokenType, expiresIn}` | `backend/05 §4` | RF-04.1 |
| `POST /auth/logout {refreshToken}` → 204 | `backend/05 §4` | RF-04.2 |
| `POST /registrations {company, person, account, acquisition}` → 201 `{companyId, userId, companyStatus, userStatus}` | `backend/07 §4` | RF-04.3 |
| `POST /auth/verify-email {token}` → 204 | `backend/07 §4` | RF-04.4 |
| `POST /auth/verify-email/resend {email}` → 204 | `backend/07 §4` | RF-04.5 |
| `POST /auth/password/forgot {email}` → 204 | `backend/07 §4` | RF-04.6 |
| `POST /auth/password/reset {token, newPassword}` → 204 | `backend/07 §4` | RF-04.7 |
| `POST /auth/invitations/accept {token, password}` → 204 | `backend/07 §4` | RF-04.8 |
| `GET /countries`, `/currencies`, `/document-types?countryId=&holder=` | `backend/02 §4` | Opciones del registro (feature `catalog`) |

| Código | Campo | Mensaje |
|---|---|---|
| `INVALID_CREDENTIALS` | — | El correo o la contraseña no son correctos. |
| `EMAIL_NOT_VERIFIED` | — | Aún no has verificado tu correo. Abre el enlace que te enviamos o reenvíalo. |
| `COMPANY_LEGAL_NAME_REQUIRED` | `company.legalName` | Escribe la razón social (hasta 200 caracteres). |
| `COMPANY_TRADE_NAME_INVALID` | `company.tradeName` | El nombre comercial admite hasta 200 caracteres. |
| `COMPANY_COUNTRY_INVALID` | `company.countryId` | Elige un país de la lista. |
| `COMPANY_DOCUMENT_TYPE_INVALID` | `company.documentTypeCode` | Elige un tipo de documento de empresa de ese país. |
| `COMPANY_DOCUMENT_NUMBER_INVALID` | `company.documentNumber` | Revisa el número de documento: no tiene el formato esperado. |
| `COMPANY_CURRENCY_INVALID` | `company.billingCurrency` | Elige una moneda de la lista. |
| `COMPANY_TYPE_INVALID` | `company.companyType` | Elige qué quieres hacer en Global 360. |
| `COMPANY_EMAIL_INVALID` / `COMPANY_PHONE_INVALID` | `company.contactEmail` / `company.contactPhone` | Revisa el correo / el teléfono (solo dígitos, con indicativo, de 7 a 15). |
| `COMPANY_ALREADY_EXISTS` | `company.documentNumber` | Ya hay una empresa registrada con este documento. Si es la tuya, escríbenos por WhatsApp. |
| `PERSON_NAME_REQUIRED` | `person.firstName` | Escribe tus nombres y apellidos (hasta 120 caracteres). |
| `PERSON_DOCUMENT_TYPE_INVALID` / `PERSON_DOCUMENT_NUMBER_INVALID` | `person.documentTypeCode` / `person.documentNumber` | Elige un tipo de documento personal de ese país / revisa el número. |
| `PERSON_PHONE_INVALID` | `person.phone` | Revisa el teléfono (solo dígitos, con indicativo, de 7 a 15). |
| `PERSON_EMAIL_INVALID`, `USER_EMAIL_INVALID` | `account.email` | Revisa el correo. |
| `PERSON_ALREADY_EXISTS` | `person.documentNumber` | Ya hay una cuenta con este documento. Ingresa o recupera tu contraseña. |
| `USER_EMAIL_ALREADY_EXISTS` | `account.email` | Ya hay una cuenta con este correo. Ingresa o recupera tu contraseña. |
| `USER_WEAK_PASSWORD` | `account.password` / `newPassword` / `password` | La contraseña debe tener entre 12 y 128 caracteres. |
| `CLIENT_PROFILE_INVALID` | — | No pudimos guardar el origen de tu visita. Inténtalo de nuevo. |
| `ACTION_TOKEN_INVALID` | — | Según la página (RF-04.4, RF-04.7, RF-04.8). |
| `USER_INVALID_STATUS_TRANSITION` | — | Según la página (RF-04.4, RF-04.8). |

## 6. Estados y reglas de la interfaz

- El registro muestra a la derecha (escritorio) o arriba (móvil) los tres pasos «Completa el formulario → Verifica tu correo → Validamos tu empresa» con el `Stepper`.
- Un envío fallido conserva todo lo escrito salvo las contraseñas.
- Los mensajes de reenvío y de recuperación son siempre los mismos, haya o no cuenta (`backend/07`, anti-enumeración).

## 7. Componentes, datos y caché

- `shared/auth`: `signIn` y `signOut` (spec 00). `features/auth`: `api.ts` (verificación, reenvío, recuperación, restablecimiento, invitación), `actions.ts`, `messages.ts`, `components/{LoginForm,LogoutButton,ResendVerificationForm,VerifyEmail,ForgotPasswordForm,SetPasswordForm}.tsx`. `SetPasswordForm` sirve a RF-04.7 y RF-04.8.
- `features/onboarding`: `contracts.ts` (cuerpo de `POST /registrations` y sus límites), `api.ts`, `actions.ts`, `messages.ts`, `components/RegisterForm.tsx`.
- Las páginas usan `AuthLayout` (spec 01). Nada se cachea; las opciones del registro salen de los catálogos públicos en caché.

## 8. Accesibilidad y SEO

- Cada formulario tiene un `<h1>`, etiquetas visibles, `autocomplete` correcto (`email`, `new-password`, `given-name`, `family-name`, `organization`, `tel`) y `FormErrorSummary`.
- `/login` y `/register` se indexan; las páginas con token y `/forgot-password` llevan `noindex` y `Referrer-Policy: no-referrer`.

## 9. Criterios de aceptación

- **CA-04.1** (RF-04.1) — Con un `api` stub que devuelve un par cuyo `cid` está vacío, la acción de login guarda las cookies y redirige a `/backoffice`; con `cid` presente, a `/portal`; con `next=/inquiries/new?serviceId=x`, a esa ruta; con `next=https://evil.co` o `//evil.co`, al inicio del usuario. `INVALID_CREDENTIALS` devuelve el mensaje genérico sin campo y sin la contraseña; `EMAIL_NOT_VERIFIED` devuelve el aviso con el correo escrito. En la E2E, el superadmin de la semilla entra y llega a `/backoffice`.
- **CA-04.2** (RF-04.2) — La acción de salir borra las dos cookies y redirige a `/` aunque `POST /auth/logout` falle con `NETWORK_ERROR`. En la E2E, después de salir, `/portal` redirige a `/login?next=%2Fportal`.
- **CA-04.3** (RF-04.3) — La acción de registro envía exactamente `company`, `person`, `account` y `acquisition` (desde `g360_acq`), sin la confirmación ni la casilla, y no llama a la API si la confirmación no coincide o la casilla no está marcada. Con `USER_EMAIL_ALREADY_EXISTS` el error queda en `account.email`; con `COMPANY_ALREADY_EXISTS`, en `company.documentNumber`. Al cambiar el país a Costa Rica, el tipo de documento de empresa ofrece `CJ` y no `NIT`. En la E2E, un registro correcto muestra «Revisa tu correo» con el correo escrito y deja un `.eml` de `email_verification` en `tmp/mail/`.
- **CA-04.4** (RF-04.4) — El render de `/verify-email?token=abc` no llama a la API; la llamada ocurre al montarse y, después, la URL ya no tiene `token`. En la E2E, el enlace del `.eml` verifica el correo y muestra «Correo verificado»; abrirlo otra vez muestra «Este enlace ya no sirve» con el reenvío.
- **CA-04.5** (RF-04.5) — El reenvío muestra el mismo mensaje con un correo registrado sin verificar, con uno inexistente y con uno ya verificado. En el login de un usuario sin verificar, el aviso trae el formulario de reenvío con el correo ya escrito.
- **CA-04.6** (RF-04.6) — `/forgot-password` muestra el mismo mensaje con un correo existente y con uno inexistente; en la E2E, solo el existente deja un `.eml` de `password_reset`.
- **CA-04.7** (RF-04.7) — Con una contraseña de 11 caracteres, el error queda en el campo y un segundo envío con el mismo enlace y una contraseña válida termina en «Listo, tu contraseña se actualizó.»; reutilizar el enlace muestra «El enlace venció o ya se usó.» con el enlace a `/forgot-password`. La URL deja de mostrar el token al cargar.
- **CA-04.8** (RF-04.8) — En la E2E, un usuario invitado (creado por API) abre el enlace del `.eml` de `user_invitation`, crea su contraseña, ve «Tu cuenta está lista.» e ingresa; abrir otra vez la invitación muestra el mensaje de `ACTION_TOKEN_INVALID`.
- **CA-04.9** (RF-04.9) — Con una sesión de un usuario de empresa, `/login` y `/register` redirigen a `/portal`; con la de un usuario interno, a `/backoffice`; `/verify-email` se muestra igual con o sin sesión.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0051 | `signIn` y `signOut` en `shared/auth`, y feature `auth` con sus contratos y mensajes | impl | F2 | RF-04.1, RF-04.2 | G360F-0009, G360F-0011 | `src/shared/auth/sign-in.ts`, `src/features/auth/{contracts,messages}.ts` |
| G360F-0052 | `/login`: formulario, acción con redirección por `cid` y `next`, y redirección con sesión ya iniciada | impl | F2 | RF-04.1, RF-04.9 | G360F-0051, G360F-0024 | `src/app/(auth)/login/page.tsx`, `src/features/auth/{actions.ts,components/LoginForm.tsx}` |
| G360F-0053 | `LogoutButton` y su acción, conectado en los shells del portal y del backoffice | impl | F2 | RF-04.2 | G360F-0051, G360F-0025, G360F-0026 | `src/features/auth/components/LogoutButton.tsx`, `src/features/auth/actions.ts` |
| G360F-0054 | Tests de las acciones de login y logout (redirecciones, `next`, errores, cookies) | test | F2 | CA-04.1, CA-04.2, CA-04.9 | G360F-0052, G360F-0053 | `src/features/auth/actions.test.ts` |
| G360F-0055 | E2E de login y logout con el superadmin de la semilla y con un usuario de empresa | test | F2 | CA-04.1, CA-04.2, CA-04.9 | G360F-0054 | `e2e/auth.spec.ts` |
| G360F-0056 | Feature `onboarding` y `/register`: formulario por bloques, tipos de documento por país, consentimiento, acción y panel «Revisa tu correo» | impl | F3 | RF-04.3 | G360F-0052, G360F-0044 | `src/features/onboarding/*`, `src/app/(auth)/register/page.tsx` |
| G360F-0057 | `/verify-email` con envío al montar y `ResendVerificationForm` (también en el login) | impl | F3 | RF-04.4, RF-04.5 | G360F-0052 | `src/app/(auth)/verify-email/page.tsx`, `src/features/auth/components/{VerifyEmail,ResendVerificationForm}.tsx` |
| G360F-0058 | `/forgot-password`, `/reset-password` y `/accept-invitation` con `SetPasswordForm` | impl | F3 | RF-04.6, RF-04.7, RF-04.8 | G360F-0057 | `src/app/(auth)/{forgot-password,reset-password,accept-invitation}/page.tsx`, `src/features/auth/components/{ForgotPasswordForm,SetPasswordForm}.tsx` |
| G360F-0059 | Tests de las acciones de registro (cuerpo, adquisición, confirmación, mapeo de códigos) y de las páginas con token | test | F3 | CA-04.3, CA-04.4, CA-04.5, CA-04.6, CA-04.7, CA-04.8 | G360F-0056, G360F-0058 | `src/features/onboarding/*.test.ts`, `src/features/auth/*.test.ts(x)` |
| G360F-0060 | E2E de registro → verificación → login, recuperación → restablecimiento e invitación, leyendo los `.eml` de `tmp/mail/` | test | F3 | CA-04.3, CA-04.4, CA-04.5, CA-04.6, CA-04.7, CA-04.8 | G360F-0059 | `e2e/registration.spec.ts`, `e2e/password.spec.ts`, `e2e/support/mail.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Captcha en el registro: no hay en el MVP (`backend/07 §11`); el límite es el rate limit por IP del backend.
- MFA en el login: F11. Login con Google o Microsoft: no pedido.
- Pertenecer a varias empresas y cambiar de empresa activa: post-MVP (`backend/07 §11`).
- **Pregunta:** ¿se avisa al usuario de que su cuenta quedó bloqueada temporalmente? El backend responde `INVALID_CREDENTIALS` también en ese caso. Por defecto: no se distingue.
- **Backend/07** — `POST /registrations` no recibe la aceptación de los términos ni de la política de datos (un campo extra responde `INVALID_BODY`), y la ley de protección de datos exige poder probar la autorización (fecha y versión del texto aceptado). **Bloquea el go-live (F6).** Por defecto: la casilla es obligatoria en el formulario y no se envía; se pide añadir `consents: [{document, version}]` al registro y a la aceptación de invitaciones.
- **Backend/07** — Un email perdido no se puede reenviar en el caso de una invitación: reinvitar responde `PERSON_ALREADY_EXISTS`. Por defecto: `/accept-invitation` con enlace vencido remite a «Recuperar contraseña», que funciona después de verificar el correo con el reenvío.
