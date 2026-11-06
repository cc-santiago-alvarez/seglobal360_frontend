# SEGlobal 360 — Frontend

Es la aplicación web de **SEGlobal 360**, la plataforma que conecta empresas que necesitan mover carga entre Colombia y Costa Rica con proveedores logísticos aprobados por Global 360. Reúne en un solo sitio:

- **El sitio público:** la landing con los servicios de Global 360 y el marketplace de proveedores y servicios, sin precios publicados.
- **El acceso:** registro de empresas, verificación del correo, ingreso y recuperación de la contraseña.
- **El portal de empresa:** los clientes piden cotizaciones, conversan con su asesor y aceptan la cotización en línea; los proveedores publican su perfil y sus servicios.
- **El backoffice:** el equipo de Global 360 valida empresas, publica proveedores, configura las rutas y sus comisiones y arma las cotizaciones.

Los datos y las reglas viven en el backend ([`global360_backend`](../global360_backend)), una API en Go. Este frontend, hecho con Next.js, muestra esa información y guarda la sesión de forma segura: el navegador nunca maneja los tokens de acceso.

Cuando salga a producción, reemplazará a la landing que hoy está publicada en www.seglobal360.com ([`global360_frontend`](../global360_frontend)).

## Estado

El proyecto está en la etapa de definición: hay reglas, specs y tareas, y todavía no hay código. El trabajo sigue el desarrollo guiado por specs (SDD):

- [`CLAUDE.md`](CLAUDE.md): las reglas del proyecto (la constitución).
- [`docs/specs/`](docs/specs): qué se construye, pantalla por pantalla.
- [`docs/tasks.md`](docs/tasks.md): las tareas en orden. Incluye los pendientes que hay que pedir al backend.

La primera tarea (`G360F-0001`, fase F0) prepara el proyecto de Next.js. Antes de instalar cada librería se avisa qué es y para qué sirve, y se explica cómo funciona.

## Cómo se levantará

Después de la fase F0, con Node.js 22 y pnpm 11, y con el backend corriendo en `http://localhost:5050`:

```bash
pnpm install
cp .env.example .env    # y completa API_BASE_URL, APP_PUBLIC_URL y el número de WhatsApp
pnpm dev                # http://localhost:3000
```

Para regenerar la lista de tareas después de cambiar una spec:

```bash
python3 docs/tools/gen_tasks.py docs
```
