# Arquitectura de banca digital para BP

Propuesta optimizada para el ejercicio de arquitectura de soluciones: canales web y móvil, consulta y ejecución de operaciones financieras, onboarding digital, integración con Core y notificaciones. El documento de entrega está en [`output/pdf/Propuesta_Arquitectura_Banca_Digital_BP.pdf`](output/pdf/Propuesta_Arquitectura_Banca_Digital_BP.pdf) y el análisis ampliado en [`docs/arquitectura.md`](docs/arquitectura.md).

## Decisiones clave

- Azure como nube de referencia; AKS solo para dominios que requieran despliegue independiente. Azure Container Apps queda como opción inicial de menor carga operativa.
- Angular SPA con patrón Backend for Frontend (BFF); React Native para móvil y Flutter como alternativa evaluada.
- OAuth 2.0 + OpenID Connect Authorization Code con PKCE S256. La app móvil usa navegador del sistema; la SPA mantiene tokens en servidor BFF y cookie `HttpOnly`, `Secure`, `SameSite`.
- Core bancario como fuente contable autoritativa. No se mantiene un saldo paralelo ni se confirma una operación por una aceptación asíncrona sin estado de negocio explícito.
- Azure Service Bus para comandos y notificaciones fiables; Transactional Outbox, consumidores idempotentes, reintentos limitados y dead-letter queue.
- Redis Cache-Aside solo para datos de lectura no sensibles o tolerantes a obsolescencia. Nunca se cachea el saldo disponible ni se autoriza una transferencia con datos cacheados.
- Auditoría de negocio append-only con eventos mínimos, almacenamiento inmutable con retención gobernada y segregación frente a logs técnicos.
- Dos canales de entrega como mínimo: push (FCM/APNs) y correo/SMS por proveedores desacoplados, con failover según criticidad y política de consentimiento.

## Navegación

- [`docs/arquitectura.md`](docs/arquitectura.md): alcance, restricciones, flujos, controles, resiliencia, normativa, ADR y operación.
- [`diagrams/Arquitectura_C4_Banca_Digital_BP.drawio`](diagrams/Arquitectura_C4_Banca_Digital_BP.drawio): Draw.io multipágina con C1 Contexto, C2 Contenedores, cuatro vistas C3 por contenedor principal y vista de despliegue Azure enlazada con C2.
- [`diagrams/`](diagrams/): fuentes Mermaid de flujos de onboarding, transferencia e infraestructura.
- [`output/pdf/`](output/pdf/): entrega exportada.

## Uso

Los diagramas `.mmd` pueden editarse en Mermaid Live o en un editor compatible. Las cifras de escala, RTO/RPO y SLO son objetivos de diseño iniciales sujetos a validación con BP y no se presentan como datos productivos conocidos. Las obligaciones regulatorias deben ser confirmadas por Cumplimiento y Asesoría Jurídica antes de implementar.
