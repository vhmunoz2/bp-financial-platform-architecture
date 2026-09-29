# Arquitectura de banca digital para BP

Propuesta de arquitectura para una plataforma de banca digital que permite a los clientes consultar productos y movimientos, hacer transferencias entre cuentas propias o interbancarias, pagar y recibir notificaciones. El repositorio contiene el modelo C4 en Draw.io, exportaciones de sus vistas y el documento de propuesta en DOCX y PDF.

> **Alcance:** es un diseño de referencia para el ejercicio. Las capacidades, proveedores, objetivos de disponibilidad, costos, RTO/RPO y obligaciones regulatorias concretas deben validarse con BP, sus equipos de seguridad, operaciones, cumplimiento y asesoría jurídica antes de construir o contratar servicios.

## Entregables

- [Propuesta en PDF](output/docx/Propuesta_Arquitectura_Banca_Digital_BP.pdf)
- [Propuesta editable en DOCX](output/docx/Propuesta_Arquitectura_Banca_Digital_BP.docx)
- [Modelo C4 e infraestructura, multipágina Draw.io](diagrams/Arquitectura_C4_Banca_Digital_BP.drawio)
- [Vista C1: Contexto](diagrams/Arquitectura_C4_Banca_Digital_BP-C1%20-%20Contexto%20C4.drawio.png)
- [Vista C2: Contenedores](diagrams/Arquitectura_C4_Banca_Digital_BP-C2%20-%20Contenedores.drawio.png)
- [Vista C3: Componentes](diagrams/Arquitectura_C4_Banca_Digital_BP-C3%20Componentes.drawio.png)
- [Vista de infraestructura Azure](diagrams/Arquitectura_C4_Banca_Digital_BP-Infraestructura.drawio.png)

El archivo `.drawio` es la fuente editable de las cuatro vistas. Las imágenes PNG sirven para consulta rápida; el DOCX/PDF reúne la explicación de la propuesta.

## Alcance funcional

La solución cubre los siguientes casos principales:

1. **Ingreso y onboarding:** autenticación de clientes existentes; incorporación móvil de nuevos clientes con verificación de identidad y reconocimiento facial.
2. **Consulta:** visualización de datos básicos, productos y movimientos obtenidos desde el Core BP y el sistema complementario de información detallada.
3. **Transferencias:** transferencias entre cuentas propias y transferencias interbancarias mediante los rieles/adaptadores habilitados por BP y sus partners.
4. **Pagos:** iniciación, validación, envío al sistema que corresponda y consulta del resultado.
5. **Notificaciones:** aviso de movimientos y estados de operación por, al menos, dos canales/proveedores desacoplados, por ejemplo push y SMS/correo.
6. **Auditoría y control:** registro de acciones relevantes del cliente, trazabilidad de operaciones y señales para monitoreo, fraude y cumplimiento.

El Core bancario conserva la autoridad contable y de saldo. La capa digital no replica el libro mayor ni declara una operación exitosa antes de tener una respuesta de negocio confirmada o un estado explícito como “pendiente”.

## C4 y alineación de capacidades

El modelo utiliza la notación C4 para organizar el diseño por niveles. BIAN se usa como referencia para agrupar capacidades y responsabilidades de servicios bancarios; TOGAF aporta una forma de relacionar objetivos, capacidades, aplicaciones, datos y tecnología. La propuesta no afirma certificación ni correspondencia uno a uno con todos los Service Domains de BIAN: el mapeo definitivo depende del catálogo, contratos y modelo operativo de BP.

### C1 — Contexto

Presenta el ecosistema a una audiencia de negocio y tecnología: clientes, canales web/móvil, capacidades del dominio digital, Core BP y partners. Explica las relaciones con identidad/autenticación, verificación facial, pagos interbancarios y proveedores de notificaciones.

Las capacidades se organizan en las perspectivas visibles en el diagrama: **clientes, canales, productos, procesos, dominio, Core y partners**. En términos de capacidades bancarias de referencia, el alcance cubre acceso de cliente, información de cliente/productos, gestión de cuentas, movimientos, pagos y transferencias, autenticación, identidad, notificaciones y controles.

### C2 — Contenedores

Detalla los canales Angular SPA y móvil, la entrada segura a través de Front Door/WAF, API Management y Application Gateway for Containers, los servicios desplegados en AKS, la integración síncrona y asíncrona, persistencia, caché, observabilidad y sistemas externos.

Los servicios de negocio se dividen por responsabilidad —onboarding/identidad, consultas, clientes, cuentas, transferencias propias, transferencias interbancarias, pagos, notificaciones y cumplimiento— para limitar acoplamiento y permitir evolución independiente donde el valor operativo lo justifique. La separación no implica crear un clúster por microservicio.

### C3 — Componentes

La vista profundiza en componentes y colaboraciones de los flujos de onboarding, consulta y operación. Muestra validación/autorización, orquestación, adaptadores, persistencia, publicación de eventos y mecanismos de robustez. Los contratos externos se encapsulan detrás de adaptadores para aislar el dominio digital de protocolos y cambios de Core/partners.

### Vista de infraestructura

Representa una posible implantación Azure: entrada global y protección perimetral, AKS, API Management, Key Vault, Azure Monitor, bases de datos, Redis, mensajería, almacenamiento, CI/CD y conexiones con Core y partners. Es una vista lógica de referencia; no sustituye un diseño de red, sizing ni landing zone de producción.

## Flujos principales

### Autenticación y onboarding

- Para SPA y aplicación móvil se recomienda **OAuth 2.0 + OpenID Connect Authorization Code con PKCE S256**. En móvil se utiliza el navegador del sistema y los mecanismos del sistema operativo; para SPA, un BFF mantiene los tokens fuera del almacenamiento accesible a JavaScript y usa una cookie `HttpOnly`, `Secure` y `SameSite`.
- La aplicación delega autenticación al producto de identidad corporativo. Aplicar MFA y autenticación reforzada/step-up a operaciones de riesgo, cambios de datos sensibles y altas de beneficiarios, con políticas basadas en riesgo.
- En onboarding, Facephi u otro proveedor realiza prueba de vida/verificación facial y validación de identidad. La biometría no se trata como contraseña: conservar referencias y resultados mínimos necesarios, protegerlos y definir retención y consentimiento con Cumplimiento.
- Tras el enrolamiento, el usuario puede usar credenciales y MFA; se recomienda habilitar passkeys/WebAuthn o biometría local ligada a una clave protegida por hardware del dispositivo. La biometría local desbloquea una credencial del dispositivo y no se envía como factor biométrico al backend.

### Consulta de datos y movimientos

El canal llama al BFF/API. El servicio de consulta compone la respuesta mediante servicios de cliente, productos/cuentas y movimientos. La información se obtiene del Core y del sistema complementario según la necesidad; Redis puede acelerar lecturas tolerantes a obsolescencia. Saldos disponibles, autorización de pagos y decisiones que requieren consistencia se consultan en la fuente autoritativa, no en una caché.

### Transferencia o pago

El servicio valida sesión, permisos, límites, beneficiario, idempotencia y reglas de riesgo; obtiene el estado autoritativo requerido; persiste la intención/operación y coordina con Core o el adaptador interbancario. Para interacciones asíncronas utiliza eventos y estados de negocio explícitos. Reintentos con backoff, timeout y circuit breaker se combinan con claves idempotentes para evitar duplicación. La respuesta puede ser confirmada, rechazada o pendiente de conciliación.

### Notificaciones

La transacción confirmada o el evento de estado se publica mediante **Transactional Outbox** y un bus duradero. Consumidores idempotentes envían push (Firebase Cloud Messaging/APNs) y SMS/correo mediante proveedores como Twilio o Azure Communication Services. Se aplican reintentos acotados, DLQ, preferencias/consentimiento del cliente y trazabilidad de entrega. La notificación es informativa; no confirma por sí sola el estado contable.

## Datos, auditoría y patrones

- **SQL Server por servicio/dominio:** persistencia transaccional cuando se requiere consistencia relacional; evitar compartir tablas entre servicios. El Core sigue siendo el sistema de registro para libro mayor y saldos.
- **Redis Cache-Aside:** perfiles o catálogos de lectura no sensibles y datos con TTL/versionado. Invalidación explícita y degradación a lectura de origen si Redis falla; no usar caché para autorizar movimientos.
- **Cosmos DB o MongoDB:** alternativas documentales para proyecciones de lectura, estado de onboarding u otros agregados con estructura variable y acceso por documento. Elegir una tecnología por carga y capacidades operativas; no mantener ambas por defecto ni usarlas como ledger sin análisis de consistencia, durabilidad y reconciliación.
- **Auditoría:** separar eventos de auditoría de logs de aplicación. Registrar actor, acción, recurso, correlación, resultado y tiempo con minimización de datos personales. Usar patrón append-only y controles de acceso segregados; exportar evidencia a Blob Storage con inmutabilidad/retención cuando la política lo requiera. MongoDB/Cosmos puede servir para consulta operacional de proyecciones, pero no reemplaza el repositorio de evidencia inmutable.
- **Patrones:** BFF, Adapter/Anti-Corruption Layer, Cache-Aside, Outbox, pub/sub, idempotent consumer, circuit breaker, timeout, retry con backoff y bulkhead. Elegir consistencia síncrona para decisiones críticas y asincronía para notificaciones/propagación de eventos.

## Seguridad, cumplimiento y privacidad

Controles de referencia que deben aterrizarse con Cumplimiento y Seguridad de BP:

- Ley Orgánica de Protección de Datos Personales de Ecuador y su reglamentación: finalidad, base de legitimación, minimización, derechos, retención, transferencias, privacidad desde el diseño y tratamiento de datos biométricos/sensibles.
- Normativa vigente de la Superintendencia de Bancos del Ecuador aplicable a seguridad de la información, riesgo operativo/tecnológico, continuidad, tercerización y canales electrónicos; mantener inventario de obligaciones y evidencia de control.
- Recomendaciones de seguridad OWASP ASVS/MASVS y OWASP API Security; NIST/ISO 27001 como marcos de control, sujeto al programa corporativo.
- PCI DSS solo si el alcance procesa, almacena o transmite datos de tarjeta o puede afectar el entorno de datos de titulares; confirmar segmentación y alcance con el adquirente/área de tarjetas.
- TLS moderno en tránsito, cifrado en reposo, gestión y rotación de secretos/llaves en Key Vault, identidades administradas, menor privilegio, separación de funciones, WAF, protección DDoS, validación de entrada y controles anti-replay.
- Tokens de acceso de vida corta y audiencias/scopes mínimos; protección contra CSRF/XSS en web, almacenamiento seguro en móvil, MFA/step-up y detección de sesión anómala.
- Datos sensibles fuera de logs, enmascaramiento, clasificación, retención definida, borrado gobernado y acceso auditado. Segmentar redes y restringir salida desde workloads.

Las referencias normativas cambian y su aplicabilidad depende del producto y jurisdicción. Antes de implementación se debe revisar el texto vigente y obtener validación legal/regulatoria.

## Disponibilidad, resiliencia y operación

- Desplegar producción en zonas de disponibilidad, con réplicas de servicios, probes de salud, Pod Disruption Budgets, requests/limits y escalado HPA; AKS Cluster Autoscaler ajusta nodos. Mantener servicios sin estado cuando sea posible.
- Ejecutar respaldos y restauraciones verificadas, replicación de datos y una región secundaria para recuperación ante desastre. Definir RTO/RPO por flujo y probar failover/failback; no asumir que la réplica equivale a respaldo.
- Usar timeouts por dependencia, circuit breaker, reintentos limitados con jitter, bulkheads, rate limits, DLQ y replay controlado. Evitar tormentas de reintentos y propagar `correlation-id`/trace context.
- Disponibilidad degradada: priorizar consultas no críticas; bloquear operaciones financieras cuando no sea posible verificar límites, identidad, saldo o resultado autoritativo.
- Azure Monitor, Application Insights y OpenTelemetry para métricas, logs y trazas correlacionadas; alertas con umbrales accionables, tableros SLO/error budget, runbooks y respuesta a incidentes.
- CI/CD con revisión, pruebas de seguridad/calidad, despliegue progresivo (canary/blue-green), análisis de imágenes y rollback automatizado. Kubernetes recupera pods; autoscaling y políticas de salud habilitan auto-healing, con supervisión de fallas persistentes.

## Costos y escalado en Azure

No hay en el enunciado volúmenes, concurrencia pico, región, retención, tamaño de datos ni SLA. Por eso no se publica un costo mensual total ficticio. El cálculo final debe realizarse en [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) usando región, SKU, horas, réplicas, almacenamiento, solicitudes, transferencia y retención reales.

### Estrategia

- Compartir clústeres AKS por ambiente/región y agrupar microservicios por perfil de recursos; evitar un clúster por servicio. Producción multi-zona y región DR tibia según RTO/RPO; ambientes no productivos apagables o reducidos fuera de horario.
- HPA y Cluster Autoscaler, requests/limits ajustados con métricas reales, escalado por cola para consumidores y cargas reservadas/ahorro para el nivel base estable. Mantener headroom para picos y failover.
- Evaluar servicios PaaS administrados antes de desplegar operación propia en AKS: base de datos, caché y mensajería deben presupuestar réplicas, backup, recuperación y transferencia entre zonas/regiones.
- Aplicar presupuestos, etiquetas de costo por dominio/ambiente, alertas de anomalía, cuotas, políticas de retención de logs y revisiones periódicas FinOps.

### Rubros a cotizar

| Rubro | Variables que dominan el costo |
| --- | --- |
| AKS | Tier de administración, número/tamaño de nodos, discos, zona, región DR y horas encendidas. |
| Front Door/WAF | Tier, solicitudes, transferencia de salida, reglas WAF y Private Link cuando aplique. |
| API Management | Tier/capacidad, unidades, regiones desplegadas, gateway y tráfico. |
| SQL administrado | SKU/compute, alta disponibilidad, almacenamiento, backups y réplicas regionales. |
| Redis | Tier, memoria, réplicas, persistencia y alta disponibilidad. |
| Event Hubs/Service Bus | Unidades/capacidad, throughput, retención, geo-replicación y DLQ. |
| Blob/Cosmos DB | Capacidad, operaciones/throughput, redundancia, tier de almacenamiento y retención. |
| Observabilidad | GB ingeridos, retención de Log Analytics, consultas y Application Insights. |
| Red y seguridad | Private Link, NAT, DNS, egress interregional, certificados, llaves y operaciones. |

Como referencia de orden de magnitud publicada al **28-09-2026**, el tier Standard de AKS se cotiza a USD 0,10 por clúster/hora. Dos clústeres Standard durante 730 horas equivaldrían a unos USD 146/mes solo en el cargo de administración. La tarifa base publicada de Azure Front Door Premium es USD 330/mes, por lo que esos dos conceptos sumarían alrededor de **USD 476/mes antes de nodos, APIM, bases de datos, Redis, mensajería, almacenamiento, logs, red, impuestos y descuentos**. No representa el costo de producción. Precios públicos y condiciones varían por región, moneda, contrato y fecha; confirmar en la calculadora y páginas oficiales: [tiers AKS](https://learn.microsoft.com/azure/aks/free-standard-pricing-tiers), [Azure Front Door](https://azure.microsoft.com/pricing/details/frontdoor/), [costos de API Management](https://learn.microsoft.com/azure/api-management/plan-manage-costs), [PostgreSQL Flexible Server](https://azure.microsoft.com/pricing/details/postgresql/flexible-server/) y [costos de Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/logs/cost-logs).

## Decisiones y alternativas

| Decisión | Motivo y alternativas consideradas |
| --- | --- |
| Angular SPA + BFF | Separa UI y backend, centraliza tokens y composición. Se podría usar SPA con tokens en el browser; se evita para reducir exposición de credenciales. |
| React Native; Flutter como alternativa | Reutiliza buena parte de la lógica entre plataformas y permite integración nativa para credenciales del dispositivo. Flutter también es viable; la selección final depende de experiencia del equipo, accesibilidad, SDK biométrico y rendimiento requerido. |
| OAuth/OIDC Code + PKCE | Flujo estándar para clientes públicos web/móvil; evita el flujo implícito y el password grant. BFF mantiene tokens de SPA en servidor. |
| AKS para servicios que requieren control | Portabilidad, ecosistema Kubernetes y políticas/despliegue granular; mayor costo y carga operativa que Container Apps/App Service. Usar PaaS más simple cuando no se necesite control de clúster. |
| Core como fuente de verdad | Consistencia de operación financiera y conciliación; una copia digital de saldos introduciría riesgo de divergencia. |
| Outbox + mensajería | Evita perder notificaciones/eventos entre commit y publicación, y desacopla el tiempo de respuesta. Alternativa: llamada directa síncrona; más simple, pero acopla disponibilidad y latencia del proveedor. |
| Redis solo para lecturas aptas | Baja latencia y menor carga del origen; se excluyen decisiones financieras críticas por riesgo de obsolescencia. |
| Auditoría inmutable separada | Preserva trazabilidad y limita alteración; se distingue de observabilidad técnica y de proyecciones de consulta. |

## Referencias técnicas y normativas

- [BIAN — Service Landscape](https://bian.org/servicelandscape-12-0-0/views/service-domains/): referencia para el lenguaje de capacidades y dominios bancarios.
- [The Open Group — TOGAF Standard](https://www.opengroup.org/togaf): referencia para arquitectura empresarial y relación entre negocio, aplicaciones, datos y tecnología.
- [OAuth 2.0 Security Best Current Practice, RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html) y [OAuth 2.0 para aplicaciones nativas, RFC 8252](https://www.rfc-editor.org/rfc/rfc8252.html).
- [Superintendencia de Bancos del Ecuador — Codificación de normas](https://www.superbancos.gob.ec/bancos/codificacion-de-normas-de-la-sb-libro-uno-sistema-financiero/).
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/) y [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/).

## Uso y edición

Abre `diagrams/Arquitectura_C4_Banca_Digital_BP.drawio` con [diagrams.net](https://app.diagrams.net/) para editar el modelo. El documento fuente tiene cuatro pestañas: C1, C2, C3 e infraestructura. Los PNG son exportaciones de consulta y deben regenerarse después de cambios al diagrama. La propuesta Word puede editarse en Microsoft Word; el PDF es la versión para lectura/entrega.

