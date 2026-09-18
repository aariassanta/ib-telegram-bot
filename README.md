# IB Gateway Telegram Bot

Telegram bot para controlar IB Gateway (Interactive Brokers) en Docker/Proxmox de forma remota.

## Características

- 📊 **Status** — Ver estado del contenedor IB Gateway
- 📋 **Logs** — Ver últimos logs en tiempo real
- 🔄 **Restart** — Reiniciar el gateway
- 🛑 **Stop** — Detener el gateway
- ▶️ **Start** — Iniciar el gateway
- 🔒 **Logout** — Cerrar sesión

## Requisitos

- Docker en el servidor (Proxmox, VPS, etc.)
- Bot de Telegram (creado via @BotFather)
- IB Gateway corriendo en Docker con nombre `ib-gateway`

## Instalación

### 1. Clonar el repo

```bash
git clone https://github.com/aariassanta/ib-telegram-bot.git
cd ib-telegram-bot
```

### 2. Configurar variables

```bash
cp .env.example .env
nano .env
```

Variables necesarias:
- `TELEGRAM_BOT_TOKEN` — Token del bot de @BotFather
- `ADMIN_PASSWORD` — Password para acceder
- `AUTHORIZED_USER_IDS` — IDs de Telegram autorizados (opcional)

### 3. Desplegar

```bash
docker compose up -d --build
```

## Uso

1. Abre Telegram y busca tu bot
2. Envía `/start`
3. Ingresa el password configurado
4. Usa los botones del menú

## Comandos

| Comando | Función |
|---------|---------|
| `/start` | Iniciar autenticación |
| `/menu` | Mostrar menú de botones |
| `/status` | Ver estado del gateway |
| `/logs` | Ver últimos logs |
| `/restart` | Reiniciar gateway |
| `/stop` | Detener gateway |
| `/startgw` | Iniciar gateway |
| `/logout` | Cerrar sesión |

## Redes

El bot debe estar en la misma red Docker que el contenedor IB Gateway. Si tu IB Gateway está en `ib-trading-app_default`:

```yaml
# docker-compose.yml
networks:
  ib-trading-app_default:
    external: true
```

## Seguridad

- Password de acceso obligatorio
- Sesiones expiran en 24 horas
- Solo usuarios autorizados pueden acceder (opcional: `AUTHORIZED_USER_IDS`)

## Troubleshooting

**Error: `name 'GATEWAY_CONTAINER' is not defined`**
→ Asegúrate de hacer `docker compose up -d --build` (no solo restart)

**El bot no responde**
→ Verifica los logs: `docker logs ib-telegram-bot`

**No puede conectar al gateway**
→ Verifica que el contenedor se llame `ib-gateway` o cambia `GATEWAY_CONTAINER` en `app/config.py`
