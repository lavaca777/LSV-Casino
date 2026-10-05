# 🎰 Casino Virtual — Blackjack Edition

Casino virtual **ficticio** donde se juega con dinero simulado (sin pagos ni dinero real).
Proyecto modular pensado para agregar más juegos sin cambiar la arquitectura base.

**Estado:** implementado · **Fecha:** Octubre 2026

---

## 1. Resumen

- **Con login**: cuenta persistente con saldo, préstamos, historial y estadísticas.
- **Juegos**: **Blackjack** (principal) y **Cara o Cruz** (juego extra que valida la modularidad del motor).

El foco principal es el **backend**; el frontend es secundario y se optimiza para desktop.

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Backend | FastAPI (Python) | FastAPI 0.141 · Python 3.13 |
| Frontend | React + Vite | React 19 · Vite 8 |
| Base de datos | PostgreSQL | 13 (contenedor Docker) |
| ORM | SQLAlchemy | 2.0 |
| Validación | Pydantic | 2.x |
| Autenticación | JWT (PyJWT) + bcrypt | PyJWT 2.13 · bcrypt 5.0 |
| Router (frontend) | React Router | 7.x |
| HTTP (frontend) | Axios | 1.x |
| Tests | pytest | 9.x |

---

## 3. Arquitectura General

**Monolito** backend (FastAPI) + **SPA** frontend (React), con PostgreSQL.

```
┌─────────────────────────────────────────────────────┐
│                   CLIENTE (React SPA)               │
│   Lobby · Blackjack · Cara o Cruz · Perfil          │
│   Billetera · Historial · Estadísticas              │
└──────────────────┬──────────────────────────────────┘
                   │ REST API (JSON) + JWT Bearer
                   ▼
┌─────────────────────────────────────────────────────┐
│              SERVIDOR (FastAPI - monolito)          │
│   routers/  → rutas HTTP (delegan)                  │
│   services/ → lógica de negocio                     │
│   games/    → motor de juegos modular (BaseGame)    │
│   models/   → tablas (SQLAlchemy)                   │
│   schemas   → validación (Pydantic)                 │
│   utils/    → seguridad (JWT/bcrypt), rate limit    │
└──────────────────┬──────────────────────────────────┘
                   │ SQL (SQLAlchemy)
                   ▼
┌─────────────────────────────────────────────────────┐
│            BASE DE DATOS (PostgreSQL)               │
│   users · wallets · loans · withdrawals             │
│   games · game_sessions · game_results              │
└─────────────────────────────────────────────────────┘
```

**Capas del backend (patrón Service + Router):**
- `routers/`: definen las rutas HTTP; **no** contienen lógica de negocio.
- `services/`: lógica de negocio.
- `models/`: tablas de la BD.
- `schemas.py`: validación de entrada/salida (Pydantic).
- `games/`: motor de juegos modular.
- `utils/`: seguridad, rate limiting y seed del catálogo.

---

## 4. Módulos Principales

### 4.1 Auth / Usuarios
- Registro y login (email/username + contraseña).
- Hashing con **bcrypt**; autenticación **JWT** (bearer token, expira en 24 h).
- **Rate limiting**: máx. 5 intentos fallidos por minuto.
- Perfil: ver/actualizar datos y cambiar contraseña.
- Logout *stateless* (el cliente descarta el token).

### 4.2 Wallet
- Saldo y `total_wagered` por usuario (se crea al registrarse).
- **Préstamos de $20** (solo si el saldo es **menor a $5**).
- **Retiros ficticios**: se aprueban automáticamente y **descuentan el saldo** (no puede superar el saldo).
- Validación de apuestas: mínimo **$5**, máximo el saldo disponible.

### 4.3 Motor de Juegos (modular)
```
games/
├─ base.py               # clase abstracta BaseGame
├─ blackjack/            # cartas.py · blackjack.py · game.py
└─ coinflip/             # game.py
```
Cada juego hereda de **`BaseGame`** y expone:
- `play(user_id, bet, **opciones)` → resultado de la partida
- `get_rules()` → reglas del juego
- `get_house_edge()` → ventaja de la casa

Los juegos disponibles se registran en la tabla **`games`** mediante un *seed* al arrancar el servidor.

### 4.4 Historial
- Listado paginado de las partidas del usuario (más recientes primero), con filtro por juego.
- Detalle de cada partida (manos jugadas, duración, payout, balance posterior).

### 4.5 Estadísticas
- Total de partidas, ganadas/perdidas/empates y tasa de victoria.
- Racha actual y racha más larga (los **empates no cortan** la racha).
- Mayor ganancia, total apostado y **profit/loss**.

---

## 5. API REST

Base: `http://localhost:8000` · Documentación interactiva: **`/docs`**

| Área | Método y ruta |
|---|---|
| Auth | `POST /auth/register` · `POST /auth/login` · `POST /auth/logout` |
| Usuarios | `GET /users/{id}` · `PUT /users/{id}` · `PUT /users/{id}/password` |
| Wallet | `GET /users/{id}/wallet` · `POST /users/{id}/loans/request` · `GET /users/{id}/loans/history` |
| Retiros | `POST /users/{id}/withdrawals/request` · `GET /users/{id}/withdrawals` |
| Juegos | `GET /games` · `POST /games/coinflip/play` |
| Blackjack | `POST /games/blackjack/start` · `POST /games/blackjack/{id}/hit` · `POST /games/blackjack/{id}/stand` · `GET /games/blackjack/{id}` |
| Historial | `GET /users/{id}/games` · `GET /users/{id}/games/{session_id}` |
| Estadísticas | `GET /users/{id}/stats` |
| Sistema | `GET /` · `GET /health` |

**Autenticación:** los endpoints protegidos requieren `Authorization: Bearer <token>`. El dueño solo puede acceder a sus propios recursos (403 si no).

---

## 6. Juegos

### 6.1 Blackjack
- El jugador compite contra **2 bots**.
- Acciones: **Hit** (pedir) y **Stand** (plantarse).
- Valor de mano con **ases flexibles** (11 o 1); los bots piden si su mano es < 17.
- Resultado: `win` / `loss` / `draw` según la mejor mano.
- Rondas de varios pasos: se pueden **retomar tras recargar** la página.
- **Payout:** win = apuesta × 2 · draw = apuesta · loss = 0.

### 6.2 Cara o Cruz
- El jugador elige cara/cruz; se lanza la moneda; si acierta, gana.
- Sirve para demostrar que **agregar un juego es simple** (una clase `BaseGame` + seed).

### 6.3 Flujo de dinero (común)
1. Se valida la apuesta (mín. $5, máx. = saldo).
2. Se descuenta la apuesta del saldo.
3. Se paga el **payout** según el resultado.
4. Se registra la partida (`game_sessions` + `game_results`) con el **balance posterior**.

---

## 7. Flujo de Usuario

### Usuario con login
1. **Registro**: email, username y contraseña.
2. **Login**: entra y recibe un JWT.
3. **Lobby**: ve el saldo y el grid de juegos.
4. **Pedir préstamo**: $20 (solo si el saldo es menor a $5).
5. **Jugar**: apuesta entre $5 y su saldo (Blackjack o Cara o Cruz).
6. **Billetera**: préstamos, retiros (descuentan saldo) e historial.
7. **Historial**: partidas con filtro y detalle.
8. **Perfil**: datos y cambio de contraseña.
9. **Estadísticas**: win rate, rachas, ganancias, profit/loss.

---

## 8. Base de Datos

**7 tablas** (PostgreSQL):

| Tabla | Campos principales |
|---|---|
| `users` | id (UUID), username (único), email (único), password_hash, created_at, updated_at |
| `wallets` | id, user_id (FK), balance, total_wagered, updated_at |
| `loans` | id, user_id (FK), amount, requested_at |
| `withdrawals` | id, user_id (FK), amount, requested_at, status |
| `games` | id, name (único), min_bet, max_bet, house_edge, created_at |
| `game_sessions` | id, user_id (FK), game_id (FK), bet, started_at, ended_at, result, payout, **balance_after** |
| `game_results` | id, session_id (FK), result_type, player_hand (JSONB), bot_hands (JSONB) |

Las tablas se crean automáticamente al arrancar el backend (con una mini-migración idempotente para columnas nuevas).

---

## 9. Features de Usuario

- **Lobby**: grid de juegos, saldo destacado, menú de usuario (Perfil, Historial, Estadísticas, Billetera, Salir) y botón "Pedir préstamo" (visible si el saldo es bajo).
- **Cuenta**: datos personales (usuario, email, fecha de creación) y cambio de contraseña.
- **Billetera**: saldo, formulario de retiro e historial de préstamos/retiros.
- **Historial**: tabla (Juego · Fecha · Resultado · Apuesta · Payout · Balance), paginación, filtro por juego y detalle en modal.
- **Estadísticas**: tarjetas con total de partidas, tasa de victoria, rachas, mayor ganancia, total apostado y profit/loss.

---

## 10. Requisitos Funcionales

### Autenticación & Seguridad
- [x] Registro con email, username y contraseña
- [x] Login con validación
- [x] Rate limiting: 5 intentos fallidos/minuto
- [x] Hashing seguro de contraseñas (bcrypt)
- [x] Validaciones en backend
- [x] Autenticación JWT con bearer tokens

### Juego
- [x] Lógica de Blackjack (hit, stand, evaluación de mano)
- [x] Bots funcionando (2)
- [x] Cálculo correcto del ganador
- [x] Actualización de saldo tras la partida
- [x] Registro de la partida en la BD
- [x] Juego extra (Cara o Cruz) para validar la modularidad

### Wallet & Dinero
- [x] Crear wallet al registrarse
- [x] Préstamos de $20 (solo si el saldo es < $5)
- [x] Validación de apuesta (mín. $5, máx. saldo)
- [x] Actualización de balance tras cada partida
- [x] Registro de retiros (descuentan el saldo ficticio)

### Historial & Estadísticas
- [x] Historial paginado y con filtro por juego
- [x] Detalle de partida (manos jugadas)
- [x] Estadísticas en tiempo real (win rate, rachas, ganancias, profit/loss)

### UI/UX
- [x] Página principal con grid de juegos
- [x] Saldo visible y destacado
- [x] Página de juego funcional (Blackjack / Cara o Cruz)
- [x] Perfil de usuario
- [x] Historial de partidas
- [x] Estadísticas
- [x] Interfaz desktop

---

## 11. Requisitos No Funcionales

- **Seguridad:** validaciones en backend, contraseñas con bcrypt, JWT.
- **Escalabilidad:** motor de juegos modular (`BaseGame`).
- **Rendimiento:** consultas eficientes (JOIN para evitar N+1).
- **Documentación:** docstrings en el código y este README.

---

## 12. Instalación y Ejecución

### 12.1 Prerrequisitos

| Herramienta | Versión | Nota |
|---|---|---|
| Docker + Docker Compose | reciente | Base de datos (PostgreSQL 13) |
| Python | 3.9+ (probado con 3.13) | Backend |
| Node.js + npm | reciente (probado con Vite 8) | Frontend |

### 12.2 Base de datos (Docker)

```bash
docker compose up -d
```

- Puerto: **5433** (evita conflicto con un PostgreSQL local en el 5432)
- Usuario: `casino` · Contraseña: `casino_dev_password` · Base: `casino_db`

Las tablas se crean automáticamente al arrancar el backend.

### 12.3 Variables de entorno

```bash
# Backend
cp Backend/.env.example Backend/.env
# Frontend
cp Frontend/.env.example Frontend/.env
```

- `Backend/.env` → `DATABASE_URL` y `SECRET_KEY` (firma de JWT).
- `Frontend/.env` → `VITE_API_URL=http://localhost:8000`.

### 12.4 Backend (FastAPI)

```bash
cd Backend
python -m venv LSV                # crear entorno virtual (opcional)
LSV\Scripts\activate              # activarlo (Windows)
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Servidor en `http://localhost:8000` · Documentación en `http://localhost:8000/docs`.

### 12.5 Frontend (React + Vite)

```bash
cd Frontend
npm install
npm run dev
```

Servidor de desarrollo en `http://localhost:5173`.

### 12.6 Tests

```bash
# Desde la raíz del repo (requiere la BD corriendo)
Backend/LSV/Scripts/python.exe -m pytest Backend/tests -v
```

Actualmente hay **154 tests** que pasan. Usan la base real de desarrollo y la vacían entre pruebas.

### 12.7 Comandos útiles

| Acción | Comando |
|---|---|
| Levantar BD | `docker compose up -d` |
| Detener BD | `docker compose down` |
| Ver BD con pgAdmin | conectarse a `localhost:5433`, usuario `casino` |
| Arrancar backend | `python -m uvicorn main:app --reload` (en `Backend/`) |
| Correr tests backend | `pytest Backend/tests` (desde la raíz) |
| Arrancar frontend | `npm run dev` (en `Frontend/`) |
| Lint frontend | `npm run lint` (en `Frontend/`) |
| Build frontend | `npm run build` (en `Frontend/`) |
