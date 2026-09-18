import docker
from app.config import GATEWAY_CONTAINER

client = docker.from_env()

def get_gateway_status() -> dict:
    try:
        container = client.containers.get(GATEWAY_CONTAINER)
        return {
            "status": container.status,
            "running": container.status == "running",
            "health": container.attrs.get("State", {}).get("Health", {}).get("Status"),
            "uptime": container.attrs.get("State", {}).get("StartedAt"),
        }
    except docker.errors.NotFound:
        return {"status": "not_found", "running": False}

def restart_gateway() -> str:
    container = client.containers.get(GATEWAY_CONTAINER)
    container.restart()
    return "Gateway reiniciado"

def stop_gateway() -> str:
    container = client.containers.get(GATEWAY_CONTAINER)
    container.stop()
    return "Gateway detenido"

def start_gateway() -> str:
    container = client.containers.get(GATEWAY_CONTAINER)
    container.start()
    return "Gateway iniciado"

def get_logs(lines: int = 30) -> str:
    container = client.containers.get(GATEWAY_CONTAINER)
    logs = container.logs(tail=lines).decode("utf-8", errors="replace")
    truncated = logs[-3000:] if len(logs) > 3000 else logs
    return f"Logs:\n{truncated}"
