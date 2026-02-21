# 🤖 Anti-Bot Detection Features

Este documento explica las funcionalidades implementadas para evitar que WhatsApp detecte el bot como automatizado.

## 🎯 Problema

WhatsApp puede detectar y banear bots que:

- Responden instantáneamente (tiempo irreal)
- Nunca muestran "escribiendo..."
- No muestran presencia online/offline
- Envían mensajes con patrones muy regulares

## ✅ Soluciones Implementadas

### 1. **Typing Indicator** ("escribiendo...")

Muestra el indicador de que estás escribiendo antes de enviar el mensaje.

```python
# Automático en sendTextWithHumanBehavior
await evolution_service.sendTextWithHumanBehavior(
    phone_number="593999999999",
    message="Hola, ¿cómo estás?",
    use_typing=True  # ← Muestra "escribiendo..."
)
```

### 2. **Delays Aleatorios Realistas**

El sistema calcula un delay basado en:

- **Delay base**: 0.5-1.5 segundos (tiempo de reacción humana)
- **Delay por caracteres**: ~0.05-0.08 segundos por carácter
- **Máximo**: 10 segundos (para no hacer esperar mucho al usuario)

**Ejemplo**:

- Mensaje corto (20 chars): ~1.5-2.5 segundos
- Mensaje medio (100 chars): ~5-8 segundos
- Mensaje largo (200+ chars): ~10 segundos (máximo)

```python
# Se calcula automáticamente
async def simulateHumanDelay(message: str):
    base_delay = random.uniform(0.5, 1.5)
    char_delay = len(message) * random.uniform(0.05, 0.08)
    total_delay = min(base_delay + char_delay, 10.0)
    await asyncio.sleep(total_delay)
```

### 3. **Presencia Online/Offline**

Simula que el usuario se conecta, responde, y se desconecta:

```python
# 1. Se pone "online"
await setPresence(phone_number, "available")

# 2. Muestra "escribiendo..."
await sendPresenceUpdate(phone_number, "composing")

# 3. Espera tiempo realista
await simulateHumanDelay(message)

# 4. Envía mensaje
await sendTextMessage(phone_number, message)

# 5. Espera 1-3 segundos más
await asyncio.sleep(random.uniform(1.0, 3.0))

# 6. Se pone "offline"
await setPresence(phone_number, "unavailable")
```

### 4. **Variabilidad Aleatoria**

Todos los tiempos usan `random.uniform()` para evitar patrones detectables:

- Tiempo antes de escribir: 0.3-0.8s
- Tiempo después de escribir: 0.2-0.5s
- Tiempo antes de desconectar: 1.0-3.0s

## 🔧 Configuración

### Activar/Desactivar Features

```python
# Usar todas las features (recomendado)
await evolution_service.sendTextWithHumanBehavior(
    phone_number="593999999999",
    message="Hola",
    use_typing=True,      # ← Typing indicator
    use_presence=True     # ← Online/Offline
)

# Solo delays, sin typing
await evolution_service.sendTextWithHumanBehavior(
    phone_number="593999999999",
    message="Hola",
    use_typing=False,
    use_presence=False
)

# Mensaje instantáneo (no recomendado)
await evolution_service.sendTextMessage(
    phone_number="593999999999",
    message="Hola"
)
```

### Ajustar Tiempos

Para modificar los tiempos de delay, edita [evolutionApi.py](../app/services/evolutionApi.py):

```python
async def simulateHumanDelay(self, message: str) -> None:
    # Ajusta estos valores según necesites
    base_delay = random.uniform(0.5, 1.5)  # ← Cambia estos números
    char_delay = len(message) * random.uniform(0.05, 0.08)  # ← Ajusta velocidad de escritura
    total_delay = min(base_delay + char_delay, 10.0)  # ← Cambia máximo

    await asyncio.sleep(total_delay)
```

## 📊 Flujo Completo

**Usuario envía**: "Hola"

```
1. Webhook recibe mensaje (0ms)
2. Agente procesa con OpenAI (200-500ms)
3. Se pone "online" (0ms)
4. Espera aleatoria 0.3-0.8s (500ms avg)
5. Muestra "escribiendo..." (0ms)
6. Delay realista según longitud (3s para msg medio)
7. Para de "escribir" (0ms)
8. Espera 0.2-0.5s (300ms avg)
9. Envía mensaje (0ms)
10. Espera 1-3s (2s avg)
11. Se pone "offline" (0ms)

TOTAL: ~6-7 segundos (parece humano ✅)
```

## 🚨 Importante

### ¿Cuándo NO usar humanización?

- **Notificaciones urgentes**: Usa `sendTextMessage()` directo
- **Respuestas automáticas críticas**: Como confirmaciones de pago
- **Testing rápido**: Desactiva con `use_typing=False, use_presence=False`

### ¿Cuándo SÍ usar humanización?

- ✅ **Conversaciones normales con clientes** (siempre)
- ✅ **Respuestas de agentes**: Greeter, Consultant, Router, Closer
- ✅ **Cualquier interacción simulando humano**

## 🧪 Testing

### Probar localmente

```python
# En tu terminal local con backend corriendo
curl -X POST http://localhost:8000/webhooks/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"remoteJid": "593999999999@s.whatsapp.net", "fromMe": false},
      "message": {"conversation": "Hola"}
    }
  }'
```

Observa los logs:

```
[DEBUG] Presence set to available for 593999999999
[DEBUG] Presence update: composing for 593999999999
[DEBUG] Simulating human typing delay: 3.24s for 85 chars
[DEBUG] Presence update: paused for 593999999999
[INFO] Message sent with human behavior to 593999999999
[DEBUG] Presence set to unavailable for 593999999999
```

## 📈 Mejoras Futuras

Ideas para hacer el bot aún más humano:

1. **Errores de tipeo ocasionales** (y corrección)
2. **Pausas en mensajes largos** (enviar en bloques)
3. **Reacciones con emojis** antes de responder
4. **Leer mensajes** sin responder inmediatamente
5. **Variación en horarios**: Responder más lento de noche

## 🔗 Referencias

- [Evolution API - Presence Docs](https://doc.evolution-api.com/v2/en/endpoints/presence)
- [WhatsApp Bot Best Practices](https://www.whatsapp.com/legal/business-policy)

---

**Implementado por**: GitHub Copilot
**Fecha**: Febrero 2026
**Versión**: 1.0
