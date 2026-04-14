# MORGANA - Guia Finviz Screener PRD

## Problem Statement
Mejorar el frontend de una guia HTML estatica del sistema MORGANA para Finviz Screener. Agregar experiencia mobile, tabla comparativa de cacerias, integracion TradingView Advanced Chart, y 12 nuevos tip cards avanzados.

## Architecture
- **Frontend**: React.js + Tailwind CSS (dark institutional theme)
- **Backend**: FastAPI + MongoDB (favorites CRUD)
- **TradingView**: iframe embed (Advanced Chart widget, dark theme)
- **Design**: "Old Money Tech" - Playfair Display headings, IBM Plex Sans body, JetBrains Mono code

## Core Requirements
1. Dark, elegant, institutional design (Bloomberg meets premium publication)
2. Mobile responsive with hamburger drawer navigation
3. 8 Cacerias documented with exact filters and URLs
4. Comparative table of all 8 cacerias side-by-side
5. TradingView Advanced Chart with symbol switcher
6. 20 Pro Tips (8 fundamental + 12 advanced MORGANA strategies)
7. Educational sections (What is Finviz, Setup, Tabs, Results)
8. Common Mistakes section
9. Workflow pipeline visualization
10. Backend favorites API (save/remove favorite cacerias)

## What's Been Implemented (2026-01-14)
- [x] Full React SPA with dark theme (#050505 base, #C5A059 gold accent)
- [x] Sidebar navigation with 18+ items + mobile hamburger drawer
- [x] Hero section with background image + gold gradient text
- [x] 4 educational sections with data tables and callouts
- [x] TradingView Advanced Chart (iframe, dark theme, 6 symbol buttons)
- [x] Comparative table of 8 cacerias (risk, exchange, market cap, objective, filters)
- [x] 8 Caceria cards with: filter recipes, copy URL, favorite toggle, tips, warnings
- [x] 20 Pro Tips (8 fundamental + 12 advanced from user's MORGANA strategies)
- [x] Common Mistakes section (7 errors)
- [x] Workflow section (6-step pipeline + 3 questions table)
- [x] Backend: Favorites CRUD (POST/GET/DELETE /api/favorites)
- [x] Mobile responsive (all sections, tables scroll horizontally)
- [x] Testing: Backend 100%, Frontend 95%+

## Prioritized Backlog
### P0 (Done)
- All core features implemented

### P1
- Search/filter functionality for cacerias
- Bookmark/save specific filter configurations
- Export favorites list as CSV/JSON

### P2
- User authentication for personal favorites
- Dark/Light theme toggle
- Real-time stock data integration
- Notification alerts when screener conditions are met
- Multi-language support (EN/ES)

## User Personas
1. **Analista Senior**: Experienced trader using MORGANA system daily
2. **Analista Junior**: Learning stock screening, needs educational content
3. **Inversor Institucional**: Uses as quick reference for screening criteria
