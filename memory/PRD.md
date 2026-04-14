# MORGANA - Guia Finviz Screener PRD

## Problem Statement
Mejorar el frontend de una guia HTML estatica del sistema MORGANA para Finviz Screener. Agregar experiencia mobile, tabla comparativa de cacerias, integracion TradingView Advanced Chart, 12 nuevos tip cards avanzados, busqueda/filtro de cacerias, export CSV de favoritos, y autenticacion de usuarios.

## Architecture
- **Frontend**: React.js + Tailwind CSS (dark institutional "Old Money Tech" theme)
- **Backend**: FastAPI + MongoDB (auth + favorites CRUD)
- **TradingView**: iframe embed (Advanced Chart widget, dark theme)
- **Auth**: JWT Bearer tokens (bcrypt + PyJWT), admin seeding
- **Design**: Playfair Display headings, IBM Plex Sans body, JetBrains Mono code, #C5A059 gold accent

## What's Been Implemented

### Iteration 1 (2026-01-14)
- [x] Full React SPA with dark theme (#050505 base, #C5A059 gold accent)
- [x] Sidebar navigation with 18+ items + mobile hamburger drawer
- [x] Hero section with background image + gold gradient text
- [x] 4 educational sections with data tables and callouts
- [x] TradingView Advanced Chart (iframe, dark theme, 6 symbol buttons)
- [x] Comparative table of 8 cacerias
- [x] 8 Caceria cards with filter recipes, copy URL, favorite toggle
- [x] 20 Pro Tips (8 fundamental + 12 advanced MORGANA strategies)
- [x] Common Mistakes section + Workflow section
- [x] Backend: Favorites CRUD (anonymous)

### Iteration 2 (2026-01-14)
- [x] JWT authentication (register, login, me endpoints)
- [x] Auth modal with login/register tabs (elegant dark design)
- [x] Admin user seeded on startup
- [x] User-scoped favorites (personal when logged in, anonymous otherwise)
- [x] Search bar for cacerias (by name, description, filter names/values)
- [x] Risk profile filter dropdown (Bajo, Moderado, Alto, Muy Alto)
- [x] CSV export of favorites
- [x] MetaMask/browser extension error suppression
- [x] Testing: Backend 100%, Frontend 100%

## Prioritized Backlog
### P1
- Notification alerts when screener conditions are met
- Real-time stock data integration (e.g., via CoinGecko/Alpha Vantage)

### P2
- Dark/Light theme toggle
- Password reset flow
- Multi-language support (EN/ES)
- Save custom screener configurations
- Share favorites with other users

## User Personas
1. **Analista Senior**: Experienced trader using MORGANA system daily
2. **Analista Junior**: Learning stock screening, needs educational content
3. **Inversor Institucional**: Uses as quick reference for screening criteria
