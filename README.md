<div align="center">

# MercadoVoz

### Registros comerciales en lenguaje natural con confirmación humana

MercadoVoz es un sistema pensado para pequeños comerciantes de **Cuenca, Ecuador**, que necesitan registrar ventas, gastos, cuentas por cobrar y abonos de forma rápida usando lenguaje cotidiano.

La regla principal es simple:

> **Ninguna operación financiera se guarda hasta que el usuario la revise y la confirme.**

<br>

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

<br>

![Estado](https://img.shields.io/badge/Estado-Piloto_Privado-2563EB?style=flat-square)
![Core](https://img.shields.io/badge/Core_Engine-Funcional-16A34A?style=flat-square)
![Validación](https://img.shields.io/badge/Validación_de_Mercado-Pendiente-D97706?style=flat-square)

</div>

---

## Descripción general

Muchos pequeños comerciantes administran su negocio usando:

- cuadernos;
- memoria;
- calculadora;
- mensajes de WhatsApp;
- notas informales.

Esto puede provocar:

- ventas que no se registran;
- gastos olvidados;
- dificultad para controlar fiados;
- abonos mal anotados;
- confusión entre dinero personal y dinero del negocio;
- poca claridad sobre cuánto debe cada cliente.

MercadoVoz busca mantener la sencillez del lenguaje cotidiano, pero convertirlo en datos comerciales estructurados.

Un comerciante puede escribir:

```text
María quedó debiendo 12
```

MercadoVoz puede interpretarlo como:

```text
Operación: RECEIVABLE
Cliente: María
Monto: $12
```

Pero esa operación **no se guarda inmediatamente**.

Primero, el sistema muestra la interpretación al usuario:

```text
Cuenta por cobrar

Cliente: María
Monto: $12

[ Confirmar ]
[ Corregir ]
[ Cancelar ]
```

Solo después de la confirmación se persiste la operación.

---

## Principio principal

MercadoVoz sigue una regla de seguridad muy clara:

> **Si el sistema no tiene suficiente certeza, pregunta, pide aclaración o se abstiene. Nunca inventa una transacción.**

Por ejemplo:

```text
me pagó todo lo de ayer
```

no contiene suficiente información para determinar de forma segura:

- quién pagó;
- qué deuda se está mencionando;
- cuánto dinero debe registrarse.

MercadoVoz puede usar contexto controlado cuando está disponible, pero no debe fabricar información financiera que falta.

---

## Operaciones principales

El núcleo actual está centrado en cuatro operaciones financieras.

### SALE

Una venta realizada.

```text
vendí 3 libras de tomate a 2 dólares
```

Posible resultado estructurado:

```json
{
  "operation": "SALE",
  "product": "tomate",
  "quantity": 3,
  "unit": "libra",
  "unit_price": 2,
  "total": 6
}
```

---

### EXPENSE

Un gasto del negocio.

```text
gasté 5 en transporte
```

Posible resultado:

```json
{
  "operation": "EXPENSE",
  "description": "transporte",
  "amount": 5
}
```

---

### RECEIVABLE

Dinero que un cliente queda debiendo al negocio.

```text
Carlos quedó debiendo 10
```

Posible resultado:

```json
{
  "operation": "RECEIVABLE",
  "customer": "Carlos",
  "amount": 10
}
```

---

### PAYMENT_RECEIVED

Pago o abono aplicado a una deuda existente.

```text
Carlos me abonó 5
```

Posible resultado:

```json
{
  "operation": "PAYMENT_RECEIVED",
  "customer": "Carlos",
  "amount": 5
}
```

Inventario y compras han sido explorados, pero todavía no forman parte del núcleo principal.

---

## Cómo funciona

```text
Entrada en lenguaje natural
        │
        ▼
Normalización
        │
        ▼
Motor de Interpretación
        │
        ▼
Capa de Seguridad
        │
        ▼
Capa de Contexto
        │
        ▼
Propuesta de operación
        │
        ▼
Confirmación humana
        │
        ▼
Persistencia
        │
        ▼
Trazabilidad / Audit Trail
```

MercadoVoz no es simplemente un parser de texto.

Es una cadena de interpretación diseñada específicamente alrededor de la seguridad financiera.

---

## Motor de Interpretación

El Motor de Interpretación intenta extraer información como:

- intención;
- tipo de operación;
- monto;
- cantidad;
- producto;
- cliente;
- unidad;
- precio unitario.

Ejemplo:

```text
vendí 5 libras de tomate a 2 cada una
```

puede producir:

```json
{
  "operation": "SALE",
  "product": "tomate",
  "quantity": 5,
  "unit": "libra",
  "unit_price": 2,
  "total": 10
}
```

Actualmente el motor es principalmente **determinista**.

El núcleo no depende obligatoriamente de un LLM.

Esto es intencional.

Para operaciones financieras, el comportamiento determinista ofrece ventajas importantes:

- reproducibilidad;
- costos predecibles;
- baja latencia;
- explicabilidad;
- pruebas automatizadas precisas;
- depuración más sencilla;
- menor riesgo de alucinaciones con datos monetarios.

Los LLM pueden ser útiles para tareas auxiliares en el futuro, pero el núcleo financiero debe mantenerse controlado.

---

## Capa de Seguridad

La Capa de Seguridad es uno de los componentes más importantes de MercadoVoz.

Su objetivo es detectar interpretaciones potencialmente peligrosas antes de que una operación llegue a persistencia.

Por ejemplo:

```text
hoy hice como 40
```

no debería convertirse automáticamente en:

```text
SALE = $40
```

porque:

```text
como 40
```

indica aproximación.

Otro ejemplo:

```text
saqué cinco para la casa
```

podría describir un retiro personal y no un gasto del negocio.

Registrarlo automáticamente como:

```text
EXPENSE = $5
```

podría contaminar los registros comerciales.

La capa de seguridad considera casos como:

- montos aproximados;
- precio unitario vs total;
- cantidades coordinadas;
- operaciones compuestas;
- dinero personal vs dinero del negocio;
- creación de deuda vs estado de deuda;
- clientes faltantes;
- contexto faltante;
- referencias ambiguas;
- múltiples interpretaciones posibles.

---

## Seguridad semántica

Considera estas dos frases:

```text
Juan quedó debiendo 10
```

y:

```text
Juan todavía debe 10
```

Parecen similares, pero representan estados distintos.

La primera puede significar la creación de una nueva deuda:

```text
RECEIVABLE +$10
```

La segunda puede simplemente describir una deuda que ya existía.

Un sistema ingenuo podría registrar otros $10 y duplicar la deuda del cliente.

MercadoVoz está diseñado para evitar precisamente este tipo de errores financieros.

---

## Capa de Contexto

Las personas hablan usando contexto.

Ejemplo:

```text
María debe 20
```

y después:

```text
me abonó cinco
```

La segunda frase no menciona a María.

MercadoVoz puede mantener contexto controlado como:

```text
active_customer = María
active_receivable = 20
```

y proponer:

```json
{
  "operation": "PAYMENT_RECEIVED",
  "customer": "María",
  "amount": 5,
  "remaining_balance": 15
}
```

Sin embargo, la propuesta sigue necesitando confirmación del usuario.

El contexto no se trata como una memoria conversacional infinita.

Cada referencia contextual puede incluir:

```text
source
created_at
expires_at
invalidation_rules
```

Esto limita cuánto tiempo la información implícita puede influir en operaciones financieras.

---

## Motor de Confirmación

Las operaciones financieras pasan por estados explícitos.

```text
PROPOSED
CONFIRMED
CORRECTED
REJECTED
CANCELLED
```

Ejemplo:

```text
MercadoVoz entendió:

VENTA

Producto: Tomate
Cantidad: 5 lb
Total: $10

[ Confirmar ]
[ Corregir ]
[ Cancelar ]
```

El sistema funciona bajo un modelo **human-in-the-loop**.

La interpretación es automatizada.

La decisión financiera final no.

---

## Motor de Corrección

Si una interpretación es incorrecta, el usuario no debería tener que repetir toda la operación.

Ejemplo:

```text
MercadoVoz:
Monto: $5
```

Usuario:

```text
no, eran seis
```

El motor de corrección puede actualizar solo el campo relevante:

```text
Monto: $6
```

sin reconstruir toda la operación.

Los campos que pueden corregirse incluyen:

- tipo de operación;
- monto;
- cantidad;
- producto;
- cliente;
- unidad;
- precio unitario.

---

## Trazabilidad

Cada operación financiera puede conservar un registro de trazabilidad.

El audit trail puede incluir:

```text
original_text
normalized_text
engine_version
context_used
fields_extracted
warnings
safety_rules_triggered
initial_proposal
corrections
confirmation
final_operation
```

Esto permite responder preguntas como:

> ¿Por qué MercadoVoz terminó guardando esta operación de esta manera?

Para un sistema que maneja información financiera, este nivel de explicabilidad es importante.

---

## Arquitectura

```text
┌─────────────────────────────┐
│           Cliente           │
│      Navegador / Móvil      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Next.js / React        │
│        TypeScript           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          FastAPI            │
│          Python             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    Motor de Interpretación  │
├─────────────────────────────┤
│     Capa de Seguridad       │
│      Capa de Contexto       │
│    Motor de Confirmación    │
│      Motor de Corrección    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         SQLite WAL          │
└─────────────────────────────┘
```

---

## Tecnologías

### Frontend

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

El frontend se encarga de:

- entrada de texto;
- vista previa de la interpretación;
- correcciones;
- confirmación de operaciones;
- historial;
- consentimiento;
- interfaz responsive.

La interfaz está pensada con un enfoque **mobile-first**, porque el usuario objetivo probablemente utilizará el sistema desde un teléfono.

---

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

FastAPI conecta el frontend con el motor de interpretación.

Ejemplo de endpoints:

```text
POST /interpret
POST /confirm
POST /correct
GET  /history
```

FastAPI facilita:

- validación mediante schemas;
- documentación automática de la API;
- modelos tipados;
- APIs ligeras;
- integración directa con lógica en Python.

---

### Base de datos

![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

El piloto actual utiliza:

```text
SQLite + WAL
```

WAL significa:

```text
Write-Ahead Logging
```

y mejora el comportamiento de SQLite cuando existen lecturas y escrituras concurrentes.

SQLite es adecuado en esta fase porque MercadoVoz todavía está en etapa de piloto y no necesita infraestructura distribuida para grandes volúmenes de usuarios.

La arquitectura actual está pensada alrededor de un backend controlado.

---

## Infraestructura

La infraestructura del piloto está preparada sobre una máquina virtual de Oracle Cloud.

```text
Oracle Cloud
US East — Ashburn

Ampere A1 Flex
2 OCPU
12 GB RAM
Ubuntu 24.04 ARM64
50 GB de almacenamiento
```

Arquitectura esperada:

```text
                    Internet
                       │
                       ▼
                 ┌───────────┐
                 │   Nginx   │
                 └─────┬─────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
     Next.js :3000             FastAPI :8000
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
                    SQLite
```

Nginx puede enrutar:

```text
/
```

hacia Next.js y:

```text
/api/
```

hacia FastAPI.

---

## Gestión de procesos

### PM2

Se utiliza para mantener Next.js ejecutándose.

```bash
pm2 start ...
```

PM2 permite mantener la aplicación activa después de cerrar la sesión SSH y reiniciarla automáticamente ante fallos.

### systemd

FastAPI está pensado para ejecutarse como un servicio Linux administrado mediante `systemd`.

Esto permite:

- inicio automático;
- reinicios;
- logs;
- gestión a nivel del sistema operativo.

---

## Seguridad del servidor

![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

Las medidas de seguridad incluyen:

- autenticación mediante claves SSH;
- firewall UFW;
- Fail2ban;
- puertos de entrada controlados;
- Nginx como reverse proxy;
- futura terminación HTTPS.

El objetivo es exponer públicamente únicamente los servicios necesarios.

---

## Estructura del repositorio

MercadoVoz utiliza una estructura tipo monorepo.

```text
mercadovoz/
│
├── apps/
│   ├── web/
│   └── api/
│
├── engine/
│
├── tests/
│
├── research/
│
├── docs/
│
├── scripts/
│
├── data/
│
├── .github/
│
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── AGENTS.md
```

### apps/web

Frontend en Next.js.

### apps/api

Capa de API basada en FastAPI.

### engine

Lógica principal de interpretación y seguridad financiera.

### tests

Pruebas automatizadas y casos de evaluación.

### research

Material de investigación utilizado durante el desarrollo.

### docs

Documentación técnica y de producto.

### scripts

Utilidades de desarrollo, evaluación y operación.

### data

Datos locales controlados y artefactos de desarrollo no sensibles.

---

## Flujo de Git

Ramas principales:

```text
main
develop
```

Ramas de trabajo:

```text
feature/*
fix/*
docs/*
chore/*
hotfix/*
```

`main` debe mantenerse desplegable.

`develop` funciona como rama principal de integración durante el desarrollo activo.

---

## Evaluación técnica

MercadoVoz no se evaluó únicamente con unas pocas frases escritas manualmente.

Durante el desarrollo se utilizaron diferentes categorías de datasets:

```text
SYNTHETIC
WEB_DERIVED
WEB_DERIVED_MULTISOURCE
REAL_DEVELOPMENT
REAL_HELDOUT
```

También se construyó un benchmark externo basado principalmente en investigación sobre lenguaje y comportamiento comercial de pequeños comerciantes de **Cuenca y Ecuador**.

El benchmark contiene:

```text
240 casos externos
```

Estos casos cubren aspectos como:

- ventas;
- gastos;
- cuentas por cobrar;
- abonos;
- contexto;
- operaciones compuestas;
- lenguaje financiero ambiguo;
- vocabulario comercial;
- interpretaciones inseguras.

La evaluación técnica correspondiente alcanzó:

```text
TECHNICAL_STATUS = TECHNICAL_GENERALIZATION_GO
```

sin violaciones monetarias críticas conocidas en esa evaluación.

Sin embargo:

```text
TECHNICAL_GENERALIZATION_GO ≠ FIELD_VALIDATED ≠ MARKET_VALIDATED
```

Superar evaluaciones técnicas no demuestra que comerciantes reales encuentren el producto útil o cómodo.

La validación real todavía está pendiente.

---

## Estado del proyecto

| Componente | Estado |
|---|---|
| Idea | Completado |
| Investigación | Completado |
| Prueba de concepto | Completado |
| Parser determinista | Completado |
| Motor de seguridad | Completado |
| Capa de contexto | Completado |
| Motor de confirmación | Completado |
| Motor de corrección | Completado |
| Core Engine | Completado |
| Benchmark externo | Completado |
| MVP de texto | Completado |
| Preparación de piloto privado | Completado |
| Repositorio de GitHub | Activo |
| Despliegue en Oracle Cloud | HTTP temporal; engine 1.0.0 |
| Robustez/generalización | Engine 1.1.0 aprobado localmente |
| Primer piloto real | P01 inició; ronda sin outcomes terminales ni lock |
| Interfaz de voz | Pendiente |
| Validación de mercado | Pendiente |

---

## Etapa actual

MercadoVoz ya alcanzó un hito técnico importante:

```text
texto
  ↓
interpretación
  ↓
seguridad
  ↓
contexto
  ↓
propuesta
  ↓
confirmación
  ↓
operación estructurada
```

La siguiente gran pregunta ya no es únicamente:

> ¿Puede el motor interpretar lenguaje comercial?

Ahora es:

> ¿Los comerciantes reales preferirán este modelo de interacción frente a sus métodos actuales?

Eso requiere validación en el mundo real.

---

## ¿Por qué texto antes que voz?

La voz forma parte de la visión de largo plazo, pero intencionalmente todavía no es la prioridad.

El flujo futuro podría ser:

```text
Micrófono
    │
    ▼
Speech-to-text
    │
    ▼
MercadoVoz
    │
    ▼
Interpretación
    │
    ▼
Confirmación
```

Sin embargo, agregar reconocimiento de voz no soluciona un mal modelo de interacción.

Primero hay que validar que:

```text
lenguaje natural → operación financiera segura
```

sea realmente útil para los comerciantes.

Si los usuarios reales demuestran que escribir resulta incómodo, la voz será un siguiente paso natural.

---

## Principios de diseño

### Confirmación humana antes que automatización silenciosa

Las operaciones financieras no deben generarse silenciosamente a partir de lenguaje incierto.

### Explicabilidad antes que comportamiento de caja negra

El sistema debería poder explicar cómo interpretó una operación.

### Determinismo cuando hay dinero involucrado

La lógica financiera principal debe mantenerse reproducible y testeable.

### Contexto con límites

El contexto es útil, pero debe tener origen, alcance y expiración claros.

### Abstenerse también es una respuesta válida

No interpretar una frase cuando existe incertidumbre es mejor que inventar una transacción.

### Validación real antes que confianza en benchmarks

Las pruebas técnicas reducen riesgos.

No reemplazan a los usuarios reales.

---

## Ejemplo completo

Entrada:

```text
Juan me abonó cinco
```

El sistema puede resolver el contexto controlado:

```text
active_customer = Juan
active_receivable = $20
```

Luego genera una propuesta:

```text
Operación: PAYMENT_RECEIVED
Cliente: Juan
Monto: $5
Saldo anterior: $20
Nuevo saldo: $15
```

El usuario ve:

```text
Juan abonó $5

Saldo pendiente: $15

[ Confirmar ]
[ Corregir ]
[ Cancelar ]
```

Solo después de:

```text
CONFIRMED
```

se persiste la operación financiera final.

---

## Visión a largo plazo

El objetivo es hacer que el registro de operaciones comerciales se sienta más parecido a una conversación normal que a un sistema contable tradicional.

Un comerciante podría escribir o decir:

```text
vendí cinco libras de papa a dos dólares
```

```text
gasté tres en pasajes
```

```text
María quedó debiendo diez
```

```text
María abonó cinco
```

y MercadoVoz podría generar al final del día:

```text
Ventas
$145

Gastos
$18

Por cobrar
$37

Abonos recibidos
$22
```

sin exigir que el comerciante aprenda a utilizar un software contable complejo.

---

## Qué NO es MercadoVoz

Actualmente MercadoVoz **no es**:

- un sistema contable completo;
- un sistema tributario;
- un ERP;
- un reemplazo de un contador profesional;
- un producto comercial validado en el mercado;
- un sistema de voz todavía;
- un agente financiero autónomo.

Actualmente es un sistema experimental enfocado en:

> **transformar lenguaje natural en registros financieros estructurados y confirmados por el usuario, sin inventar movimientos.**

---

## Roadmap

```text
Motor de interpretación
        ✅
        │
Seguridad y detección de ambigüedad
        ✅
        │
Contexto controlado
        ✅
        │
Confirmación y corrección
        ✅
        │
Evaluación externa
        ✅
        │
MVP de texto
        ✅
        │
Despliegue Oracle Cloud
        🔜
        │
Piloto con comerciantes reales
        ⏳
        │
Validación de usabilidad
        ⏳
        │
Validación de mercado
        ⏳
        │
Entrada por voz
        ⏳
```

---

## Contribuciones

MercadoVoz se encuentra actualmente en una etapa temprana de desarrollo y validación.

Antes de contribuir, revisa:

```text
CONTRIBUTING.md
```

Para información relacionada con seguridad:

```text
SECURITY.md
```

Las convenciones internas de desarrollo y las instrucciones para agentes pueden encontrarse en:

```text
AGENTS.md
```

---

## Seguridad

No reportes vulnerabilidades de seguridad mediante issues públicos de GitHub.

Sigue el proceso documentado en:

```text
SECURITY.md
```

La integridad de los datos y la corrección financiera se consideran aspectos de primera importancia en este proyecto.

---

## Autor

**David Mendez**

Full-Stack Developer  
Universidad Católica de Cuenca  
Cuenca, Ecuador

[![GitHub](https://img.shields.io/badge/GitHub-lildavicho-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lildavicho)

---

<div align="center">

### MercadoVoz

**Lenguaje natural para registrar operaciones comerciales sin inventar movimientos financieros.**

<sub>Construido para experimentar, validar y aprender con pequeños comerciantes reales.</sub>

</div>
