# Spec 05 — Portal: inicio, cuenta, empresa y usuarios (`user`, `company`, `client`, `rbac`)

| | |
|---|---|
| Estado | Borrador |
| Features | `src/features/{user,company,client,rbac}`, `src/features/onboarding` (invitaciones), `src/app/(portal)` |
| Rutas | `/portal`, `/account`, `/company`, `/company/users` |
| Backend | `backend/03` (Implementada), `backend/04` (Implementada), `backend/07` (Implementada) |
| Depende de | Specs 00, 01 y 04 |

## 1. Resumen y alcance

Es la base del portal de empresa: el layout con el menú según los permisos, el inicio, la cuenta del usuario (F2), los datos de la empresa con su perfil comercial y la gestión de los usuarios de la empresa: invitar, activar, desactivar, bloquear y cambiar el rol (F3). Sirve a empresas `client`, `provider` y `both`; las secciones de solicitudes (spec 06) y de proveedor (spec 07) se enchufan al mismo layout y al mismo menú.

## 2. Origen

| Requisito | Fuente |
|---|---|
| Menú lateral: empresa y estado, «Nueva solicitud» con su motivo, secciones, usuario | Artboard `PortalNav` y nota `nota-portal-flujo` («Usuarios solo aparece con `user:manage`») |
| Inicio con saludo, aviso de empresa en validación y accesos | Artboard `PortalInicio` |
| Mi empresa: datos no editables, campos editables, perfil comercial, «Solo un administrador…» | Artboard `PortalEmpresa` y nota `nota-portal-cuenta` |
| Usuarios: invitar, estados, «Eres tú», «Esperando que acepte», roles Administrador/Operativo | Artboard `PortalUsuarios` y nota `nota-portal-cuenta` |
| Mi cuenta: datos personales, contraseña, «se cierra tu sesión en los demás dispositivos» | Artboard `PortalCuenta` y nota `nota-portal-cuenta` |
| Empresa, edición y estados | `backend/04 §4` (RF-04.2, RF-04.4) |
| Usuario actual, perfil, contraseña, listado y estados de usuarios | `backend/04 §4` (RF-04.6 a RF-04.8) |
| Perfil de cliente | `backend/07 §4` (RF-07.10) |
| Invitaciones | `backend/07 §4` (RF-07.5) |
| Roles, asignaciones, antiescalada | `backend/03 §4` y §5 (RF-03.3, RF-03.4, RF-03.6) |

## 3. Requisitos funcionales

- **RF-05.1** — Layout y menú del portal.
  - `(portal)/layout.tsx` obtiene, dentro de un `<Suspense>`, el usuario (`getCurrentUser`), sus grants y su empresa (`GET /companies/:cid`), y renderiza `PortalShell` (spec 01) con `LogoutButton` (spec 04). Un usuario interno que entra al portal es redirigido a `/backoffice`.
  - `src/app/(portal)/_nav.ts` construye el menú con `can`/`canIn` sobre la empresa del usuario: Inicio (`/portal`, siempre), Mi empresa (`/company`, `company:read`), Usuarios (`/company/users`, `user:manage`), Mi cuenta (`/account`, siempre) y Marketplace (`/marketplace`, siempre, en un grupo aparte). Las specs 06 y 07 añaden sus entradas en este mismo archivo.
  - Acción principal «Nueva solicitud» (la añade la spec 06): visible con `inquiry:create` en la empresa; deshabilitada con el motivo «Disponible cuando validemos tu empresa.» si la empresa no está `active`.
  - El encabezado del menú muestra la razón social (o el nombre comercial si existe) y el estado de la empresa con su etiqueta de §6.
- **RF-05.2** — Inicio `/portal`.
  - «Hola, [nombres]» y «Este es el resumen de tu empresa en Global 360.».
  - Aviso según el estado de la empresa: `pending_validation` → «Tu empresa está en validación. Ya puedes explorar el marketplace. Podrás crear solicitudes cuando Global 360 valide los datos de tu empresa; te avisaremos por correo.» con WhatsApp; `suspended` → «Tu empresa está suspendida. Escríbenos para conocer el motivo y reactivarla.»; `inactive` → «Tu empresa está inactiva.» con el motivo (`statusReason`) si existe.
  - Acceso «Explorar el marketplace». Los bloques de solicitudes y cotizaciones (spec 06) y de proveedor (spec 07) se añaden como secciones de esta página.
- **RF-05.3** — Mi cuenta `/account`.
  - Datos de solo lectura: correo de acceso. Formulario de nombres, apellidos y teléfono (`PATCH /users/me`), con «Guardar datos» y la confirmación en la misma página.
  - Cambio de contraseña: actual, nueva y confirmación. La Server Action llama a `POST /users/me/password`; con 204, como el backend invalida también la sesión actual en su siguiente renovación, vuelve a iniciar sesión con `signIn(email, nueva)` y muestra «Listo. Cerramos tu sesión en los demás dispositivos.». Si ese `signIn` falla, borra la sesión y lleva a `/login`.
  - `USER_CURRENT_PASSWORD_INVALID` va al campo de la contraseña actual; `USER_WEAK_PASSWORD`, al de la nueva.
- **RF-05.4** — Mi empresa `/company`.
  - Solo lectura: razón social, documento (tipo y número), país, tipo (Cliente, Proveedor o Ambos) y estado, con la nota «El documento y el país no se pueden cambiar. Para corregir la razón social, escríbele a tu asesor.».
  - Con `company:manage` en la empresa, formulario de nombre comercial, moneda de facturación (catálogo), correo y teléfono de contacto (`PATCH /companies/:id`; un campo vacío se envía como `""` para quitarlo). Sin el permiso, los mismos datos de solo lectura y «Solo un administrador de tu empresa puede editar estos datos.».
- **RF-05.5** — Perfil comercial (empresas `client` y `both`).
  - Sección «Perfil comercial — Ayuda a tu asesor a entender tu operación antes de cotizar.» con industria, sitio web (`https://`), envíos estimados al mes, descripción y productos principales (hasta 10, con `TagsInput`), sobre `GET` y `PATCH /clients/:id`.
  - Editable con `client:manage`; si no, solo lectura. Un `estimatedMonthlyShipments` ya informado no se puede vaciar (§11): el campo lo indica.
  - `TagsInput` (Client Component con entradas ocultas repetidas y respaldo de una entrada por línea sin JS) se añade a `shared/ui` y lo reutiliza la spec 07.
- **RF-05.6** — Usuarios `/company/users` (`requirePermission('user:manage', cid)`).
  - Tabla paginada de `GET /users?companyId=` con persona (iniciales y correo; ver §11), rol (de `GET /role-assignments?companyId=&status=active`, con su nombre visible de §6), estado y acciones.
  - Acciones según el estado: `active` → Desactivar y Bloquear; `inactive` → Activar y Bloquear; `blocked` → Desbloquear; `pending_verification` → «Esperando que acepte» y Bloquear. Bloquear pide el motivo con `ConfirmDialog` (obligatorio, hasta 500).
  - La fila propia muestra «Eres tú» y no ofrece Desactivar ni Bloquear.
- **RF-05.7** — Invitar a un usuario.
  - «Invitar usuario» abre un formulario (en `Dialog` o en la página) con nombres*, apellidos*, correo*, país del documento*, tipo de documento* (titular `person`), número* y rol* entre los **roles asignables**: los de `GET /roles?scope=company&status=active` cuyos permisos están todos entre los grants del usuario en su empresa (`assignableRoles` en `rbac/model.ts`), con su nombre visible y su descripción.
  - La Server Action llama a `POST /companies/:id/users`; con 201 muestra «Invitación enviada. La persona recibirá un correo para crear su contraseña.» y la fila nueva aparece como «Esperando que acepte».
- **RF-05.8** — Cambiar el rol.
  - Cada fila (salvo la propia) tiene un selector con los roles asignables. La Server Action asigna el nuevo (`POST /role-assignments {userId, roleId, companyId}`) y después revoca las asignaciones anteriores de ese usuario en la empresa (`POST /role-assignments/:id/revoke {reason: "Cambio de rol desde el portal"}`).
  - Si la asignación funciona y una revocación falla, muestra «[correo] quedó con los dos roles. Inténtalo de nuevo para quitar el anterior.» y la tabla refleja los dos.
  - `isLastManager` (`rbac/model.ts`) impide en la UI dejar a la empresa sin ningún usuario activo con `user:manage`: deshabilita Desactivar, Bloquear y el cambio de rol de ese usuario con el motivo «Tu empresa necesita al menos un administrador.».

## 4. Rutas y pantallas

| Ruta | Acceso | Artboard | RF |
|---|---|---|---|
| Layout de `(portal)` | Usuario de empresa | `PortalNav` | RF-05.1 |
| `/portal` | Usuario de empresa | `PortalInicio` | RF-05.2 |
| `/account` | Usuario de empresa | `PortalCuenta` | RF-05.3 |
| `/company` | `company:read` en su empresa | `PortalEmpresa` | RF-05.4, RF-05.5 |
| `/company/users` | `user:manage` en su empresa | `PortalUsuarios` | RF-05.6, RF-05.7, RF-05.8 |

## 5. Contrato consumido

| Endpoint | Backend | Uso |
|---|---|---|
| `GET /users/me`, `PATCH /users/me {firstName, lastName, phone}` | `backend/04 §4` | RF-05.2, RF-05.3 |
| `POST /users/me/password {currentPassword, newPassword}` → 204 | `backend/04 §4` | RF-05.3 |
| `POST /auth/login` (vía `signIn`) | `backend/05 §4` | Nuevo inicio de sesión tras el cambio de contraseña |
| `GET /companies/:id`, `PATCH /companies/:id {tradeName, billingCurrency, contactEmail, contactPhone}` | `backend/04 §4` | RF-05.1, RF-05.4 |
| `GET /clients/:id`, `PATCH /clients/:id {industry, website, description, mainProducts, estimatedMonthlyShipments}` | `backend/07 §4` | RF-05.5 |
| `GET /users?companyId=&status=&q=&page=&pageSize=` | `backend/04 §4` | RF-05.6 |
| `POST /users/:id/activate`, `/deactivate`, `/block {reason}`, `/unblock` | `backend/04 §4` | RF-05.6 |
| `POST /companies/:id/users {person, email, roleId}` → 201 | `backend/07 §4` | RF-05.7 |
| `GET /roles?scope=company&status=active` | `backend/03 §4` | RF-05.7, RF-05.8 |
| `GET /role-assignments?companyId=&status=active`, `POST /role-assignments`, `POST /role-assignments/:id/revoke {reason}` | `backend/03 §4` | RF-05.6, RF-05.8 |

| Código | Campo | Mensaje |
|---|---|---|
| `PERSON_NAME_REQUIRED` / `PERSON_PHONE_INVALID` | `firstName` / `phone` | Escribe nombres y apellidos (hasta 120) / revisa el teléfono. |
| `USER_CURRENT_PASSWORD_INVALID` | `currentPassword` | La contraseña actual no es correcta. |
| `USER_WEAK_PASSWORD` | `newPassword` | La contraseña debe tener entre 12 y 128 caracteres. |
| `COMPANY_TRADE_NAME_INVALID`, `COMPANY_CURRENCY_INVALID`, `COMPANY_EMAIL_INVALID`, `COMPANY_PHONE_INVALID` | el campo correspondiente | Revisa el dato (mismos textos que la spec 04). |
| `CLIENT_PROFILE_INVALID` | — | Revisa el perfil: el sitio web debe empezar por https:// y cada producto tiene hasta 80 caracteres. |
| `USER_SELF_ACTION_FORBIDDEN` | — | No puedes desactivarte ni bloquearte a ti mismo. |
| `USER_INVALID_STATUS_TRANSITION` | — | Este usuario ya cambió de estado. Recarga la página. |
| `USER_REASON_REQUIRED` | `reason` | Escribe el motivo del bloqueo. |
| `PERSON_ALREADY_EXISTS` | `person.documentNumber` | Ya existe una cuenta con este documento. |
| `USER_EMAIL_ALREADY_EXISTS` | `email` | Ya existe una cuenta con este correo. |
| `ROLE_ASSIGNMENT_ESCALATION` | `roleId` | No puedes asignar un rol con más permisos que los tuyos. |
| `ROLE_NOT_FOUND`, `ROLE_INACTIVE` | `roleId` | Ese rol ya no está disponible. Elige otro. |
| `ROLE_ASSIGNMENT_ALREADY_EXISTS` | — | Este usuario ya tiene ese rol. |
| `ROLE_ASSIGNMENT_USER_INVALID` | — | Solo se puede cambiar el rol de un usuario activo. |
| `COMPANY_NOT_FOUND` (al invitar) | — | Tu empresa no puede invitar usuarios en su estado actual. Escríbenos. |
| `USER_NOT_FOUND`, `CLIENT_NOT_FOUND` | — | `notFound()` |

## 6. Estados y reglas de la interfaz

| Estado de la empresa | Etiqueta | Tono |
|---|---|---|
| `pending_validation` | En validación | `warning` |
| `active` | Activa | `success` |
| `suspended` | Suspendida | `danger` |
| `inactive` | Inactiva | `neutral` |

| Estado del usuario | Etiqueta | Tono |
|---|---|---|
| `pending_verification` | Esperando que acepte | `info` |
| `active` | Activo | `success` |
| `inactive` | Inactivo | `neutral` |
| `blocked` | Bloqueado | `danger` |

- Tipo de empresa: `client` Cliente, `provider` Proveedor, `both` Cliente y proveedor.
- **Nombre visible de un rol:** su `description` si existe; si no, su `name`. El código nunca decide qué se muestra o se permite (constitución §6).
- Todo lo que depende de permisos se calcula con `canIn(grants, cid, perm)`; la API decide y su 403 o 404 se trata según constitución §4.

## 7. Componentes, datos y caché

- Lecturas privadas sin caché del servidor; el layout y las páginas comparten `getCurrentUser` y `getGrants` por request.
- Tras cada acción: `refresh()` para recargar los datos de la página.
- Componentes: `features/user/components/{ProfileForm,PasswordForm,UsersTable,UserStatusActions}.tsx`, `features/company/components/{CompanySummary,CompanyForm}.tsx`, `features/client/components/ClientProfileForm.tsx`, `features/onboarding/components/InviteUserForm.tsx`, `features/rbac/components/RoleSelect.tsx`, `shared/ui/TagsInput.tsx`.

## 8. Accesibilidad y SEO

- Las acciones de cada fila tienen nombres accesibles con la persona («Desactivar a ana@empresa.co»).
- Los cambios de estado se confirman con un `Alert` de `role="status"`.
- Todas las rutas son privadas: `noindex` y fuera del sitemap.

## 9. Criterios de aceptación

- **CA-05.1** (RF-05.1) — `_nav` con los grants de `client_admin` en su empresa devuelve Inicio, Mi empresa, Usuarios, Mi cuenta y Marketplace; con los de `client_operator`, lo mismo sin Usuarios; con un grant `user:manage` de **otra** empresa, sin Usuarios. Un usuario interno que abre `/portal` es redirigido a `/backoffice`. El encabezado muestra el nombre de la empresa y «En validación» para una empresa `pending_validation`.
- **CA-05.2** (RF-05.2) — Con la empresa `pending_validation`, `/portal` muestra el aviso de validación con WhatsApp; con `suspended`, el de suspensión; con `active`, ninguno. El saludo usa `person.firstName`.
- **CA-05.3** (RF-05.3) — La acción de contraseña, con 204 y un `signIn` stub correcto, guarda la sesión nueva y muestra el mensaje de RF-05.3; con `USER_CURRENT_PASSWORD_INVALID`, deja el error en el campo actual y no llama a `signIn`; si `signIn` falla, borra la sesión y redirige a `/login`. En la E2E, tras cambiar la contraseña, el usuario sigue navegando el portal sin volver a ingresar y la contraseña anterior ya no sirve en `/login`.
- **CA-05.4** (RF-05.4) — Un `client_admin` ve el formulario de `/company` y guarda el nombre comercial; un `client_operator` ve los datos de solo lectura y el aviso, sin formulario. Vaciar el teléfono envía `contactPhone: ""`. La acción nunca envía `legalName`, `countryId` ni el documento.
- **CA-05.5** (RF-05.5) — Una empresa `provider` no muestra la sección de perfil comercial. Con `mainProducts` de tres productos y uno vacío, la acción envía los tres recortados. `TagsInput` no admite un undécimo producto. Con `CLIENT_PROFILE_INVALID`, el mensaje de §5.
- **CA-05.6** (RF-05.6) — Un `client_operator` que abre `/company/users` recibe la página 403. Para un `client_admin`, la fila propia muestra «Eres tú» sin Desactivar ni Bloquear; un usuario `pending_verification` muestra «Esperando que acepte»; Bloquear sin motivo no envía; desactivar a un usuario activo lo deja «Inactivo».
- **CA-05.7** (RF-05.7) — `assignableRoles` con los grants de `client_admin` y los roles de la semilla devuelve los dos roles de cliente y no los de proveedor. Con `USER_EMAIL_ALREADY_EXISTS`, el error queda en el campo de correo. En la E2E, el `client_admin` invita a un operativo, la fila aparece como «Esperando que acepte», el invitado acepta con el flujo de la spec 04 y su fila pasa a «Activo».
- **CA-05.8** (RF-05.8) — Con una asignación correcta y una revocación que falla, la acción devuelve el aviso de los dos roles. `isLastManager` es verdadero para el único usuario activo con `user:manage` y deshabilita sus acciones; con dos administradores, es falso. En la E2E, cambiar a un operativo a administrador lo deja con un solo rol, y el menú de ese usuario muestra Usuarios al ingresar.

## 10. Tareas

| ID | Tarea | Tipo | Fase | Cubre | Depende de | Archivos |
|---|---|---|---|---|---|---|
| G360F-0061 | Features `user` (perfil propio, contraseña, listado y estados), `company` (lectura y listado) y `rbac` (permisos, roles y asignaciones): contratos, `api.ts` y mensajes; las reutiliza el backoffice (specs 08 y 09) | impl | F2 | RF-05.1, RF-05.3, RF-05.6, RF-05.8 | G360F-0011 | `src/features/user/{contracts,api,messages}.ts`, `src/features/company/{contracts,api,messages,model}.ts`, `src/features/rbac/{contracts,api,messages}.ts` |
| G360F-0062 | Layout del portal, `_nav.ts` por permisos e inicio `/portal` con los avisos de estado | impl | F2 | RF-05.1, RF-05.2 | G360F-0061, G360F-0025, G360F-0053 | `src/app/(portal)/{layout.tsx,_nav.ts,portal/page.tsx}`, `src/features/company/components/CompanyStatusNotice.tsx` |
| G360F-0063 | `/account`: datos personales y cambio de contraseña con nuevo inicio de sesión | impl | F2 | RF-05.3 | G360F-0061, G360F-0051 | `src/app/(portal)/account/page.tsx`, `src/features/user/{actions.ts,components/{ProfileForm,PasswordForm}.tsx}` |
| G360F-0064 | Tests del menú por permisos, de los avisos del inicio y de las acciones de la cuenta | test | F2 | CA-05.1, CA-05.2, CA-05.3 | G360F-0062, G360F-0063 | `src/app/(portal)/_nav.test.ts`, `src/features/{company,user}/**/*.test.ts(x)` |
| G360F-0065 | E2E del portal: menú según el rol, inicio y cambio de contraseña | test | F2 | CA-05.1, CA-05.2, CA-05.3 | G360F-0064, G360F-0055 | `e2e/portal-account.spec.ts` |
| G360F-0066 | `/company`: datos y edición por permiso, perfil comercial del cliente y `TagsInput` | impl | F3 | RF-05.4, RF-05.5 | G360F-0062 | `src/app/(portal)/company/page.tsx`, `src/features/company/{actions.ts,components/*}`, `src/features/client/*`, `src/shared/ui/TagsInput.tsx` |
| G360F-0067 | `/company/users`: listado con roles, estados y acciones por fila; modelo de `rbac` (`assignableRoles`, `isLastManager`) | impl | F3 | RF-05.6 | G360F-0062 | `src/app/(portal)/company/users/page.tsx`, `src/features/user/{actions.ts,components/{UsersTable,UserStatusActions}.tsx}`, `src/features/rbac/model.ts` |
| G360F-0068 | Invitar a un usuario con roles asignables | impl | F3 | RF-05.7 | G360F-0067, G360F-0056 | `src/features/onboarding/{api,actions}.ts`, `src/features/onboarding/components/InviteUserForm.tsx` |
| G360F-0069 | Cambiar el rol en dos llamadas, con aviso de fallo parcial y protección del último administrador | impl | F3 | RF-05.8 | G360F-0067 | `src/features/rbac/{actions.ts,components/RoleSelect.tsx}` |
| G360F-0070 | Tests de empresa, perfil comercial, estados de usuario, invitación, roles asignables, último administrador y cambio de rol | test | F3 | CA-05.4, CA-05.5, CA-05.6, CA-05.7, CA-05.8 | G360F-0066, G360F-0068, G360F-0069 | `src/features/{company,client,user,rbac,onboarding}/**/*.test.ts(x)` |
| G360F-0071 | E2E de empresa y usuarios: edición por permiso, invitación aceptada, cambio de rol y desactivación | test | F3 | CA-05.4, CA-05.6, CA-05.7, CA-05.8 | G360F-0070, G360F-0060 | `e2e/portal-company.spec.ts` |

## 11. Fuera de alcance y preguntas abiertas

- Avisos dentro de la plataforma y marcas de no leído: no hay en el MVP; todo aviso llega por correo (nota `nota-portal-huecos`, punto 4).
- Cambiar de empresa activa o pertenecer a varias: post-MVP.
- **Backend/04** — Un `client_admin` no puede ver los nombres de los usuarios de su empresa: `GET /users` solo trae `personId` y `GET /persons/:id` exige `person:read` global. Por defecto: la tabla muestra el correo y las iniciales sacadas del correo; se pide incluir `person{firstName, lastName}` en la respuesta de usuario o un permiso de lectura de personas por empresa.
- **Backend/04** — `GET /users/me` no trae el documento de la persona, y la maqueta de «Mi cuenta» lo muestra. Por defecto: «Mi cuenta» no muestra el documento.
- **Backend/03** — Los roles no tienen un nombre visible distinto de su código (`client_admin`). Por defecto: se muestra su `description`; se pide un `displayName` en el rol o una descripción en español en la semilla.
- **Backend/03** — Cambiar un rol son dos llamadas no atómicas, y nada impide dejar a una empresa sin administrador ni que uno se quite a sí mismo su rol. Por defecto: RF-05.8 (aviso de fallo parcial y `isLastManager` en la UI); se pide un endpoint de cambio de rol atómico y la protección del último administrador de empresa.
- **Backend/07** — `estimatedMonthlyShipments` no se puede vaciar una vez informado (`null` significa «no cambiar»). Por defecto: el campo lo indica y no admite vaciarse.
