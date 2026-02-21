# 🔧 Oracle Cloud CLI Setup Guide

## 📥 Instalación

### Opción 1: Script Automático (Recomendado)

```powershell
cd "F:\Angelo Archivos\AgentesIAparaInfoproducto"
.\install-oci-cli.ps1
```

### Opción 2: Instalación Manual con PowerShell

```powershell
# Ejecuta este comando (tarda 2-3 min)
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.ps1'))"
```

### Opción 3: Instalación con Python (Si prefieres)

```powershell
# Usando pip
pip install oci-cli

# Verificar
oci --version
```

## ⚙️ Configuración

### Paso 1: Obtener Información de Oracle Cloud

1. **Ir a Oracle Cloud Console**:

   ```
   https://cloud.oracle.com
   ```

2. **Obtener User OCID**:
   - Click en tu perfil (arriba derecha)
   - Click en tu nombre de usuario
   - Copiar el **OCID** (empieza con `ocid1.user.oc1..`)

3. **Obtener Tenancy OCID**:
   - Click en tu perfil
   - Click en **Tenancy**
   - Copiar el **OCID** (empieza con `ocid1.tenancy.oc1..`)

4. **Obtener Region Identifier**:
   - Arriba derecha, ver tu región actual
   - Ejemplos:
     - US East (Ashburn): `us-ashburn-1`
     - US West (Phoenix): `us-phoenix-1`
     - São Paulo: `sa-saopaulo-1`

### Paso 2: Configurar OCI CLI

```powershell
# Ejecuta este comando
oci setup config
```

**Te pedirá**:

```
Enter a location for your config [C:\Users\angel\.oci\config]:
  → Presiona Enter (usa default)

Enter a user OCID:
  → Pega tu User OCID: ocid1.user.oc1..xxx

Enter a tenancy OCID:
  → Pega tu Tenancy OCID: ocid1.tenancy.oc1..xxx

Enter a region:
  → Escribe tu región: us-ashburn-1

Do you want to generate a new API Signing RSA key pair? [Y/n]:
  → Presiona Y

Enter a directory for your keys [C:\Users\angel\.oci]:
  → Presiona Enter

Enter a name for your key [oci_api_key]:
  → Presiona Enter

Enter a passphrase for your private key (empty for no passphrase):
  → Presiona Enter (sin password)
```

### Paso 3: Subir API Key a Oracle Cloud

El setup generó un archivo `oci_api_key_public.pem`. Necesitas subirlo:

1. **Abrir el archivo public key**:

   ```powershell
   cat "$env:USERPROFILE\.oci\oci_api_key_public.pem"
   ```

2. **Copiar TODO el contenido** (incluyendo BEGIN/END PUBLIC KEY)

3. **Ir a Oracle Cloud Console**:
   - Click en tu perfil
   - Click en tu nombre
   - En la izquierda: **API Keys**
   - Click **Add API Key**
   - Seleccionar **Paste Public Key**
   - Pegar el contenido
   - Click **Add**

### Paso 4: Verificar Configuración

```powershell
# Ver tu config
cat "$env:USERPROFILE\.oci\config"

# Probar conexión
oci iam region list --output table
```

Si ves una lista de regiones, ¡funciona! ✅

## 🚀 Comandos Útiles

### Listar Compute Instances

```powershell
oci compute instance list --compartment-id <tu-compartment-id> --output table
```

### Obtener tu Compartment ID

```powershell
oci iam compartment list --all --output table
```

### Ver tus VMs corriendo

```powershell
oci compute instance list --lifecycle-state RUNNING --output table
```

### Crear VM (ejemplo)

```powershell
oci compute instance launch `
  --availability-domain "AD-1" `
  --compartment-id "ocid1.compartment.oc1..xxx" `
  --shape "VM.Standard.A1.Flex" `
  --shape-config '{"ocpus":2,"memoryInGBs":12}' `
  --image-id "ocid1.image.oc1.xxx" `
  --subnet-id "ocid1.subnet.oc1.xxx" `
  --display-name "whatsapp-agents"
```

### Ver logs de una instancia

```powershell
oci compute console-history capture --instance-id <instance-id>
oci compute console-history get-content --console-history-id <console-history-id>
```

## 🛠️ Crear Deployment Automatizado

Una vez configurado, puedes crear scripts para:

### 1. Crear VM Automáticamente

```powershell
# create-vm.ps1
$compartmentId = "ocid1.compartment.oc1..xxx"
$imageId = "ocid1.image.oc1..xxx"  # Ubuntu 22.04
$subnetId = "ocid1.subnet.oc1..xxx"

oci compute instance launch `
  --compartment-id $compartmentId `
  --availability-domain "AD-1" `
  --display-name "whatsapp-agents" `
  --shape "VM.Standard.A1.Flex" `
  --shape-config '{"ocpus":2,"memoryInGBs":12}' `
  --image-id $imageId `
  --subnet-id $subnetId `
  --assign-public-ip true `
  --metadata file://cloud-init.json
```

### 2. Obtener IP Pública

```powershell
$instanceId = "ocid1.instance.oc1..xxx"

# Get VNIC attachment
$vnicAttachment = oci compute instance list-vnics --instance-id $instanceId --query "data[0].id" --raw-output

# Get public IP
$publicIp = oci network vnic get --vnic-id $vnicAttachment --query "data.""public-ip""" --raw-output

Write-Host "Public IP: $publicIp"
```

### 3. Conectar via SSH

```powershell
$publicIp = "xxx.xxx.xxx.xxx"
$sshKey = "C:\Users\angel\Downloads\ssh-key.key"

ssh -i $sshKey ubuntu@$publicIp
```

## 📚 Referencia Rápida

### Help

```powershell
oci --help
oci compute --help
oci compute instance --help
```

### Output Formats

```powershell
# Table (bonito)
oci compute instance list --output table

# JSON (para scripts)
oci compute instance list --output json

# JSON compacto
oci compute instance list --output json --query "data[].{Name:\"display-name\",IP:\"public-ip\"}"
```

### Configuración Múltiple

```powershell
# Ver profiles
cat "$env:USERPROFILE\.oci\config"

# Usar profile específico
oci compute instance list --profile PROFILE_NAME
```

## 🐛 Troubleshooting

### "NotAuthenticated" Error

```powershell
# Regenerar config
oci setup repair-file-permissions --file "$env:USERPROFILE\.oci\config"

# O reconfigura
oci setup config
```

### "ConfigFileNotFound"

```powershell
# Verifica que existe
Test-Path "$env:USERPROFILE\.oci\config"

# Si no existe, configura de nuevo
oci setup config
```

### "ServiceError: NotAuthorizedOrNotFound"

- Verifica que subiste el API key public a Oracle Cloud
- Verifica que el User OCID y Tenancy OCID sean correctos

### Connection Timeout

- Verifica tu conexión a internet
- Intenta con otra región más cercana

## 🔗 Enlaces Útiles

- **OCI CLI Docs**: https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/
- **Command Reference**: https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/
- **Oracle Cloud Console**: https://cloud.oracle.com

## ⚡ Próximos Pasos

Una vez configurado OCI CLI, puedes:

1. ✅ Crear VMs desde terminal
2. ✅ Automatizar deployments
3. ✅ Gestionar recursos sin entrar al portal web
4. ✅ Crear scripts de CI/CD

¿Listo para instalar? Ejecuta:

```powershell
.\install-oci-cli.ps1
```
