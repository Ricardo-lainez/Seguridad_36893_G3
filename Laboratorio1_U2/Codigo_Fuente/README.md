# Laboratorio de criptografía cliente-servidor

**Universidad de las Fuerzas Armadas ESPE – Matriz Sangolquí**  
**Carrera:** Ingeniería de Software  
**Asignatura:** Seguridad de ingeniería de software  
**NRC:** 36893  
**Proyecto:** Diseño e implementación de un laboratorio de criptografía cliente-servidor  
**Fecha:** Noviembre de 2026

## 1. Descripción

Este proyecto implementa un laboratorio académico aislado de criptografía con arquitectura cliente-servidor. Su propósito es demostrar el uso de mecanismos criptográficos para proteger información ficticia de matrícula, tanto durante su almacenamiento como durante su transmisión por una red.

El laboratorio comprende las actividades A–G:

- **A.** Integridad de archivos mediante SHA-256.
- **B.** Cifrado y descifrado simétrico con AES-256-GCM.
- **C.** Criptografía asimétrica RSA y firma digital RSA-PSS.
- **D.** Acuerdo de secreto mediante X25519/ECDH.
- **E.** Almacenamiento y verificación de contraseñas con Argon2id.
- **F.** Certificado autofirmado y servicio HTTPS mediante TLS.
- **G.** Captura y análisis del tráfico TLS con Wireshark.

El laboratorio utiliza bibliotecas criptográficas conocidas. No implementa algoritmos criptográficos propios.

## 2. Alcance y restricciones

El entorno está destinado exclusivamente a prácticas académicas:

- Se utilizan dos máquinas virtuales en un mismo equipo anfitrión.
- Los datos y las contraseñas utilizados son ficticios.
- La comunicación de laboratorio se realiza mediante una red interna de VirtualBox.
- El servicio HTTPS escucha en el puerto `8443`.
- El certificado del servidor es autofirmado y tiene una vigencia de siete días.
- No se contempla la exposición del servicio a Internet ni su uso en producción.
- No se deben utilizar datos personales, credenciales reales ni claves de uso personal.

## 3. Arquitectura del laboratorio

### 3.1. Máquinas virtuales

Las dos máquinas utilizan Ubuntu 26.04 LTS Desktop y VirtualBox 7.1.4.

| Característica | `cripto-servidor` | `cripto-cliente` |
|---|---|---|
| Sistema operativo | Ubuntu 26.04 LTS Desktop | Ubuntu 26.04 LTS Desktop |
| CPU | 2 | 2 |
| Memoria RAM | 3072 MB | 4096 MB |
| Disco | 25 GB | 25 GB |
| Interfaz interna | `enp0s8` | `enp0s8` |
| Dirección IP interna | `10.10.10.10/24` | `10.10.10.20/24` |
| Nombre de red | `cripto-lan` | `cripto-lan` |
| Función | Servicio HTTPS, certificado y clave privada | Solicitudes HTTPS, validación del certificado y captura de tráfico |

Cada máquina dispone de dos adaptadores:

1. **Adaptador NAT:** utilizado temporalmente para descargar e instalar paquetes. En el entorno documentado aparece con la dirección `10.0.2.15`.
2. **Adaptador de red interna:** conectado a `cripto-lan`, por donde se realiza la comunicación entre cliente y servidor.

La red interna utiliza el segmento `10.10.10.0/24` y no tiene puerta de enlace. Para la captura final de tráfico, el adaptador NAT debe desactivarse, de modo que la comunicación quede aislada en la red interna.

### 3.2. Flujo general

1. El servidor genera el certificado público `server.crt` y conserva la clave privada `server.key`.
2. El cliente recibe únicamente el certificado público.
3. El cliente utiliza ese certificado para validar la identidad del servidor.
4. El cliente realiza solicitudes HTTPS al servidor por el puerto `8443`.
5. TLS protege los datos mientras viajan por la red.
6. Wireshark permite observar la negociación TLS y los registros de aplicación cifrados.

**Importante:** TLS protege la información durante el tránsito. No significa que los datos permanezcan cifrados dentro del servidor después de que la aplicación los recibe y descifra.

## 4. Herramientas y versiones

Las siguientes versiones constan en el informe del laboratorio:

| Herramienta | Versión o referencia | Uso |
|---|---|---|
| VirtualBox | 7.1.4 | Virtualización |
| Ubuntu | 26.04 LTS | Sistema operativo de las máquinas |
| OpenSSL | 3.5.5 | Certificados, claves y pruebas TLS |
| Python | 3.14.4 | Ejecución de los programas |
| `cryptography` | 50.0.2 | AES-GCM, RSA y X25519 |
| `argon2-cffi` | 25.1.0 | Argon2id |
| curl | 8.18.0 | Solicitudes HTTPS |
| tcpdump | 4.99.6 | Captura de tráfico |
| Wireshark | 4.6.4 en la actividad G; instalado desde los repositorios de Ubuntu | Análisis de paquetes |

VirtualBox, Ubuntu y las herramientas del sistema operativo no se instalan desde `requirements.txt`. Ese archivo contiene únicamente las dependencias Python del proyecto.

## 5. Estructura esperada de archivos

La carpeta de trabajo utilizada dentro de las máquinas es `~/lab-crypto`.

```text
lab-crypto/
├── crypto_lab.py
├── server_https.py
├── requirements.txt
├── README.md
└── .gitignore
```

Funciones principales:

| Archivo | Ubicación | Descripción |
|---|---|---|
| `crypto_lab.py` | Cliente y servidor | Comandos de las actividades A–E |
| `server_https.py` | Solo servidor | Servicio HTTPS didáctico |
| `requirements.txt` | Carpeta del proyecto | Dependencias Python fijadas por versión |
| `README.md` | Carpeta del proyecto | Documentación del laboratorio |
| `.gitignore` | Repositorio | Exclusión de claves y archivos de prueba |

Los archivos `server.crt` y `server.key` se generan durante la actividad F. No son dependencias ni deben incluirse en un repositorio público. La clave privada debe permanecer en el servidor.

## 6. Instalación y preparación

### 6.1. Instalar herramientas del sistema

En ambas máquinas virtuales, habilitar temporalmente el adaptador NAT y ejecutar:

```bash
sudo apt update
sudo apt install -y openssl python3 python3-venv python3-pip curl wireshark tcpdump
```

Para transferir archivos mediante SCP y administrar las máquinas por SSH, puede ser necesario instalar el servicio SSH en el servidor y el cliente SSH en el equipo desde el que se realiza la conexión:

```bash
sudo apt install -y openssh-server openssh-client
```

La instalación de SSH es un apoyo para la administración y transferencia de archivos; no es una dependencia Python del laboratorio.

### 6.2. Crear el entorno virtual e instalar dependencias

En cada máquina, dentro de `~/lab-crypto`:

```bash
cd ~/lab-crypto
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Para comprobar las dependencias:

```bash
python -m pip show cryptography argon2-cffi
```

Para consultar los comandos disponibles en el programa:

```bash
python crypto_lab.py --help
```

### 6.3. Copiar los programas

`crypto_lab.py` debe estar disponible en ambas máquinas. `server_https.py` debe estar en `cripto-servidor`.

La transferencia entre máquinas puede realizarse con SCP. Por ejemplo, desde el cliente:

```bash
scp usuario@10.10.10.10:/home/usuario/lab-crypto/server.crt .
```

Sustituir `usuario` por el nombre de usuario real de la máquina. No transferir `server.key`.

## 7. Configuración de la red interna

La interfaz de red interna utilizada es `enp0s8`.

### 7.1. Configurar el servidor

En `cripto-servidor`:

```bash
sudo nmcli connection add type ethernet ifname enp0s8 con-name cripto-lan \
  ipv4.method manual ipv4.addresses 10.10.10.10/24 ipv4.never-default yes \
  ipv6.method disabled

sudo nmcli connection up cripto-lan
```

### 7.2. Configurar el cliente

En `cripto-cliente`:

```bash
sudo nmcli connection add type ethernet ifname enp0s8 con-name cripto-lan \
  ipv4.method manual ipv4.addresses 10.10.10.20/24 ipv4.never-default yes \
  ipv6.method disabled

sudo nmcli connection up cripto-lan
```

Si ya existe una conexión automática por DHCP en `enp0s8` que interfiere con `cripto-lan`, se debe revisar y retirar esa conexión conflictiva antes de activar la configuración estática.

### 7.3. Comprobar conectividad

En el cliente:

```bash
ping -c 4 10.10.10.10
```

En el servidor:

```bash
ping -c 4 10.10.10.20
```

En la preparación documentada se obtuvieron cuatro paquetes enviados y cuatro recibidos, con 0 % de pérdida en ambos sentidos.

## 8. Ejecución de las actividades

Antes de ejecutar los comandos de `crypto_lab.py`, activar el entorno virtual:

```bash
cd ~/lab-crypto
source .venv/bin/activate
```

Los comandos siguientes corresponden al procedimiento documentado. Si se necesita consultar parámetros adicionales de un subcomando, utilizar `python crypto_lab.py --help` o la ayuda del subcomando.

### 8.1. Actividad A: integridad SHA-256 (T01)

En `cripto-cliente`:

```bash
echo "Acta de matrícula de prueba" > acta.txt
sha256sum acta.txt
python crypto_lab.py hash acta.txt

echo "Cambio no autorizado" >> acta.txt
sha256sum acta.txt
python crypto_lab.py hash acta.txt
```

**Resultado esperado:** el hash debe cambiar después de modificar el archivo. `sha256sum` y el programa deben coincidir para cada estado del archivo.

### 8.2. Actividad B: cifrado AES-256-GCM (T02 y T03)

Crear el archivo de prueba y ejecutar:

```bash
echo "Acta de matrícula de prueba" > acta.txt
python crypto_lab.py encrypt acta.txt
python crypto_lab.py decrypt acta.txt.aesgcm
cmp acta.txt acta.recovered
```

**T02 – Resultado esperado:** el descifrado debe superar la autenticación GCM y recuperar un archivo idéntico al original. En la ejecución documentada, el archivo cifrado tuvo 57 bytes y el recuperado 29 bytes.

**T03 – Prueba negativa:** se realiza una copia de respaldo y se altera un byte del archivo cifrado:

```bash
cp acta.txt.aesgcm acta.txt.aesgcm.bak

python - <<'PY'
from pathlib import Path

archivo = Path("acta.txt.aesgcm")
datos = bytearray(archivo.read_bytes())
datos[12] ^= 1
archivo.write_bytes(datos)
PY

python crypto_lab.py decrypt acta.txt.aesgcm
```

El descifrado debe ser rechazado por fallo de autenticación (`InvalidTag`). Para restaurar el archivo de prueba:

```bash
cp acta.txt.aesgcm.bak acta.txt.aesgcm
```

**Nota sobre el nombre de la clave:** el informe registra `aes.key`, mientras que el resumen de implementación describe una clave con nombre `<archivo>.key`. El nombre efectivo depende de la versión del programa entregada. Revisar el mensaje que muestra `encrypt` y la ayuda del programa antes de utilizar la clave manualmente. La clave debe mantenerse separada del archivo cifrado y protegida con permisos restrictivos.

### 8.3. Actividad C: RSA y firma digital (T04 y T05)

Generar el par de claves:

```bash
python crypto_lab.py rsa-keys
```

El programa solicita una passphrase para proteger la clave privada. La clave privada `rsa_private.pem` debe conservarse protegida; la clave pública `rsa_public.pem` puede compartirse para verificar firmas.

Firmar y verificar el documento:

```bash
python crypto_lab.py sign acta.txt
python crypto_lab.py verify acta.txt acta.txt.sig
```

**T04 – Resultado esperado:** la verificación de la firma original debe ser válida. El informe registra una firma RSA-PSS con SHA-256 de 384 bytes.

**T05 – Pruebas negativas:** modificar el documento y verificarlo con la firma original:

```bash
cp acta.txt acta_modificada.txt
echo "Cambio no autorizado en la matricula" >> acta_modificada.txt
python crypto_lab.py verify acta_modificada.txt acta.txt.sig
```

También se puede alterar una copia de la firma para comprobar que el programa la rechaza. El informe documenta el rechazo tanto de un documento modificado como de una firma alterada.

El resumen del programa también registra los subcomandos `rsa-wrap` y `rsa-unlock` para la demostración de RSA-OAEP. Consultar `python crypto_lab.py --help` para conocer sus argumentos exactos; no se deben asumir parámetros que no estén indicados por el programa.

### 8.4. Actividad D: acuerdo de secreto X25519/ECDH (T06)

En `cripto-cliente`:

```bash
python crypto_lab.py ecdh-demo
```

**Resultado esperado:** los dos participantes deben obtener el mismo secreto compartido sin transmitir directamente sus claves privadas ni el secreto. En el laboratorio también se comprobó la derivación de claves mediante HKDF-SHA256.

### 8.5. Actividad E: almacenamiento de contraseñas Argon2id (T07)

Generar el hash de una contraseña ficticia:

```bash
python crypto_lab.py password-hash
```

Consultar el archivo generado:

```bash
cat password.hash
```

Verificar la contraseña mediante el procedimiento del programa:

```bash
python crypto_lab.py password-check "$(cat password.hash)"
```

Se deben realizar dos comprobaciones: una con la contraseña correcta y otra con una contraseña incorrecta.

**Resultado esperado:** la contraseña correcta es aceptada y la incorrecta es rechazada. La configuración documentada utiliza Argon2id versión 19, memoria de 65536 KiB, tres iteraciones y paralelismo cuatro.

No utilizar contraseñas reales ni publicar el contenido de archivos de hashes de uso personal.

### 8.6. Actividad F: certificado y servicio HTTPS (T08)

Esta actividad requiere las dos máquinas virtuales.

#### Paso 1. Generar el certificado en el servidor

En `cripto-servidor`, dentro de `~/lab-crypto`:

```bash
openssl req -x509 -newkey rsa:3072 -sha256 -days 7 -nodes \
  -keyout server.key -out server.crt \
  -subj "/CN=lab.local" \
  -addext "subjectAltName=DNS:lab.local,IP:10.10.10.10"
```

Proteger la clave privada:

```bash
chmod 600 server.key
```

Inspeccionar el certificado y los permisos:

```bash
ls -l server.crt server.key

openssl x509 -in server.crt -noout \
  -subject -issuer -dates -ext subjectAltName
```

El certificado es público; `server.key` es secreto y debe permanecer exclusivamente en el servidor.

#### Paso 2. Iniciar el servicio HTTPS

En `cripto-servidor`:

```bash
cd ~/lab-crypto
python3 server_https.py
```

El servicio debe indicar que escucha en `0.0.0.0:8443`. Mantener esta terminal abierta mientras se realizan las pruebas desde el cliente.

#### Paso 3. Transferir únicamente el certificado público

Desde `cripto-cliente`:

```bash
scp usuario@10.10.10.10:/home/usuario/lab-crypto/server.crt .
ls -l server.crt
```

Ajustar el usuario y la ruta al entorno real. No copiar `server.key`.

#### Paso 4. Probar una solicitud GET

En `cripto-cliente`:

```bash
curl -v --cacert server.crt https://10.10.10.10:8443/
```

**Resultado esperado:** conexión HTTPS validada y respuesta HTTP `200 OK`.

#### Paso 5. Probar una solicitud POST

```bash
curl --cacert server.crt -X POST https://10.10.10.10:8443/ \
  -H 'Content-Type: text/plain' \
  --data 'matricula=ESTUDIANTE-DE-PRUEBA'
```

La respuesta documentada es:

```json
{"resultado":"solicitud recibida por HTTPS"}
```

En la terminal del servidor debe observarse la recepción de la solicitud dentro de TLS.

#### Paso 6. Inspeccionar la negociación TLS

Desde el cliente:

```bash
openssl s_client -connect 10.10.10.10:8443 \
  -CAfile server.crt -tls1_3
```

En la ejecución documentada se obtuvo:

- Protocolo: TLS 1.3.
- Suite criptográfica: `TLS_AES_256_GCM_SHA384`.
- Grupo de intercambio: `X25519MLKEM768`.
- Tipo de firma: `rsa_pss_rsae_sha256`.
- Verificación: `Verify return code: 0 (ok)`.

**T08 – Resultado esperado:** solicitudes GET y POST satisfactorias, certificado validado y conexión TLS 1.3.

### 8.7. Actividad G: captura y análisis con Wireshark (T09)

La captura se realiza en `cripto-cliente`, sobre la interfaz `enp0s8`, conectada a `cripto-lan`.

1. Desactivar el adaptador NAT de las máquinas virtuales para la captura final.
2. Abrir Wireshark en `cripto-cliente`.
3. Seleccionar la interfaz `enp0s8` e iniciar la captura.
4. Con el servidor HTTPS activo, generar una solicitud desde otra terminal del cliente:

```bash
curl --cacert server.crt https://10.10.10.10:8443/
```

5. Detener la captura y aplicar los filtros de visualización.

**Filtro para el tráfico del servicio:**

```text
tcp.port == 8443
```

**Filtro para los mensajes ClientHello y ServerHello:**

```text
tls.handshake.type == 1 || tls.handshake.type == 2
```

Se deben identificar:

- `ClientHello`: mensaje inicial de negociación enviado por el cliente.
- `ServerHello`: respuesta del servidor con los parámetros seleccionados.
- `Application Data`: registros que transportan datos de aplicación cifrados.

En la captura documentada se registraron 21 paquetes. Se identificaron `ClientHello` en el paquete 4, `ServerHello` en el paquete 6 y un registro `Application Data` en el paquete 10. Estos números corresponden a esa ejecución y pueden variar en nuevas capturas.

Guardar la captura con el nombre:

```text
T09_Captura_Trafico_TLS.pcapng
```

Volver a abrir el archivo guardado para comprobar que puede inspeccionarse en Wireshark.

**T09 – Resultado esperado:** identificar la negociación TLS y registros de aplicación cifrados, y conservar el archivo PCAPNG como evidencia.

## 9. Matriz de pruebas y resultados

La matriz del informe final registra los siguientes resultados:

| ID | Prueba | Resultado documentado |
|---|---|---|
| T01 | Calcular SHA-256 y modificar un archivo | El hash cambió después de la modificación; `sha256sum` y el programa coincidieron. |
| T02 | Cifrar y descifrar con AES-256-GCM | Autenticación válida y recuperación idéntica del archivo. |
| T03 | Alterar un bit del archivo cifrado | Descifrado rechazado por fallo de autenticación (`InvalidTag`). |
| T04 | Generar RSA, firmar y verificar | Par de claves generado y firma RSA-PSS válida. |
| T05 | Verificar un documento y una firma alterados | Ambas verificaciones fueron rechazadas. |
| T06 | Ejecutar X25519/ECDH | Los participantes obtuvieron el mismo secreto compartido; las claves derivadas coincidieron. |
| T07 | Verificar contraseña con Argon2id | La contraseña correcta fue aceptada y la incorrecta rechazada. |
| T08 | Solicitar el servicio HTTPS | GET y POST respondieron HTTP 200 OK; certificado validado y TLS 1.3. |
| T09 | Capturar tráfico TLS | Se identificaron ClientHello, ServerHello y Application Data; captura PCAPNG conservada. |

## 10. Evidencias y entregables

Las evidencias deben mostrar, cuando corresponda, el nombre de la máquina virtual y los resultados relevantes de cada prueba. La guía de trabajo utiliza identificadores E01, E02, etc., asociados a las pruebas T01–T09.

Entregables relacionados con el proyecto:

- Informe final del laboratorio.
- `requirements.txt`.
- `README.md`.
- Código `crypto_lab.py`.
- Código `server_https.py`.
- Máquinas virtuales exportadas (`cripto-cliente.ova` y `cripto-servidor.ova`).
- Guía de importación de las máquinas virtuales.
- Diagramas de arquitectura y flujo criptográfico.
- Captura `T09_Captura_Trafico_TLS.pcapng`.
- Evidencias de ejecución de las pruebas.

Los archivos `.ova`, los diagramas, el código y la captura se entregan como elementos separados cuando corresponda. Este README no sustituye esos archivos.

## 11. Consideraciones de seguridad

- Utilizar únicamente datos y contraseñas ficticios.
- No compartir `server.key`, `rsa_private.pem`, claves AES ni passphrases.
- No almacenar claves privadas, certificados de práctica, hashes de contraseñas ni archivos de prueba sensibles en repositorios públicos.
- Mantener las claves privadas con permisos restrictivos; en el laboratorio se utilizó `chmod 600`.
- No transferir la clave privada del servidor al cliente.
- No utilizar `curl -k` ni desactivar la validación del certificado. Utilizar `--cacert server.crt`.
- No exponer el servicio HTTPS a Internet.
- Desactivar el adaptador NAT durante la captura final para conservar el aislamiento de la red interna.
- El certificado autofirmado es apropiado para esta práctica controlada; no equivale a un certificado emitido por una autoridad certificadora pública.
- Al finalizar, eliminar las claves y certificados de práctica conforme a las indicaciones del laboratorio.

## 12. Solución de problemas observados

| Problema | Causa identificada | Solución aplicada |
|---|---|---|
| El instalador de Ubuntu no arrancaba (`vmwgfx`) | Incompatibilidad del controlador gráfico en la configuración de VirtualBox | Cambiar a `VBoxSVGA` y asignar 128 MB de memoria de vídeo. |
| La máquina volvía a iniciar el instalador | La ISO seguía montada y el DVD tenía prioridad de arranque | Colocar el disco virtual primero y expulsar la ISO. |
| `cripto-lan` no se activaba | Una conexión automática DHCP interfería con la IP estática | Retirar la conexión conflictiva y activar `cripto-lan`. |
| El servidor tenía la IP del cliente | Se ejecutó la configuración en la máquina equivocada | Verificar el nombre de la VM y asignar `10.10.10.10/24` al servidor y `10.10.10.20/24` al cliente. |
| El portapapeles compartido no funcionaba | Limitación de la sesión gráfica de Ubuntu con esta configuración | Transferir archivos mediante SCP y administrar por SSH cuando esté disponible. |
| El equipo se quedaba sin memoria con ambas VM encendidas | Recursos limitados del equipo anfitrión | Instalar o trabajar con una máquina a la vez y cerrar aplicaciones innecesarias. |

## 13. Referencia de comandos del programa

Los subcomandos documentados de `crypto_lab.py` son:

| Actividad | Subcomandos |
|---|---|
| A – SHA-256 | `hash` |
| B – AES-256-GCM | `encrypt`, `decrypt` |
| C – RSA y firma | `rsa-keys`, `sign`, `verify`, `rsa-wrap`, `rsa-unlock` |
| D – X25519/ECDH | `ecdh-demo` |
| E – Argon2id | `password-hash`, `password-check` |

Para ver la sintaxis exacta de cada operación en la versión entregada:

```bash
python crypto_lab.py --help
```

---

**Fin de la documentación.**
