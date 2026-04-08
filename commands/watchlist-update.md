---
description: Actualiza output/watchlist.md con el top 10 de empresas analizadas (sistema 5 pilares)
argument-hint: "[opcional: ticker específico para re-escanear]"
---

# /watchlist — Actualizador de Watchlist Morgana

Actualiza `output/watchlist.md` rankeando todas las empresas analizadas por score total (5 pilares, escala 0-100).

## Paso 1 — Escanear reportes

Busca todos los archivos en `output/reportes/` con el patrón:
```
output/reportes/[TICKER]/[FECHA]_*.md
```

Para cada ticker, toma **el archivo más reciente** (fecha más alta en el nombre).
Ignorar `_due_diligence.md` y `_earnings.md` — solo procesar `_analisis*.md` y `_decision*.md`.

## Paso 2 — Extraer scores de cada reporte

**Score total** (buscar en este orden):
```
SCORE.*\*\*(\d+(\.\d+)?)/100\*\*
SCORE.*\*\*(\d+(\.\d+)?)\*\*
(P1×0.25 + P2×0.15 + P3×0.25 + P4×0.25 + P5×0.10) × 10
```

**Scores por pilar** (1–10 cada uno):
```
P1.*Moat.*\*\*(\d+)/10\*\*          → p1_moat
P2.*Finanzas.*\*\*(\d+)/10\*\*      → p2_finanzas
P3.*Motor.*\*\*(\d+)/10\*\*         → p3_motor
P4.*Management.*\*\*(\d+)/10\*\*    → p4_mgmt
P5.*Contexto.*\*\*(\d+)/10\*\*      → p5_contexto
Puntuación:.*\*\*(\d+)/10\*\*       → fallback genérico
```

Si no hay score total, calcularlo: `(p1×0.25 + p2×0.15 + p3×0.25 + p4×0.25 + p5×0.10) × 10`
Si faltan pilares individuales, marcar con `?`.

**Clasificación** (buscar en VEREDICTO / DECISIÓN):
```
COMPOUNDER ELITE  → "COMPOUNDER ELITE 🏆"
HIGH GROWTH       → "HIGH GROWTH ⭐"
WATCHLIST         → "WATCHLIST ⚠️"
DESCARTAR         → "DESCARTAR ❌"
BUY               → usar score para clasificar
AVOID / EVITAR    → "DESCARTAR ❌"
```

## Paso 3 — Detectar cambios vs. análisis anterior

Para cada ticker con más de un reporte, comparar reporte reciente con el anterior:
- Pilar subió → marcar con `↑`
- Pilar bajó → marcar con `↓`
- Clasificación cambió (ej: WATCHLIST → HIGH GROWTH) → añadir `★ Upgrade` o `▼ Downgrade`

## Paso 4 — Rankear y seleccionar top 10

Ordenar de mayor a menor score total. Empate: más reciente primero.
- Score ≥ 60: incluir en tabla principal
- Score < 60: sección "Empresas descartadas"

## Paso 5 — Escribir output/watchlist.md

Sobreescribir con el siguiente formato:

```markdown
# Morgana — Watchlist

> Generado por `/watchlist` | Actualizado: [FECHA HOY]
> Sistema: 5 pilares | Score 0–100 | Corte tabla principal: ≥60

| Rank | Ticker | Score | P1-Moat | P2-Fin | P3-Motor | P4-Mgmt | P5-Ctx | Clasificación | Último análisis |
|------|--------|-------|---------|--------|----------|---------|--------|---------------|----------------|
| 1 | NVDA | 88.5 | 9 | 8 | 9 | 9↑ | 8 | HIGH GROWTH ⭐ | 2026-04-01 |
| 2 | HRMY | 72.0 | 7 | 6↑ | 8 | 7 | 7 | HIGH GROWTH ⭐ | 2026-04-05 |
...

---

## Notas de cambios

- **[TICKER]**: [descripción del cambio] — [fecha anterior] → [fecha actual]

---

## Empresas descartadas (score < 60)

- [TICKER] — score [X] — [motivo si aparece en el reporte]

---

*Ejecuta `/watchlist` para actualizar con los reportes en `output/reportes/`.*
```

### Reglas de formato

- Columnas P1-P5: número 1-10 + flecha si cambió. `?` si no disponible.
- Score: redondeado a 1 decimal.
- Clasificación según umbrales de CLAUDE.md: ≥85 COMPOUNDER ELITE 🏆, 70–84 HIGH GROWTH ⭐, 60–69 WATCHLIST ⚠️, <60 DESCARTAR ❌.
- Si hay menos de 10 empresas válidas, mostrar todas (no forzar 10 filas).
- Si un ticker aparece en `output/portfolio.json` como posición activa, agregar `[EN CARTERA]` junto al ticker.
