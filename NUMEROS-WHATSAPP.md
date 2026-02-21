# 📱 Números de WhatsApp Configurados

## Configuración de Números

### 1. Número del Bot (Envía mensajes)

- **Número**: +593 98 430 4211
- **Formato interno**: `593984304211`
- **Uso**: Este número enviará todos los mensajes a los clientes
- **Conexión**: Se vinculará mediante Evolution API (escaneo de QR code)

### 2. Número del Propietario (Recibe notificaciones)

- **Número**: +593 99 949 6469
- **Formato interno**: `593999496469`
- **Uso**: Recibe notificaciones cuando un cliente envía comprobante de pago
- **Variable**: `OWNER_WHATSAPP=593999496469`

## Flujo de Notificaciones

Cuando un cliente envía comprobante de pago:

```
Cliente → Bot (593984304211)
         ↓
Sistema procesa imagen
         ↓
Notificación → Propietario (593999496469)
```

**Mensaje de notificación al propietario:**

```
Nueva venta pendiente de verificación:

👤 Cliente: Carlos
🌎 País: Ecuador
📱 Teléfono: 593987654321
💰 Monto: $9.0
📸 Comprobante: [imagen]

Para confirmar:
Responde "CONFIRMAR" o usa el endpoint:
POST /api/confirm-payment
Body: {"phone_number": "593987654321"}
```

## Configuración en Evolution API

Cuando despliegues, necesitarás:

1. **Conectar el bot (593984304211)**:
   - Ir a Evolution API dashboard
   - Crear instancia: `whatsapp-bot-593984304211`
   - Escanear QR code con el celular del bot

2. **Configurar webhook**:
   ```bash
   POST http://YOUR_VM_IP:8080/instance/create
   Body: {
     "instanceName": "whatsapp-bot-593984304211",
     "webhook": "http://localhost:8000/webhooks/evolution"
   }
   ```

## Próximos Pasos

- [ ] Desplegar en Oracle Cloud VM
- [ ] Instalar Evolution API en Docker
- [ ] Escanear QR code con +593 98 430 4211
- [ ] Probar envío de mensaje de prueba
- [ ] Verificar que +593 99 949 6469 recibe notificaciones
