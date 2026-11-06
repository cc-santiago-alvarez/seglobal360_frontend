#!/usr/bin/env python3
"""Genera docs/tasks.md a partir de las specs del frontend y valida la trazabilidad (constitución §17).

Uso:
    python3 docs/tools/gen_tasks.py docs              # valida y regenera docs/tasks.md
    python3 docs/tools/gen_tasks.py docs --renumber   # compacta los IDs en orden secuencial por spec

Las casillas marcadas a mano en docs/tasks.md (`- [x] **G360F-xxxx**`) se conservan al regenerar.
--renumber solo se permite mientras no haya ninguna casilla marcada: después, los IDs son tickets de commits.
"""
import os
import re
import sys
from pathlib import Path

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
RENUMBER = '--renumber' in sys.argv[1:]
DOCS = Path(ARGS[0] if ARGS else 'docs')
SPECS = sorted((DOCS / 'specs').glob('*.spec.md'))
OUT = DOCS / 'tasks.md'
CLAUDE_MD = DOCS.parent / 'CLAUDE.md'
SELF = Path(__file__).resolve()

RF_DEF = re.compile(r'^- \*\*(RF-(\d\d)\.\d+)\*\*')
CA_DEF = re.compile(r'^- \*\*(CA-(\d\d)\.\d+)\*\* \(([^)]*)\)')
ID_RE = re.compile(r'(RF-\d\d\.\d+|CA-\d\d\.\d+)')
RF_RE = re.compile(r'RF-\d\d\.\d+')
PREFIX = 'G360F-'
TASK_RE = re.compile(re.escape(PREFIX) + r'\d{4}')
STATUS_RE = re.compile(r'^\| Estado \| (.+?) \|$')
DONE_RE = re.compile(r'^- \[x\] \*\*(' + re.escape(PREFIX) + r'\d{4})\*\*', re.IGNORECASE)
BACKEND_RE = re.compile(r'^- \*\*Backend/(\d\d)\*\* — (.+)$')

# Épicas post-MVP: (fase, ID, título, depende de). Cada una exige escribir y aprobar su spec antes del código.
# Cada una se desbloquea con la épica de la misma fase del backend.
EXTRA = [
    ('F7', 'G360F-0141', 'Spec y desarrollo del **seguimiento de órdenes y envíos** para el cliente (hitos e historial) y de su gestión por Operaciones en el backoffice', ['G360F-0140']),
    ('F8', 'G360F-0142', 'Spec y desarrollo de **documentos**: carga con progreso, versiones y descarga por orden y envío; logo y documentos del proveedor', ['G360F-0140']),
    ('F9', 'G360F-0143', 'Spec y desarrollo de **pagos**: checkout con la pasarela, estado de pagos, facturas y reembolsos para el cliente; conciliación en el backoffice', ['G360F-0140']),
    ('F10', 'G360F-0144', 'Spec y desarrollo del **formulario público de leads** y de la medición de campañas de punta a punta', ['G360F-0140']),
    ('F11', 'G360F-0145', 'MFA en el acceso de los roles administrativos y backoffice ampliado (Personal, Legal, Tecnología, reportes financieros)', ['G360F-0140']),
    ('F12', 'G360F-0146', 'Sitio y portal en inglés (i18n), WhatsApp y mensajería en tiempo real en la conversación de la solicitud', ['G360F-0140']),
]

PHASES = [
    ('F0', 'Preparación del repositorio (spec 00)', 'El esqueleto de Next compila y pasan `pnpm lint`, `pnpm typecheck`, `pnpm test` y `pnpm build`.', True),
    ('F1', 'Plataforma base, sistema de diseño y landing migrada (specs 00, 01 y 03)', 'El front arranca con la configuración validada, llama a la API de desarrollo con request-id y errores uniformes, el kit y los layouts existen y la landing actual está migrada.', True),
    ('F2', 'Fundación: acceso, portal y backoffice básico (specs 04, 05, 08 y 09)', 'Login funcional con roles: un usuario entra, ve el menú según sus permisos, la sesión se renueva sin que lo note y sale; el superadmin gestiona catálogos, roles, empresas y usuarios desde el backoffice.', True),
    ('F3', 'Clientes y proveedores (specs 04, 05, 07, 08 y 09)', 'Una empresa se registra, verifica su correo y Global 360 la valida desde el backoffice; un proveedor completa su perfil, es aprobado y publicado y publica un servicio; el administrador de la empresa gestiona sus datos y sus usuarios.', True),
    ('F4', 'Corredor y marketplace (specs 02, 03 y 09)', 'La landing muestra rutas y proveedores reales, el marketplace lista y filtra servicios y proveedores, y el backoffice activa CO↔CR con su regla de comisión.', True),
    ('F5', 'Solicitud y cotización (specs 06 y 10)', 'Un cliente crea una solicitud desde el marketplace, el asesor la toma y conversa con él, le envía la cotización y el cliente la acepta en línea.', True),
    ('F6', 'Backoffice y salida a producción (specs 11 y 12)', 'Bandeja y reportes del backoffice, E2E de interfaz y axe en verde, presupuestos de rendimiento cumplidos y dominio migrado: **MVP en producción**.', True),
    ('F7', 'Órdenes y operación logística', 'El cliente sigue sus órdenes y envíos con sus hitos, y Operaciones los gestiona desde el backoffice.', False),
    ('F8', 'Documentos', 'Documentos cargados, versionados y descargables por orden y envío; logo y documentos del proveedor.', False),
    ('F9', 'Pagos y liquidaciones', 'Checkout con la pasarela, estado de pagos y facturas para el cliente, y conciliación en el backoffice.', False),
    ('F10', 'CRM y adquisición', 'Leads y campañas medidos de punta a punta.', False),
    ('F11', 'Backoffice ampliado y seguridad', 'MFA para los administradores y módulos internos ampliados.', False),
    ('F12', 'Escalamiento e integraciones', 'Sitio y portal en inglés, WhatsApp y mensajería en tiempo real.', False),
]
PHASE_CODES = [p[0] for p in PHASES]
MVP_PHASES = {p[0] for p in PHASES if p[3]}


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


specs, tasks, PHASE_OF, rfs, cas = {}, {}, {}, {}, {}
backend_items = []
errors = []

for path in SPECS:
    num = path.name[:2]
    text = path.read_text(encoding='utf-8')
    specs[num] = {'file': path.name, 'title': text.splitlines()[0].lstrip('# ').strip(), 'status': '—'}
    section = None
    for line in text.splitlines():
        if line.startswith('## '):
            section = line
        m = STATUS_RE.match(line)
        if m and specs[num]['status'] == '—':
            specs[num]['status'] = m.group(1)
        m = RF_DEF.match(line)
        if m:
            if m.group(1) in rfs:
                errors.append(f'{m.group(1)}: RF duplicado')
            if m.group(2) != num:
                errors.append(f'{m.group(1)}: definido en la spec {num}')
            rfs[m.group(1)] = num
        m = CA_DEF.match(line)
        if m:
            if m.group(1) in cas:
                errors.append(f'{m.group(1)}: CA duplicado')
            if m.group(2) != num:
                errors.append(f'{m.group(1)}: definido en la spec {num}')
            cas[m.group(1)] = RF_RE.findall(m.group(3))
        m = BACKEND_RE.match(line)
        if m:
            backend_items.append((num, m.group(1), m.group(2)))
        if line.startswith('| ' + PREFIX) and section and 'Tareas' in section:
            c = cells(line)
            if len(c) != 7:
                errors.append(f'{c[0]}: la fila de la tabla Tareas no tiene 7 columnas ({path.name})')
                continue
            if c[0] in tasks:
                errors.append(f'{c[0]}: ID duplicado')
            tasks[c[0]] = {'id': c[0], 'title': c[1], 'type': c[2], 'covers': ID_RE.findall(c[4]),
                           'deps': TASK_RE.findall(c[5]), 'files': c[6], 'spec': num,
                           'row': sum(1 for t in tasks.values() if t['spec'] == num)}
            PHASE_OF[c[0]] = c[3]

for phase, tid, title, deps in EXTRA:
    if tid in tasks:
        errors.append(f'{tid}: ID duplicado')
    tasks[tid] = {'id': tid, 'title': title, 'type': 'epic', 'covers': [], 'deps': deps,
                  'files': 'spec por escribir', 'spec': None}
    PHASE_OF[tid] = phase

# ---------- validaciones (constitución §17) ----------
for tid, t in tasks.items():
    phase = PHASE_OF[tid]
    if phase not in PHASE_CODES:
        errors.append(f'{tid}: fase inválida {phase!r}')
        continue
    if t['spec'] and t['type'] not in ('impl', 'test', 'ops'):
        errors.append(f'{tid}: tipo inválido {t["type"]!r} (en una spec solo impl, test u ops)')
    if t['type'] == 'epic' and phase in MVP_PHASES:
        errors.append(f'{tid}: una épica no puede estar en una fase del MVP ({phase})')
    for c in t['covers']:
        if c.startswith('RF') and c not in rfs:
            errors.append(f'{tid}: RF inexistente {c}')
        if c.startswith('CA') and c not in cas:
            errors.append(f'{tid}: CA inexistente {c}')
    if t['type'] in ('impl', 'ops') and not any(c.startswith('RF') for c in t['covers']):
        errors.append(f'{tid}: tarea {t["type"]} sin RF')
    if t['type'] == 'test' and not any(c.startswith('CA') for c in t['covers']):
        errors.append(f'{tid}: tarea test sin CA')
    for d in t['deps']:
        if d not in tasks:
            errors.append(f'{tid}: dependencia inexistente {d}')
        elif PHASE_OF[d] in PHASE_CODES and PHASE_CODES.index(PHASE_OF[d]) > PHASE_CODES.index(phase):
            errors.append(f'{tid} ({phase}) depende de {d} ({PHASE_OF[d]}), que es de una fase posterior')

for ca, refs in cas.items():
    if not refs:
        errors.append(f'{ca}: no cita ningún RF')
    for r in refs:
        if r not in rfs:
            errors.append(f'{ca}: cita {r}, que no existe')
        elif r[3:5] != ca[3:5]:
            errors.append(f'{ca}: cita {r}, de otra spec')

rf_impl = {rf: [] for rf in rfs}
rf_test = {rf: [] for rf in rfs}
rf_ca = {rf: [] for rf in rfs}
for ca, refs in cas.items():
    for r in refs:
        if r in rf_ca:
            rf_ca[r].append(ca)
tested_cas = set()
for tid, t in tasks.items():
    for c in t['covers']:
        if c in rfs and t['type'] in ('impl', 'ops'):
            rf_impl[c].append(tid)
        if c in cas and t['type'] == 'test':
            tested_cas.add(c)
            for r in cas[c]:
                if r in rf_test and tid not in rf_test[r]:
                    rf_test[r].append(tid)
for rf in rfs:
    if not rf_impl[rf]:
        errors.append(f'{rf}: sin tarea impl u ops')
    if not rf_test[rf]:
        errors.append(f'{rf}: sin tarea test')
    if not rf_ca[rf]:
        errors.append(f'{rf}: sin criterio de aceptación')
for ca in cas:
    if ca not in tested_cas:
        errors.append(f'{ca}: ninguna tarea test lo verifica')


def sort_key(tid):
    return int(tid[len(PREFIX):])


def topo_order(ids):
    """Orden topológico dentro de la fase; a igualdad, por ID."""
    pending = sorted(ids, key=sort_key)
    idset, done, result = set(ids), set(), []
    while pending:
        for tid in pending:
            if all(d in done or d not in idset for d in tasks[tid]['deps']):
                result.append(tid)
                done.add(tid)
                pending.remove(tid)
                break
        else:
            errors.append('ciclo de dependencias en: ' + ', '.join(pending))
            return result + pending
    return result


def canonical_order():
    """Orden secuencial por spec: specs en orden; dentro de cada spec, por fase y por
    orden topológico de las filas de su tabla. Después, las épicas en el orden de EXTRA."""
    result = []
    for num in sorted(specs):
        ids = [t for t in tasks if tasks[t]['spec'] == num]
        pending = sorted(ids, key=lambda t: (PHASE_CODES.index(PHASE_OF[t]), tasks[t]['row']))
        idset, seen = set(ids), set()
        while pending:
            for tid in pending:
                if all(d in seen or d not in idset for d in tasks[tid]['deps']):
                    result.append(tid)
                    seen.add(tid)
                    pending.remove(tid)
                    break
            else:
                errors.append(f'spec {num}: ciclo de dependencias en ' + ', '.join(pending))
                return result + pending
    return result + [tid for _, tid, _, _ in EXTRA]


ordered = {code: topo_order([t for t in tasks if PHASE_OF.get(t) == code]) for code in PHASE_CODES}

if errors:
    print('\n'.join(errors))
    sys.exit(1)

# ---------- casillas marcadas a mano ----------
done = set()
if OUT.exists():
    for line in OUT.read_text(encoding='utf-8').splitlines():
        m = DONE_RE.match(line)
        if m and m.group(1) in tasks:
            done.add(m.group(1))

# ---------- orden secuencial (constitución §17) ----------
canonical = canonical_order()
position = {tid: i for i, tid in enumerate(canonical)}
for tid in canonical:
    for d in tasks[tid]['deps']:
        if position[d] > position[tid]:
            errors.append(f'{tid} depende de {d}, que va después en el orden de las specs: '
                          'una tarea solo puede depender de tareas anteriores (spec anterior, o fila anterior de su spec)')
if errors:
    print('\n'.join(errors))
    sys.exit(1)


def renumber():
    """Asigna G360F-0001…N en el orden canónico y reescribe los IDs en specs, CLAUDE.md y este script."""
    if done:
        print('--renumber no se permite: ya hay tareas cerradas ([x]) y sus IDs son tickets de commits.')
        sys.exit(1)
    mapping = {old: f'{PREFIX}{i + 1:04d}' for i, old in enumerate(canonical)}
    targets = list(SPECS) + [CLAUDE_MD, SELF]
    for path in targets:
        text = path.read_text(encoding='utf-8')
        # Dos pasadas para que un ID nuevo no se confunda con uno viejo todavía sin reemplazar.
        text = TASK_RE.sub(lambda m: f'@@{mapping[m.group(0)][len(PREFIX):]}@@' if m.group(0) in mapping else m.group(0), text)
        text = re.sub(r'@@(\d{4})@@', PREFIX + r'\1', text)
        if path in SPECS:
            text = sort_task_rows(text)
        path.write_text(text, encoding='utf-8')
    changed = sum(1 for old, new in mapping.items() if old != new)
    print(f'Renumeradas {changed} de {len(mapping)} tareas. Regenerando {OUT}…', flush=True)
    os.execv(sys.executable, [sys.executable, str(SELF), str(DOCS)])


def sort_task_rows(text):
    """Ordena por ID las filas de la tabla Tareas de una spec."""
    lines = text.split('\n')
    section, idx = None, []
    for i, line in enumerate(lines):
        if line.startswith('## '):
            section = line
        if line.startswith('| ' + PREFIX) and section and 'Tareas' in section:
            idx.append(i)
    rows = sorted((lines[i] for i in idx), key=lambda l: cells(l)[0])
    for i, row in zip(idx, rows):
        lines[i] = row
    return '\n'.join(lines)


if RENUMBER:
    renumber()

expected = [f'{PREFIX}{i + 1:04d}' for i in range(len(canonical))]
for tid in canonical:
    for d in tasks[tid]['deps']:
        if sort_key(d) > sort_key(tid):
            errors.append(f'{tid} depende de {d}, que tiene un número mayor')
if not done and canonical != expected:
    errors.append('la numeración no es secuencial por spec (hay saltos o desorden): '
                  'ejecuta `python3 docs/tools/gen_tasks.py docs --renumber`')
if errors:
    print('\n'.join(errors))
    sys.exit(1)


# ---------- render ----------
def ready_at_phase_start(tid):
    return all(PHASE_OF[d] != PHASE_OF[tid] for d in tasks[tid]['deps'])


def spec_link(num):
    return f'[spec {num}](specs/{specs[num]["file"]})'


TYPES = ('impl', 'test', 'ops', 'epic')
out = []
w = out.append
w('# Tareas — SEGlobal 360 frontend')
w('')
w('> **Archivo generado** por `docs/tools/gen_tasks.py`. La fuente de cada tarea es la tabla *Tareas* de su spec, y la de cada pendiente con el backend, las líneas `- **Backend/NN** — …` de la §11 de su spec. Las épicas post-MVP se definen en el script (`EXTRA`). Lo único que se edita a mano son las casillas `[x]`, que se conservan al regenerar (§7).')
w('')
w('## 1. Cómo leer este documento')
w('')
w('- **ID:** `G360F-xxxx`, con numeración propia del frontend de 4 dígitos. Es también el ticket del commit (`[G360F-xxxx] feat: …`, constitución §16). Los IDs van en orden secuencial por spec, y una tarea solo depende de tareas con número menor. Mientras ninguna tarea esté cerrada, se compactan con `--renumber` (§7); después son estables, y una tarea nueva toma el siguiente ID libre.')
w('- **Formato:** `- [ ] ID [P] tipo título`, seguido de una línea con lo que cubre y sus dependencias, y otra con los archivos.')
w('- **`[x]`:** la tarea está mergeada en `main`. Se marca a mano en el PR que la cierra.')
w('- **`[P]`:** la tarea puede empezar al inicio de su fase, porque no depende de otra tarea de la misma fase. Las tareas `[P]` de una fase se pueden repartir en paralelo.')
w('- **Cubre:** los requisitos (`RF-NN.x`) que implementa o los criterios de aceptación (`CA-NN.x`) que verifica.')
w('- **Tipo:** `impl` (código de producción), `test`, `ops` (repositorio, infraestructura, operación) o `epic` (post-MVP: exige escribir y aprobar su spec antes del código).')
w('- **Reglas:** las de trazabilidad de constitución §17. Este script las valida.')
w('')
w('## 2. Resumen')
w('')
w('| Fase | Nombre | Tareas | Hechas | impl | test | ops | epic |')
w('|---|---|---|---|---|---|---|---|')
for code, name, _, _ in PHASES:
    ids = ordered[code]
    cnt = {ty: sum(1 for t in ids if tasks[t]['type'] == ty) for ty in TYPES}
    w(f'| {code} | {name} | {len(ids)} | {sum(1 for t in ids if t in done)} | {cnt["impl"]} | {cnt["test"]} | {cnt["ops"]} | {cnt["epic"]} |')
    if code == 'F6':
        mvp_ids = [t for t in tasks if PHASE_OF[t] in MVP_PHASES]
        w(f'| | **Subtotal MVP (F0–F6)** | **{len(mvp_ids)}** | **{sum(1 for t in mvp_ids if t in done)}** | | | | |')
tot = {ty: sum(1 for t in tasks.values() if t['type'] == ty) for ty in TYPES}
w(f'| | **Total** | **{len(tasks)}** | **{len(done)}** | **{tot["impl"]}** | **{tot["test"]}** | **{tot["ops"]}** | **{tot["epic"]}** |')
w('')
w('```')
w('F0 ─▶ F1 ─▶ F2 ─▶ F3 ─▶ F4 ─▶ F5 ─▶ F6 ═╪═▶ F7, F8, F9, F10, F11, F12 (cada una tras su épica del backend)')
w('                                   corte MVP')
w('```')
w('')
w('| Spec | Título | Estado |')
w('|---|---|---|')
for num in sorted(specs):
    w(f'| {spec_link(num)} | {specs[num]["title"]} | {specs[num]["status"]} |')
w('')
w('## 3. Tareas por fase')
w('')
for code, name, exit_, mvp in PHASES:
    ids = ordered[code]
    w(f'### {code} — {name}')
    w('')
    specs_in = sorted({tasks[t]['spec'] for t in ids if tasks[t]['spec']})
    if specs_in:
        w('Specs: ' + ', '.join(spec_link(s) for s in specs_in) + '.')
        w('')
    for tid in ids:
        t = tasks[tid]
        box = 'x' if tid in done else ' '
        p = ' [P]' if ready_at_phase_start(tid) else ''
        covers = ', '.join(t['covers']) if t['covers'] else '—'
        deps = ', '.join(t['deps']) if t['deps'] else '—'
        w(f'- [{box}] **{tid}**{p} `{t["type"]}` {t["title"]}')
        w(f'  - cubre: {covers} · depende de: {deps}')
        w(f'  - archivos: {t["files"]}')
    w('')
    w(f'**Criterio de salida {code}:** {exit_}')
    w('')
    if code == 'F6':
        w('---')
        w('')
        w('> **Corte del MVP.** Lo que sigue son épicas post-MVP. Cada una exige escribir y aprobar su spec (con RF, CA y tareas propias) antes de escribir código.')
        w('')

w('## 4. Matriz de trazabilidad: requisito → tareas')
w('')
w('| Spec | RF | Implementan | Verifican (tests) | CA |')
w('|---|---|---|---|---|')
for rf in sorted(rfs, key=lambda r: (r[3:5], int(r.split('.')[1]))):
    w(f'| {rfs[rf]} | {rf} | {", ".join(sorted(rf_impl[rf], key=sort_key))} | {", ".join(sorted(rf_test[rf], key=sort_key))} | {", ".join(sorted(rf_ca[rf], key=lambda c: int(c.split(".")[1])))} |')
w('')
w('## 5. Épicas post-MVP')
w('')
w('| ID | Fase | Épica | Depende de |')
w('|---|---|---|---|')
for code in PHASE_CODES:
    for tid in ordered[code]:
        if tasks[tid]['type'] == 'epic':
            w(f'| {tid} | {code} | {tasks[tid]["title"]} | {", ".join(tasks[tid]["deps"]) or "—"} |')
w('')
w('## 6. Pendientes con el backend')
w('')
w('Huecos del contrato de la API que encontraron las specs del frontend. Cada uno se resuelve enmendando la spec del backend indicada; mientras tanto, el front aplica el valor por defecto que dice su spec.')
w('')
if backend_items:
    w('| Spec del front | Spec del backend | Pendiente |')
    w('|---|---|---|')
    for front, back, text in sorted(backend_items):
        w(f'| {spec_link(front)} | `backend/{back}` | {text} |')
else:
    w('Ninguno.')
w('')
w('## 7. Regenerar y validar')
w('')
w('El script lee los `RF`, los `CA` y las tablas *Tareas* de cada spec, junto con las épicas de `EXTRA`. Conserva las casillas `[x]` de este archivo, lo reescribe, y falla (código 1, con la lista de problemas) si encuentra:')
w('- un ID, RF o CA duplicado, un RF o CA definido fuera de su spec, o un CA que cita un RF de otra spec;')
w('- una fila de la tabla *Tareas* que no tiene 7 columnas, un tipo o una fase inválidos, o una épica en una fase del MVP;')
w('- una tarea `impl` u `ops` sin RF, o una tarea `test` sin CA;')
w('- un RF sin tarea `impl` u `ops`, sin tarea `test` o sin CA, o un CA que ninguna tarea `test` verifica;')
w('- una dependencia inexistente, hacia una fase posterior, hacia una tarea con número mayor, o un ciclo;')
w('- mientras ninguna tarea esté cerrada, una numeración que no sea secuencial por spec (G360F-0001…N sin saltos).')
w('')
w('```bash')
w('python3 docs/tools/gen_tasks.py docs              # valida y regenera')
w('python3 docs/tools/gen_tasks.py docs --renumber   # compacta los IDs; solo antes de cerrar la primera tarea')
w('```')
w('')
w(f'Última generación: {len(specs)} specs, {len(rfs)} RF, {len(cas)} CA, {len(tasks)} tareas ({len(done)} hechas), {len(backend_items)} pendientes con el backend. Validación sin errores. Siguiente ID libre: `{PREFIX}{max(sort_key(t) for t in tasks) + 1:04d}`.')

OUT.write_text('\n'.join(out) + '\n', encoding='utf-8')
print(f'OK: {len(specs)} specs, {len(rfs)} RF, {len(cas)} CA, {len(tasks)} tareas ({len(done)} hechas)')
