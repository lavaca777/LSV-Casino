# 📊 Especificación del Proyecto: Casino Virtual - Blackjack Edition

**Versión:** 1.0  
**Fecha:** Agosto 2026  
**Estado:** Listo para desarrollo  
**Audiencia:** Equipo de desarrollo + Profesor

---

## 1. Resumen Ejecutivo

Desarrollo de un **casino virtual ficticio** donde los usuarios pueden jugar blackjack sin dinero real. El sistema está diseñado para ser **modular y escalable**, permitiendo agregar más juegos en el futuro sin modificar la arquitectura base.

### Diferenciador principal
- **Sin login** *(diferido al final del proyecto)*: Dinero ilimitado, juego para probar, sin persistencia
- **Con login**: Sistema de préstamos de $20, registro permanente con historial completo

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Backend | FastAPI | Python 3.9+ |
| Frontend | React | 18+ |
| Base de datos | PostgreSQL | 13+ |
| API | REST | HTTP/HTTPS |
| Autenticación | JWT | Bearer tokens |

**Nota:** El foco principal es el **BACKEND**. Frontend es secundario y se optimiza para desktop.

---

## 3. Arquitectura General

```
┌─────────────────────────────────────────────────────┐
│                   CLIENTE (React)                   │
│  ┌──────────────────────────────────────────────┐  │
│  │ Página principal (juegos)                    │  │
│  │ Juego (Blackjack)                            │  │
│  │ Perfil de usuario                            │  │
│  │ Historial de partidas                        │  │
│  │ Estadísticas                                 │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │ REST API
                   ▼
┌─────────────────────────────────────────────────────┐
│              SERVIDOR (FastAPI)                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ ├─ Auth Service (JWT)                        │  │
│  │ ├─ User Service                              │  │
│  │ ├─ Game Engine (módulo)                      │  │
│  │ │  └─ Blackjack                              │  │
│  │ ├─ Wallet Service (préstamos, retiros)       │  │
│  │ ├─ Stats Service                             │  │
│  │ └─ Logging (esencial)                        │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │ SQL
                   ▼
┌─────────────────────────────────────────────────────┐
│            BASE DE DATOS (PostgreSQL)               │
│  ├─ users                                           │
│  ├─ wallets                                         │
│  ├─ loans                                           │
│  ├─ games                                           │
│  ├─ game_sessions                                   │
│  ├─ game_results                                    │
│  └─ withdrawals                                     │
└─────────────────────────────────────────────────────┘
```

---

## 4. Módulos Principales

### 4.1 Auth Service
- Registro / Login
- Validación de credenciales
- Rate limiting: 5 intentos fallidos por minuto
- Hashing seguro de contraseñas (bcrypt)
- Autenticación JWT con bearer tokens

### 4.2 User Service
- CRUD de perfil
- Datos personales (nombre, usuario, email, fecha creación)
- Cambio de contraseña

### 4.3 Game Engine (Modular)
**Estructura base para juegos:**
```
games/
├─ __init__.py
├─ base.py (clase abstracta)
├─ blackjack.py
└─ [otros juegos aquí]
```

**Cada juego hereda de `BaseGame`** y expone:
- `play(user_id, bet)` → devuelve resultado
- `get_rules()` → reglas del juego
- `get_house_edge()` → ventaja de la casa

### 4.4 Wallet Service
- Gestión de dinero de usuario
- Sistema de préstamos de $20 (sin límite diario por ahora; los límites quedan como opcional al final)
- Validación de apuestas mínimas/máximas
- Registro de retiros (solo lógica, no dinero real)

### 4.5 Stats Service
- Cálculo de estadísticas en tiempo real

### 4.6 Logging
- Logs de errores críticos
- Logs de transacciones de dinero
- Logs de partidas (inicio/final)

---

## 5. Flujo de Usuario

### 5.1 Usuario SIN LOGIN *(diferido al final del proyecto)*
1. Entra a la página principal
2. Ve grid de juegos
3. Hace clic en Blackjack
4. Juega con dinero ilimitado (simulado)
5. Cierra el navegador → se pierde todo (sin persistencia)

### 5.2 Usuario CON LOGIN
1. **Registro**: Crea cuenta (email, username, contraseña)
2. **Login**: Entra con credenciales
3. **Dashboard**: Ve saldo actual, botón de préstamo visible
4. **Pedir préstamo**: Puede pedir préstamos de $20 (sin límite diario por ahora)
5. **Juega**: Apuesta entre $5 y su saldo disponible
6. **Historial**: Todas las partidas se registran con resultado y balance
7. **Perfil**: Ve sus datos, puede cambiar contraseña
8. **Estadísticas**: Ve sus stats de juego

---

## 6. Juego Principal: Blackjack

### 6.1 Mecánica Básica
- **Oponentes:** 2 bots, juegan en secuencia (uno tras otro)
- **Reglas:** Blackjack estándar
- **Apuesta mínima:** $5
- **Apuesta máxima:** Saldo disponible del usuario

### 6.2 Acciones del Jugador
- Hit (pedir carta)
- Stand (plantarse)

### 6.3 Bots
- 2 bots con comportamiento simple (hit si < 17, stand si >= 17)
- Juegan en secuencia (primero bot 1, luego bot 2, luego jugador)

### 6.4 Resultado de Partida
- **Victoria:** Jugador > Bots o Bots quiebran
- **Derrota:** Jugador se pasa de 21 o < todos los bots
- **Empate:** Jugador = Bot

---

## 7. Base de Datos

### 7.1 Tablas Principales

#### users
```sql
id (PK)
username (UNIQUE, NOT NULL)
email (UNIQUE, NOT NULL)
password_hash (NOT NULL)
created_at
updated_at
```

#### wallets
```sql
id (PK)
user_id (FK → users)
balance (DECIMAL, default 0)
total_wagered (DECIMAL, para estadísticas)
updated_at
```

#### loans
```sql
id (PK)
user_id (FK → users)
amount (DECIMAL, default 20)
requested_at
```

#### games
```sql
id (PK)
name (VARCHAR: "blackjack", etc.)
min_bet (DECIMAL)
max_bet (DECIMAL)
house_edge (DECIMAL, para referencia)
created_at
```

#### game_sessions
```sql
id (PK)
user_id (FK → users, nullable si es sin login — *diferido al final*)
game_id (FK → games)
bet (DECIMAL)
started_at
ended_at
result (ENUM: win, loss, draw)
payout (DECIMAL)
session_token (para usuarios sin login — *diferido al final*)
```

#### game_results
```sql
id (PK)
session_id (FK → game_sessions)
result_type (ENUM: win, loss, draw)
player_hand (JSON o TEXT)
bot_hands (JSON o TEXT)
```

#### withdrawals
```sql
id (PK)
user_id (FK → users)
amount (DECIMAL)
requested_at
status (ENUM: pending, approved, rejected)
```

---

## 8. Features de Usuario

### 8.1 Página Principal
- Grid de juegos (cuadrados con nombre, miniatura)
- Saldo visible y destacado en esquina superior derecha
- Botón "Pedir préstamo" (solo usuarios logueados)
- Opción de perfil/usuario (desplegable)

### 8.2 Gestión de Cuenta
- Datos personales: nombre, usuario, email, fecha creación
- Cambiar contraseña
- Ver historial de transacciones (préstamos)

### 8.3 Billetera Virtual
- Registro histórico de retiros solicitados
- Muestra dinero retirado (no dinero actual)

### 8.4 Historial de Partidas
- Tabla: Juego | Fecha | Resultado (V/D/P) | Apuesta | Payout | Balance
- Balance acumulado

### 8.5 Estadísticas
- Total de partidas jugadas
- Tasa de victoria (%)
- Racha actual de victorias
- Racha más larga histórica
- Mayor ganancia en una sola mano
- Fichas totales apostadas en la historia

---

## 9. Requisitos Funcionales

### 9.1 Autenticación & Seguridad
- [ ] Registro con email, username, contraseña
- [ ] Login con validación
- [ ] Rate limiting: 5 intentos fallidos/minuto
- [ ] Hashing seguro de contraseñas (bcrypt)
- [ ] Validaciones en backend
- [ ] Autenticación JWT con bearer tokens

### 9.2 Juego
- [ ] Lógica de Blackjack (hit, stand, evaluación de mano)
- [ ] Bots funcionando en secuencia
- [ ] Cálculo correcto de ganador
- [ ] Actualización de saldo tras partida
- [ ] Registro de partida en BD

### 9.3 Wallet & Dinero
- [ ] Crear wallet al registrarse
- [ ] Lógica de préstamos de $20 (sin límite diario por ahora)
- [ ] Validación de apuesta (min $5, max saldo)
- [ ] Actualización de balance tras cada partida
- [ ] Registro de retiros (sin procesar dinero)

### 9.4 Estadísticas
- [ ] Generar estadísticas en tiempo real
- [ ] Histórico de partidas accesible

### 9.5 UI/UX
- [ ] Página principal con grid de juegos
- [ ] Saldo visible y destacado
- [ ] Modal/página de juego funcional
- [ ] Perfil de usuario
- [ ] Historial de partidas
- [ ] Estadísticas
- [ ] Interfaz desktop

---

## 10. Requisitos No Funcionales

- **Rendimiento:** Las consultas deben < 200ms
- **Disponibilidad:** Deploy en servidor estable
- **Seguridad:** Validaciones en backend, sin inyecciones SQL
- **Escalabilidad:** Modular para agregar juegos
- **Logging:** Logs de errores y transacciones financieras
- **Documentación:** Comentarios en código, README en repo

---

## 11. Instalación y Ejecución

### 11.1 Prerrequisitos

| Herramienta | Versión | Nota |
|-------------|---------|------|
| Docker + Docker Compose | cualquier reciente | Para la base de datos (PostgreSQL 13 en contenedor) |
| Python | 3.9+ (probado con 3.13) | Backend |
| Node.js + npm | cualquier reciente (probado con Vite 8) | Frontend |

### 11.2 Base de datos (Docker)

El proyecto incluye un `docker-compose.yml` con PostgreSQL 13. Para levantarla:

```bash
docker compose up -d
```

- Puerto: **5433** (evita conflicto con un PostgreSQL local en el 5432)
- Usuario: `casino` · Contraseña: `casino_dev_password` · Base: `casino_db`

Las tablas se crean automáticamente al arrancar el backend (no hace falta SQL manual).

### 11.3 Configuración de variables de entorno

Copia las plantillas a los archivos reales y ajusta si es necesario:

```bash
# Backend
cp Backend/.env.example Backend/.env
# Frontend
cp Frontend/.env.example Frontend/.env
```

- `Backend/.env` → `DATABASE_URL` (apunta a la BD del paso 11.2) y `SECRET_KEY` (firma de JWT).
- `Frontend/.env` → `VITE_API_URL=http://localhost:8000` (URL del backend).

### 11.4 Backend (FastAPI)

```bash
cd Backend
python -m venv LSV                # crear entorno virtual (opcional)
LSV\Scripts\activate              # activarlo (Windows)
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

El servidor queda en `http://localhost:8000`. Documentación interactiva de la API en
`http://localhost:8000/docs`.

### 11.5 Frontend (React + Vite)

```bash
cd Frontend
npm install
npm run dev
```

El servidor de desarrollo queda en `http://localhost:5173`.

### 11.6 Tests

```bash
# Tests backend (desde la raíz del repo, requiere BD corriendo)
Backend/LSV/Scripts/python.exe -m pytest Backend/tests -v
```

Los tests de backend usan la base real de desarrollo y la vacían entre pruebas.

### 11.7 Comandos útiles

| Acción | Comando |
|--------|---------|
| Levantar BD | `docker compose up -d` |
| Detener BD | `docker compose down` |
| Ver BD con pgAdmin | conectarse a `localhost:5433`, usuario `casino` |
| Arrancar backend | `python -m uvicorn main:app --reload` (en `Backend/`) |
| Correr tests backend | `pytest Backend/tests` (desde la raíz) |
| Arrancar frontend | `npm run dev` (en `Frontend/`) |
| Lint frontend | `npm run lint` (en `Frontend/`) |
| Build frontend | `npm run build` (en `Frontend/`) |