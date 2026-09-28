"""Build an editable, multi-page Draw.io C4 architecture for BP."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "diagrams" / "Arquitectura_C4_Banca_Digital_BP.drawio"

COLORS = {
    "navy": "#17324D", "blue": "#DCEBFA", "blueLine": "#3973A5",
    "teal": "#DDF3EF", "tealLine": "#258276", "gold": "#FFF1D2",
    "goldLine": "#B7791F", "purple": "#EEE7FA", "purpleLine": "#7656A8",
    "red": "#FCE8E6", "redLine": "#B42318", "gray": "#F1F5F9",
    "grayLine": "#8294A8", "text": "#162B3D", "white": "#FFFFFF",
}


class Page:
    def __init__(self, name, pid, width=1920, height=1080):
        self.diagram = Element("diagram", {"name": name, "id": pid})
        self.model = SubElement(self.diagram, "mxGraphModel", {
            "dx": str(width), "dy": str(height), "grid": "1", "gridSize": "10",
            "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
            "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(width),
            "pageHeight": str(height), "math": "0", "shadow": "0",
        })
        self.root = SubElement(self.model, "root")
        SubElement(self.root, "mxCell", {"id": "0"})
        SubElement(self.root, "mxCell", {"id": "1", "parent": "0"})
        self.serial = 2

    def box(self, title, description, x, y, w, h, tone="blue", *, subtitle=None, shape="rounded"):
        cid = f"n{self.serial}"
        self.serial += 1
        color = COLORS[tone]
        line = COLORS.get(tone + "Line", COLORS["blueLine"])
        label = f"<b>{escape(title)}</b>"
        if subtitle:
            label += f"<br><font color=\"{COLORS['navy']}\"><i>{escape(subtitle)}</i></font>"
        if description:
            label += f"<br>{escape(description).replace(chr(10), '<br>')}"
        style = (f"shape={shape};rounded=1;whiteSpace=wrap;html=1;arcSize=12;"
                 f"fillColor={color};strokeColor={line};strokeWidth=2;fontColor={COLORS['text']};"
                 "fontFamily=Arial;fontSize=15;align=center;verticalAlign=middle;spacing=10;")
        cell = SubElement(self.root, "mxCell", {"id": cid, "value": label, "style": style,
                                                  "vertex": "1", "parent": "1"})
        SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})
        return cid

    def zone(self, title, x, y, w, h, tone="gray", *, dashed=False):
        cid = f"z{self.serial}"
        self.serial += 1
        style = (f"swimlane;horizontal=1;startSize=42;rounded=1;whiteSpace=wrap;html=1;"
                 f"fillColor={COLORS[tone]};swimlaneFillColor={COLORS['white']};"
                 f"strokeColor={COLORS.get(tone+'Line', COLORS['grayLine'])};strokeWidth=2;"
                 "fontColor=#17324D;fontFamily=Arial;fontSize=18;fontStyle=1;align=left;spacingLeft=14;")
        if dashed:
            style += "dashed=1;dashPattern=8 6;"
        cell = SubElement(self.root, "mxCell", {"id": cid, "value": escape(title), "style": style,
                                                  "vertex": "1", "parent": "1"})
        SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})
        return cid

    def edge(self, source, target, label, *, color="blueLine", dashed=False, waypoints=None, labelpos=None):
        cid = f"e{self.serial}"
        self.serial += 1
        style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
                 f"html=1;endArrow=block;endFill=1;strokeWidth=2;strokeColor={COLORS.get(color,color)};"
                 "fontFamily=Arial;fontSize=12;fontColor=#17324D;labelBackgroundColor=#FFFFFF;"
                 "exitPerimeter=1;entryPerimeter=1;")
        if dashed:
            style += "dashed=1;dashPattern=8 6;"
        cell = SubElement(self.root, "mxCell", {"id": cid, "value": escape(label), "style": style,
                                                  "edge": "1", "parent": "1", "source": source, "target": target})
        geom = SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        if labelpos:
            geom.set("x", str(labelpos[0]))
            geom.set("y", str(labelpos[1]))
        if waypoints:
            pts = SubElement(geom, "Array", {"as": "points"})
            for px, py in waypoints:
                SubElement(pts, "mxPoint", {"x": str(px), "y": str(py)})
        return cid

    def note(self, title, body, x, y, w, h):
        return self.box(title, body, x, y, w, h, "gold", shape="note")


def page_context():
    # Rebuilt C1 follows the original left-to-right layer structure. BIAN names label
    # business responsibilities; the boxes are logical systems/services, not a 1:1 SD deployment.
    p = Page("C1 - Contexto", "c1-contexto", 3200, 1480)
    p.box("C1 | CONTEXTO Y CAPAS DE BANCA DIGITAL BP", "Vista del sistema solicitada · las capas y sistemas se organizan según el diagrama original · BIAN guía las responsabilidades de negocio", 35, 20, 3130, 70, "blue")
    p.zone("Actor", 35, 115, 245, 1210, "gray")
    p.zone("1 · CANALES", 300, 115, 500, 1210, "blue")
    p.zone("2 · PRODUCTO Y PROCESOS", 820, 115, 500, 1210, "teal")
    p.zone("3 · DOMINIO / INTEGRACIÓN", 1340, 115, 680, 1210, "gold")
    p.zone("4 · CORE / SISTEMAS DE REGISTRO", 2040, 115, 520, 1210, "gray")
    p.zone("Sistemas existentes de BP y terceros", 2580, 115, 585, 1210, "purple", dashed=True)

    customer = p.box("Cliente", "Cliente existente o nuevo\nInicia consultas y operaciones", 65, 280, 185, 130, "blue")

    web = p.box("Banca web", "SPA para consulta y operaciones", 345, 245, 405, 125, "blue")
    mobile = p.box("Banca móvil", "Framework multiplataforma\nOnboarding facial y acceso", 345, 465, 405, 125, "blue")

    onboarding = p.box("Onboarding y activación", "Captura de datos y consentimiento\nVerificación facial / prueba de vida\nActivación de la relación", 865, 195, 405, 150, "teal")
    access = p.box("Autenticación y acceso", "Inicio de sesión web y móvil\nUsuario/clave o biometría local\nAutorización reforzada según operación", 865, 385, 405, 150, "teal")
    inquiry = p.box("Consulta financiera", "Consulta de posición consolidada\nConsulta de movimientos por cuenta\nDatos básicos y perfil detallado", 865, 575, 405, 150, "teal")
    transfer_flow = p.box("Pago / transferencia", "Cuenta propia: validación y ejecución\nInterbancaria: riel externo\nConfirmación, rechazo o pendiente", 865, 765, 405, 150, "teal")
    notify_flow = p.box("Notificación y auditoría", "Notificar movimientos confirmados\nRegistrar las acciones del cliente\nGestionar excepciones de entrega", 865, 955, 405, 150, "teal")

    gateway = p.box("API Gateway", "Punto de entrada de integración\nPolíticas y enrutamiento de APIs", 1380, 155, 600, 105, "gold")
    profile_service = p.box("Consulta de cliente", "Datos básicos + enriquecimiento\nBIAN: Customer Profile / Party Reference Data Directory\nOrquesta las 2 fuentes requeridas", 1380, 300, 285, 145, "teal")
    position_service = p.box("Consulta de posición", "Vista agregada de cuentas/productos\nBIAN: Customer Position\nNo sustituye el detalle transaccional", 1695, 300, 285, 145, "teal")
    movement_service = p.box("Consulta de movimientos", "Historial detallado por cuenta\nBIAN: Current Account / Position Keeping\nLectura desde la fuente autoritativa", 1380, 485, 285, 155, "teal")
    payment_service = p.box("Transferencias", "Iniciar y autorizar orden\nBIAN: Payment Order Initiation /\nTransaction Authorization / Payment Execution", 1695, 485, 285, 155, "teal")
    onboarding_service = p.box("Gestión de onboarding", "Estado de alta y verificaciones\nBIAN: Party Lifecycle Management\nFacial/KYC delegados al proveedor", 1380, 680, 285, 145, "teal")
    notification_service = p.box("Servicio de notificaciones", "Evento de movimiento confirmado\nDespacho por mínimo 2 canales\nPreferencias y estado de entrega", 1695, 680, 285, 145, "teal")
    cache = p.box("Persistencia de clientes frecuentes", "Cache-Aside de datos permitidos\nNo es fuente de saldos ni de movimientos", 1380, 875, 285, 125, "blue")
    audit = p.box("Base de datos de auditoría", "Registro append-only de acciones\nEvidencia, retención y acceso segregado", 1695, 875, 285, 125, "red")

    core = p.box("Core bancario BP", "Datos básicos · productos · cuentas\nMovimientos detallados · saldos\nLedger / contabilización autoritativa", 2075, 310, 450, 160, "blue")
    detail = p.box("Sistema independiente de detalle", "Complementa la información del cliente\nFuente de detalle bajo demanda", 2075, 550, 450, 145, "blue")

    iam = p.box("Producto IAM / CIAM de BP", "OAuth 2.0 + OpenID Connect\nAutenticación y emisión de tokens", 2615, 155, 515, 115, "purple")
    face = p.box("Proveedor de identidad facial / KYC", "Reconocimiento facial + liveness\nVerificación durante onboarding", 2615, 335, 515, 115, "purple")
    rail = p.box("Rieles interbancarios", "SPI/BCE o Banred según convenio\nTransferencias hacia otros bancos", 2615, 535, 515, 115, "purple")
    push = p.box("Canal de notificación push", "FCM / APNs\nEntrega móvil", 2615, 755, 245, 115, "purple")
    msg = p.box("Canal de notificación alterno", "Email o SMS provider\nRuta alternativa independiente", 2885, 755, 245, 115, "purple")
    obs = p.box("Monitoreo y seguridad", "Métricas, alertas y eventos\nRequisito transversal", 2615, 975, 515, 115, "red")

    p.edge(customer, web, "HTTPS", color="blueLine")
    p.edge(customer, mobile, "App segura", color="blueLine")
    p.edge(web, access, "Canal web", color="tealLine")
    p.edge(mobile, onboarding, "Alta móvil", color="tealLine")
    p.edge(mobile, access, "Canal móvil", color="tealLine")
    p.edge(onboarding, gateway, "Solicitudes de alta", color="goldLine")
    p.edge(access, gateway, "APIs protegidas", color="goldLine")
    p.edge(inquiry, gateway, "Consultas", color="goldLine")
    p.edge(transfer_flow, gateway, "Órdenes", color="goldLine")
    p.edge(notify_flow, gateway, "Eventos / auditoría", color="goldLine")
    p.edge(gateway, profile_service, "Enrutamiento API", color="tealLine")
    p.edge(gateway, position_service, "Enrutamiento API", color="tealLine")
    p.edge(gateway, movement_service, "Enrutamiento API", color="tealLine")
    p.edge(gateway, payment_service, "Enrutamiento API", color="tealLine")
    p.edge(gateway, onboarding_service, "Enrutamiento API", color="tealLine")
    p.edge(gateway, notification_service, "Enrutamiento API", color="tealLine")
    p.edge(profile_service, core, "API segura: datos básicos", color="blueLine")
    p.edge(profile_service, detail, "API segura: datos detallados", color="blueLine")
    p.edge(position_service, core, "API: resumen consolidado", color="blueLine")
    p.edge(movement_service, core, "API: historial por cuenta", color="blueLine")
    p.edge(payment_service, core, "API: cuenta propia / contabilización", color="blueLine")
    p.edge(payment_service, rail, "Transferencia interbancaria", color="purpleLine")
    p.edge(onboarding_service, face, "Verificación facial / liveness", color="purpleLine")
    p.edge(mobile, iam, "OIDC: Authorization Code + PKCE", color="purpleLine", dashed=True)
    p.edge(web, iam, "OIDC: Authorization Code", color="purpleLine", dashed=True)
    p.edge(gateway, iam, "JWKS / validación de token", color="purpleLine", dashed=True)
    p.edge(notification_service, push, "Push", color="purpleLine")
    p.edge(notification_service, msg, "Email / SMS", color="purpleLine")
    p.edge(profile_service, cache, "Cache-Aside", color="blueLine")
    p.edge(profile_service, audit, "Acceso / resultado", color="redLine", dashed=True)
    p.edge(movement_service, audit, "Consulta / resultado", color="redLine", dashed=True)
    p.edge(payment_service, audit, "Orden / resultado", color="redLine", dashed=True)
    p.edge(onboarding_service, audit, "Alta / resultado", color="redLine", dashed=True)
    p.edge(notification_service, audit, "Despacho / resultado", color="redLine", dashed=True)
    p.edge(gateway, obs, "Métricas / seguridad", color="redLine", dashed=True)
    p.note("Límite de responsabilidades", "BIAN clasifica responsabilidades de negocio; no exige un sistema por Service Domain. Customer Position es el resumen agregado. El historial transaccional se consulta en Current Account / Position Keeping del Core. La caché y auditoría son persistencias auxiliares, nunca autoridades de saldos o movimientos.", 335, 1350, 2800, 70)
    return p


def page_c1_context():
    p = Page("C1 - Contexto C4", "c1-contexto", 3000, 1400)
    p.box("C1 | CONTEXTO DEL SISTEMA · MODELO C4", "Sistema de interés, clientes, canales, procesos de negocio, Core y partners · BIAN orienta las capacidades; el detalle interno se reserva para C2/C3", 35, 20, 2930, 65, "blue")
    p.zone("1 · CLIENTES", 35, 110, 240, 1160, "gray")
    p.zone("2 · CANALES", 285, 110, 360, 1160, "blue")
    p.zone("3 · PRODUCTOS Y PROCESOS (anotación de negocio)", 655, 110, 490, 1160, "teal")
    p.zone("4 · DOMINIO · sistema de interés C4", 1155, 110, 550, 1160, "gold")
    p.zone("5 · CORE BP · sistemas de registro", 1715, 110, 480, 1160, "gray")
    p.zone("6 · PARTNERS Y PLATAFORMAS COMPARTIDAS", 2205, 110, 760, 1160, "purple", dashed=True)

    customer = p.box("Cliente", "Existente o nuevo\nPersona titular que consulta\ny realiza operaciones", 60, 300, 190, 130, "blue", subtitle="Person")
    web = p.box("Canal web", "Aplicación SPA\nConsulta y operaciones", 320, 260, 290, 105, "blue", subtitle="Canal de acceso · C1")
    mobile = p.box("Canal móvil", "Aplicación multiplataforma\nOnboarding facial y acceso", 320, 470, 290, 105, "blue", subtitle="Canal de acceso · C1")

    p.note("Jornada 1 · Onboarding", "Captura de datos y consentimiento → verificación facial y prueba de vida → validación de identidad → activación de acceso móvil.", 685, 175, 430, 115)
    p.note("Jornada 2 · Acceso", "Autenticación OAuth/OIDC → validación de permisos → step-up para acciones sensibles → consulta segura de productos.", 685, 315, 430, 115)
    p.note("Jornada 3 · Consulta", "Datos básicos y perfil → posición consolidada → historial de movimientos por cuenta desde la fuente autoritativa.", 685, 455, 430, 115)
    p.note("Jornada 4 · Pago", "Captura de orden → validación de cuenta/beneficiario y autorización → ejecución propia o interbancaria → estado confirmado, rechazado o pendiente.", 685, 595, 430, 135)
    p.note("Jornada 5 · Notificación y evidencia", "Movimiento confirmado → notificación por al menos dos canales → registro auditable de la acción y su resultado.", 685, 755, 430, 115)

    bank = p.box("BP | Banca Digital", "Sistema de banca por internet para clientes BP. Consolida experiencias web y móvil; consulta datos de sistemas fuente; inicia y coordina consultas, pagos y notificaciones. No sustituye al Core como autoridad contable.", 1195, 330, 470, 220, "gold", subtitle="Software System · frontera C1")
    p.note("Alineación BIAN (responsabilidades candidatas)", "Party Lifecycle Management · Party Authentication · Customer Profile · Customer Position · Current Account / Position Keeping · Payment Order Initiation · Transaction Authorization · Payment Execution. BIAN no prescribe un microservicio por dominio.", 1185, 640, 490, 200)

    core = p.box("Core bancario BP", "Datos básicos · clientes\nProductos · cuentas\nMovimientos · saldos · ledger", 1745, 275, 420, 145, "blue", subtitle="Sistema BP existente · fuente de registro")
    detail = p.box("Sistema de perfil detallado", "Fuente complementaria del cliente\nConsulta de detalle bajo demanda", 1745, 500, 420, 125, "blue", subtitle="Sistema BP existente")

    iam = p.box("IAM / CIAM de BP", "OAuth 2.0 + OpenID Connect\nMFA / credenciales de acceso", 2240, 150, 690, 95, "purple", subtitle="Plataforma compartida existente")
    kyc = p.box("Partner de identidad facial / KYC", "Reconocimiento facial + liveness\nVerificación de identidad en onboarding", 2240, 280, 690, 95, "purple", subtitle="Sistema externo")
    rail = p.box("Partner de pagos interbancarios", "SPI/BCE o Banred según convenio\nRecepción de estado / liquidación", 2240, 410, 690, 95, "purple", subtitle="Sistema externo")
    push = p.box("Partner de notificación Push", "FCM / APNs · entrega a dispositivo", 2240, 555, 330, 90, "purple", subtitle="Sistema externo · ruta 1")
    msg = p.box("Partner Email / SMS", "Entrega alternativa independiente", 2590, 555, 340, 90, "purple", subtitle="Sistema externo · ruta 2")
    evidence = p.box("Auditoría y monitoreo BP", "Persistencia de auditoría y señales\noperativas / seguridad", 2240, 710, 690, 100, "red", subtitle="Plataforma transversal existente/propuesta")
    p.edge(customer, web, "Accede por navegador", color="blueLine")
    p.edge(customer, mobile, "Accede por aplicación", color="blueLine")
    p.edge(web, bank, "HTTPS", color="tealLine")
    p.edge(mobile, bank, "HTTPS · OIDC/PKCE", color="tealLine")
    p.edge(bank, iam, "OIDC · autenticación y step-up", color="purpleLine")
    p.edge(bank, kyc, "API segura · rostro/liveness", color="purpleLine")
    p.edge(bank, core, "API privada · datos/cuentas/movimientos/pagos", color="blueLine")
    p.edge(bank, detail, "API privada · datos complementarios", color="blueLine")
    p.edge(bank, rail, "API segura · orden interbancaria", color="goldLine")
    p.edge(bank, push, "Evento · notificación Push", color="goldLine")
    p.edge(bank, msg, "Evento · Email/SMS de respaldo", color="goldLine")
    p.edge(bank, evidence, "Acciones auditables / telemetría", color="redLine", dashed=True)
    return p


def page_containers():
    p = Page("C2 - Contenedores", "c2-contenedores", 2400, 1360)
    p.box("C2 | DIAGRAMA DE CONTENEDORES C4", "Contenedores ejecutables/gestionados, tecnología, responsabilidades, relaciones y dependencias externas", 35, 10, 2330, 58, "blue")
    p.zone("BP | Región primaria Azure | red privada y zonas de disponibilidad", 35, 80, 1760, 1190, "blue")
    p.zone("Dependencias de BP y terceros", 1845, 80, 520, 1190, "purple", dashed=True)
    p.zone("Canales y perímetro", 70, 150, 1685, 270, "gray")
    p.zone("Contenedores de dominio e integración | responsabilidades BIAN de referencia", 70, 455, 1685, 425, "teal")
    p.zone("Datos y servicios de plataforma", 70, 915, 1685, 300, "gold")
    spa = p.box("SPA Web", "Angular · Static Web Apps / CDN\nBFF + sesión segura", 110, 230, 260, 120, "blue")
    mobile = p.box("Aplicación móvil", "React Native · iOS / Android\nNavegador del sistema + PKCE", 405, 230, 280, 120, "blue")
    afd = p.box("Front Door + WAF", "TLS · bot/rate protection\nDDoS · health probe", 755, 230, 260, 120, "gold")
    apim = p.box("API Management", "Validación JWT · quota\nrouting · correlation ID", 1080, 230, 270, 120, "gold")
    bffweb = p.box("Web BFF", "OIDC confidential client\nCookie HttpOnly + CSRF", 1400, 185, 270, 95, "teal")
    bffmob = p.box("Mobile BFF", "Resource API · scopes\nStep-up contextual", 1400, 300, 270, 95, "teal")
    profile = p.box("Perfil y datos del cliente", "Consulta datos básicos en Core y complementa el detalle desde su fuente especializada. Cache-Aside con TTL y datos permitidos.\nBIAN: Customer Profile / Party Reference Data Directory", 85, 550, 260, 135, "teal")
    onboarding = p.box("Onboarding y ciclo de vida", "Gestiona el estado de alta; coordina verificación documental, facial/liveness y activación en CIAM y Core.\nBIAN: Party Lifecycle Management", 365, 550, 260, 135, "teal")
    movement = p.box("Consulta de movimientos", "Entrega historial paginado por cuenta; obtiene el detalle autoritativo del Core y mantiene proyección de lectura con control de frescura.\nBIAN: Current Account / Position Keeping", 645, 550, 260, 135, "teal")
    position = p.box("Posición consolidada del cliente", "Agrega saldos y productos para una vista resumida; no contabiliza ni reemplaza el ledger o el detalle de movimientos.\nBIAN: Customer Position", 925, 550, 260, 135, "teal")
    transfer = p.box("Pagos y transferencias", "Valida, autoriza e inicia pagos propios e interbancarios; aplica idempotencia y Saga, y consulta el estado al Core/riel.\nBIAN: Payment Order Initiation / Transaction Authorization / Payment Execution", 1205, 550, 260, 135, "teal")
    integration = p.box("Adaptadores de integración (ACL)", "Aísla los contratos del dominio frente a Core, fuente de detalle y rieles; transforma formatos y aplica mTLS, timeouts y políticas de reintento", 1485, 550, 260, 135, "teal")
    notification = p.box("Orquestación de notificaciones", "Consume eventos confirmados; aplica preferencias y plantillas, enruta a Push y Email/SMS, y registra entrega/reintentos", 435, 735, 285, 105, "teal")
    audit = p.box("Exportación de auditoría", "Consume eventos de forma idempotente, minimiza/enmascara PII y persiste evidencia inmutable con retención", 765, 735, 285, 105, "red")
    pg = p.box("PostgreSQL HA", "Persistencia por servicio\nEstado + Transactional Outbox", 105, 1005, 285, 115, "blue")
    redis = p.box("Azure Managed Redis", "Cache de lecturas permitidas\nNunca autoriza saldos", 435, 1005, 285, 115, "blue")
    bus = p.box("Azure Service Bus Premium", "Topics / queues · retries\nDLQ · entrega durable", 765, 1005, 285, 115, "gold")
    blob = p.box("Blob Storage inmutable", "Evidencia de auditoría\nretención y acceso segregados", 1095, 1005, 285, 115, "red")
    kv = p.box("Key Vault + Managed Identity", "Secretos / certificados\nRotación y acceso JIT", 1425, 955, 285, 95, "gold")
    monitor = p.box("Azure Monitor + OTel", "Métricas · logs · trazas\nSLO · alertas · runbooks", 1425, 1070, 285, 95, "gold")
    ci = p.box("IAM / CIAM", "OAuth 2.0 + OIDC\nMFA · passkeys · token lifecycle", 1970, 155, 275, 95, "purple")
    kyc = p.box("Proveedor de identidad", "Documento + liveness\nKYC / antifraude", 1970, 290, 275, 95, "purple")
    core = p.box("Core bancario BP", "Ledger y saldos autoritativos\nCliente · productos · movimientos", 1970, 455, 275, 110, "purple")
    details = p.box("Sistema de cliente detallado", "Enriquecimiento por API\npropietario funcional separado", 1970, 615, 275, 100, "purple")
    rail = p.box("Rieles de pago", "Banred / SPI-BCE\nsegún convenio y ruta", 1970, 770, 275, 100, "purple")
    providers = p.box("Canales de entrega", "FCM / APNs\nEmail / SMS provider", 1970, 935, 275, 110, "purple")
    p.edge(spa, afd, "HTTPS", color="blueLine")
    p.edge(mobile, afd, "HTTPS", color="blueLine")
    p.edge(afd, apim, "WAF + TLS", color="goldLine")
    p.edge(apim, bffweb, "HTTPS + JWT", color="goldLine")
    p.edge(apim, bffmob, "HTTPS + JWT", color="goldLine")
    p.edge(bffweb, profile, "REST", color="tealLine")
    p.edge(bffweb, movement, "REST", color="tealLine")
    p.edge(bffweb, position, "REST", color="tealLine")
    p.edge(bffweb, transfer, "REST", color="tealLine")
    p.edge(bffmob, onboarding, "REST", color="tealLine")
    p.edge(bffmob, transfer, "REST", color="tealLine")
    p.edge(profile, redis, "Cache-Aside", color="blueLine")
    p.edge(profile, integration, "REST/mTLS", color="tealLine")
    p.edge(onboarding, integration, "REST/mTLS", color="tealLine")
    p.edge(movement, integration, "REST/mTLS", color="tealLine")
    p.edge(position, integration, "REST/mTLS", color="tealLine")
    p.edge(transfer, integration, "REST/mTLS", color="tealLine")
    p.edge(transfer, pg, "ACID state + outbox", color="blueLine")
    p.edge(movement, pg, "Projection", color="blueLine", dashed=True)
    p.edge(onboarding, pg, "KYC state", color="blueLine")
    p.edge(transfer, bus, "Outbox relay", color="goldLine")
    p.edge(bus, notification, "TransactionPosted", color="goldLine")
    p.edge(bus, audit, "Audit event", color="redLine")
    p.edge(audit, blob, "WORM evidence", color="redLine")
    p.edge(notification, providers, "Push / Email / SMS", color="goldLine")
    p.edge(integration, core, "Private API · mTLS", color="purpleLine")
    p.edge(integration, details, "Private API · mTLS", color="purpleLine")
    p.edge(integration, rail, "ISO 20022 / HTTPS", color="purpleLine")
    p.edge(bffweb, ci, "OIDC Code flow / BFF", color="purpleLine", dashed=True)
    p.edge(mobile, ci, "System browser + PKCE", color="purpleLine", dashed=True)
    p.edge(onboarding, kyc, "Liveness / KYC API", color="purpleLine", dashed=True)
    return p


def page_components():
    p = Page("C3 - Componentes de transferencias", "c3-transferencias", 2400, 1360)
    p.box("C3 | COMPONENTES C4 · TRANSFER SERVICE", "Descomposición de un contenedor C2 · límites de confianza · BIAN: Payment Order Initiation, Transaction Authorization y Payment Execution", 35, 10, 2330, 58, "blue")
    p.zone("Canal / perímetro", 75, 150, 270, 460, "gray", dashed=True)
    p.zone("Transfer Service | bounded context", 365, 85, 1310, 1180, "teal")
    p.zone("Core, rieles y plataforma compartida", 1720, 85, 645, 1180, "purple", dashed=True)
    p.zone("Solicitud y autorización", 395, 150, 1210, 330, "gray")
    p.zone("Ejecución y persistencia", 395, 520, 1210, 655, "blue")
    channel = p.box("Web / Mobile BFF", "Sesión o token\nStep-up para la orden", 100, 220, 220, 105, "blue")
    apim = p.box("API Management", "JWT: issuer · audience · scope\nquota · correlation · WAF", 110, 400, 235, 120, "gold")
    api = p.box("Transfer Command API", "<<Component>>\nValidación de esquema\nownership por cuenta/recurso", 410, 245, 250, 120, "teal")
    authz = p.box("Authorization / Risk Policy", "<<Component>>\nLímites · beneficiario\nstep-up enlazado a importe", 730, 245, 260, 120, "teal")
    idem = p.box("Idempotency Guard", "<<Component>>\nClave única + hash de orden\nreplay devuelve mismo estado", 1060, 245, 260, 120, "gold")
    saga = p.box("Transfer Orchestrator", "<<Component>> · BIAN Payment Execution\nPENDING / POSTED / REJECTED\nRECONCILIATION_REQUIRED", 1340, 245, 285, 165, "teal")
    coread = p.box("Core Adapter", "<<Component>>\nCommand/read contract\nconsulta estado por referencia", 410, 535, 245, 120, "teal")
    railad = p.box("Rail Adapter", "<<Component>>\nISO 20022 / HTTPS\nfirma callbacks + allowlist", 700, 535, 245, 120, "teal")
    core = p.box("Core ledger BP", "Saldo, reserva y asiento\nautoridad contable", 2110, 335, 215, 115, "purple")
    rail = p.box("SPI/BCE o Banred", "Aceptación / rechazo\nconfirmación / liquidación", 2110, 540, 215, 115, "purple")
    repo = p.box("Transfer Repository", "<<Component>>\nEstado ACID local\nNo mantiene ledger", 410, 720, 240, 115, "blue")
    db = p.box("PostgreSQL HA", "Contenedor de datos C2\nEstado + clave única\nNo guarda ledger duplicado", 2110, 680, 215, 115, "blue")
    outbox = p.box("Transactional Outbox", "<<Component>>\nCommit atómico con estado\neventId + correlationId", 1000, 700, 270, 115, "gold")
    relay = p.box("Outbox Relay", "<<Component>>\nEntrega al menos una vez\nreintento seguro", 1300, 700, 250, 115, "gold")
    bus = p.box("Service Bus Topic", "Eventos versionados\nRetry + DLQ + redrive controlado", 1795, 680, 245, 95, "gold")
    consumers = p.box("Event Consumers", "Dedup por eventId\nAudit + Notification", 1795, 800, 245, 115, "red")
    archive = p.box("Audit Blob WORM", "Append-only · retención\nRBAC separado + evidencia", 2110, 760, 215, 115, "red")
    notify = p.box("Notification Service", "Bandeja durable + prefs\nPush / Email / SMS", 1795, 945, 245, 115, "gold")
    providers = p.box("Notification Providers", "FCM / APNs\nEmail / SMS", 2110, 945, 215, 115, "purple")
    p.edge(channel, apim, "HTTPS + access token", color="blueLine")
    p.edge(apim, api, "HTTPS + JWT", color="goldLine")
    p.edge(api, authz, "Validar titularidad", color="tealLine")
    p.edge(authz, idem, "Orden autorizada", color="tealLine")
    p.edge(idem, saga, "Idempotent command", color="goldLine")
    p.edge(saga, coread, "Own-account route", color="tealLine")
    p.edge(saga, railad, "Interbank route", color="tealLine")
    p.edge(coread, core, "API privada", color="purpleLine")
    p.edge(railad, rail, "ISO 20022 / HTTPS", color="purpleLine")
    p.edge(saga, repo, "Transición de estado", color="blueLine")
    p.edge(saga, api, "Estado + referencia", color="blueLine", dashed=True)
    p.edge(repo, db, "Persist state / key", color="blueLine")
    p.edge(repo, outbox, "Same local transaction", color="goldLine")
    p.edge(outbox, relay, "Polling / CDC", color="goldLine")
    p.edge(relay, bus, "Publicar evento", color="goldLine")
    p.edge(bus, consumers, "At-least-once", color="redLine")
    p.edge(consumers, archive, "AuditEvent", color="redLine")
    p.edge(consumers, notify, "TransactionPosted", color="goldLine")
    p.edge(notify, providers, "TLS · fallback por política", color="goldLine")
    p.note("Regla de timeout", "Timeout externo no significa rechazo. Consultar por referencia antes de reintentar.\nSin débito ciego; pendientes pasan a conciliación.", 1795, 1095, 530, 80)
    p.note("Compensación", "Solo si Core/riel confirman reverso.\nUna Saga gestiona estado distribuido;\nno ofrece rollback ACID global.", 1795, 165, 530, 125)
    p.note("Correspondencia BIAN", "Payment Order Initiation crea / valida la orden; Transaction Authorization evalúa permisos y controles; Payment Execution coordina el envío al Core o al riel. Son responsabilidades de referencia, no componentes de despliegue obligatorios.", 410, 870, 1160, 100)
    return p


def page_components_movements():
    p = Page("C3 - Componentes de consulta de movimientos", "c3-movimientos", 2400, 1360)
    p.box("C3 | COMPONENTES C4 · MOVEMENT QUERY SERVICE", "Descomposición de un contenedor C2 · lectura paginada con fuente autoritativa y proyección no autoritativa", 35, 10, 2330, 58, "blue")
    p.zone("Canal / seguridad de entrada", 55, 145, 285, 600, "gray", dashed=True)
    p.zone("Movement Query Service | límite del contenedor", 365, 100, 1250, 1160, "teal")
    p.zone("Dependencias C2: integración, datos y Core", 1640, 100, 725, 1160, "purple", dashed=True)
    bff = p.box("Web / Mobile BFF", "Access token / sesión\nAccount reference", 85, 235, 225, 105, "blue")
    apim = p.box("API Management", "JWT / scopes\nRate limit / correlationId", 85, 440, 225, 105, "gold")
    api = p.box("Movement Query API", "<<Component>>\nREST resource / cursor contract", 405, 210, 260, 125, "teal")
    context = p.box("Customer Context Resolver", "<<Component>>\nsubject · customerId · channel", 700, 210, 260, 125, "teal")
    entitlement = p.box("Account Access Policy", "<<Component>>\nTitularidad / autorización de cuenta", 995, 210, 280, 125, "teal")
    query = p.box("Movement Query Orchestrator", "<<Component>>\nFiltros · fechas · paginación por cursor", 405, 430, 300, 135, "teal")
    selector = p.box("Source / Freshness Selector", "<<Component>>\nProyección solo si cumple freshness SLA\nFallback al Core ante desfase", 745, 430, 330, 135, "gold")
    mapper = p.box("Response Mapper / PII Filter", "<<Component>>\nModelo de lectura · minimización de datos", 1110, 430, 300, 135, "teal")
    projection = p.box("Movement Read Repository", "<<Component>>\nRead model reconstruible\nNunca autoriza saldo ni contabiliza", 405, 690, 300, 130, "blue")
    adapter = p.box("Core Account Adapter", "<<Component>>\nMapea contrato interno a BIAN-aligned API", 745, 690, 330, 130, "teal")
    auditpub = p.box("Audit Event Publisher", "<<Component>>\nConsulta, recurso y resultado\nSin credenciales ni datos sensibles", 1110, 690, 300, 130, "red")
    acl = p.box("Integration ACL", "Contenedor C2\nmTLS · contrato versionado", 1675, 220, 285, 120, "teal")
    core = p.box("Core BP", "Current Account\nBIAN: Current Account / Position Keeping\nHistorial transaccional autoritativo", 1990, 220, 335, 140, "purple")
    db = p.box("PostgreSQL HA", "Contenedor de datos C2\nRead projection / checkpoint", 1675, 510, 285, 120, "blue")
    bus = p.box("Service Bus Audit Topic", "Contenedor C2\nEntrega durable al consumidor de auditoría", 1990, 510, 335, 120, "gold")
    p.edge(bff, apim, "HTTPS", color="blueLine")
    p.edge(apim, api, "JWT validated", color="goldLine")
    p.edge(api, context, "Resolve subject", color="tealLine")
    p.edge(context, entitlement, "Customer context", color="tealLine")
    p.edge(entitlement, query, "Authorized account", color="tealLine")
    p.edge(query, selector, "Query plan + cursor", color="tealLine")
    p.edge(selector, projection, "Fresh projection", color="blueLine")
    p.edge(selector, adapter, "Live authoritative read", color="goldLine")
    p.edge(projection, db, "Read / checkpoint", color="blueLine")
    p.edge(adapter, acl, "REST / mTLS", color="purpleLine")
    p.edge(acl, core, "Current Account query", color="purpleLine")
    p.edge(projection, selector, "Watermark / freshness", color="blueLine", dashed=True)
    p.edge(selector, mapper, "Page + source metadata", color="tealLine")
    p.edge(mapper, api, "Response DTO", color="tealLine", dashed=True)
    p.edge(api, auditpub, "Record read action", color="redLine", dashed=True)
    p.edge(auditpub, bus, "Audit event", color="redLine")
    p.note("BIAN y consistencia", "Customer Position describe una vista financiera agregada y no reemplaza el detalle de movimientos. Para el histórico por cuenta se consulta Current Account / Position Keeping del Core. La proyección acelera lecturas solo si expone su watermark; si no satisface la frescura acordada, se consulta la fuente autoritativa.", 405, 900, 1005, 150)
    return p


def page_components_onboarding():
    p = Page("C3 - Componentes de onboarding y acceso", "c3-onboarding", 2400, 1360)
    p.box("C3 | COMPONENTES C4 · ONBOARDING SERVICE", "Alta móvil con verificación facial, ciclo de vida de relación y activación segura de credenciales", 35, 10, 2330, 58, "blue")
    p.zone("Canal móvil", 55, 145, 285, 690, "gray", dashed=True)
    p.zone("Onboarding Service | límite del contenedor", 365, 100, 1250, 1160, "teal")
    p.zone("Dependencias C2: CIAM, KYC y Core", 1640, 100, 725, 1160, "purple", dashed=True)
    mobile = p.box("Mobile App", "<<Container>>\nFramework multiplataforma\nCaptura con consentimiento", 85, 225, 225, 125, "blue")
    apim = p.box("API Management", "<<Container>>\nJWT / rate limit / correlationId", 85, 475, 225, 125, "gold")
    api = p.box("Onboarding API", "<<Component>>\nValidación de request / esquema", 405, 210, 280, 125, "teal")
    context = p.box("Applicant Context", "<<Component>>\nIdentidad declarada · sesión\nIdempotency key de alta", 720, 210, 290, 125, "teal")
    workflow = p.box("Party Lifecycle Workflow", "<<Component>>\nBIAN: Party Lifecycle Management\nEstado persistido / transiciones", 1045, 210, 300, 135, "teal")
    consent = p.box("Consent & Evidence Manager", "<<Component>>\nFinalidad · versión · expiración\nMinimización de evidencia", 405, 445, 280, 135, "teal")
    biometric = p.box("Biometric Verification Adapter", "<<Component>>\nNonce · liveness result\nNo almacenar plantilla biométrica", 720, 445, 290, 135, "teal")
    decision = p.box("Onboarding Decision Policy", "<<Component>>\nAccept / reject / needs-review\nReglas auditables", 1045, 445, 300, 135, "gold")
    coread = p.box("Customer Registration Adapter", "<<Component>>\nBusca/crea relación cliente\nNo duplica registro maestro", 405, 700, 280, 130, "teal")
    ciad = p.box("CIAM Enrollment Adapter", "<<Component>>\nVincula identidad aprobada\nActiva enrollment / recovery", 720, 700, 290, 130, "teal")
    audit = p.box("Onboarding Audit Publisher", "<<Component>>\nCorrelación de pasos y decisión\nEvidencia sin secretos", 1045, 700, 300, 130, "red")
    kyc = p.box("Face / KYC Provider", "Sistema externo\nFace match + liveness", 1675, 205, 285, 120, "purple")
    ci = p.box("BP IAM / CIAM", "Sistema existente\nOAuth 2.0 / OIDC\nPasskey o usuario/clave", 1985, 205, 340, 135, "purple")
    core = p.box("Core bancario BP", "Sistema existente\nRegistro maestro de cliente", 1675, 475, 285, 120, "purple")
    bus = p.box("Audit Event Bus", "Contenedor C2\nEntrega durable a auditoría", 1985, 475, 340, 120, "gold")
    p.edge(mobile, apim, "HTTPS · consentimiento", color="blueLine")
    p.edge(apim, api, "HTTPS / access token", color="goldLine")
    p.edge(api, context, "Applicant request", color="tealLine")
    p.edge(context, workflow, "Start / resume workflow", color="tealLine")
    p.edge(workflow, consent, "Consent required", color="tealLine")
    p.edge(consent, biometric, "Verified purpose + evidence ref", color="tealLine")
    p.edge(biometric, kyc, "TLS · signed request / nonce", color="purpleLine")
    p.edge(kyc, decision, "Match / liveness result", color="purpleLine")
    p.edge(decision, workflow, "Decision + state", color="goldLine")
    p.edge(workflow, coread, "Approved identity", color="tealLine")
    p.edge(coread, core, "Private API / mTLS", color="purpleLine")
    p.edge(workflow, ciad, "Customer reference + activation", color="tealLine")
    p.edge(ciad, ci, "OIDC enrollment / account link", color="purpleLine")
    p.edge(workflow, audit, "Step / outcome event", color="redLine", dashed=True)
    p.edge(audit, bus, "Audit event", color="redLine")
    p.note("BIAN / seguridad", "Party Lifecycle Management representa el seguimiento de la relación desde las verificaciones iniciales. Party Authentication es una responsabilidad posterior de autenticación (delegada al CIAM para emisión de credenciales/tokens). El biométrico del teléfono debe permanecer en el dispositivo; el banco conserva resultados y referencias mínimas, no plantillas faciales.", 405, 925, 1005, 145)
    return p


def page_components_notifications():
    p = Page("C3 - Componentes de notificaciones", "c3-notificaciones", 2400, 1360)
    p.box("C3 | COMPONENTES C4 · NOTIFICATION SERVICE", "Despacho confiable de avisos a partir de movimientos confirmados · al menos dos proveedores/canales", 35, 10, 2330, 58, "blue")
    p.zone("Productores y eventos", 55, 145, 285, 700, "gray", dashed=True)
    p.zone("Notification Service | límite del contenedor", 365, 100, 1250, 1160, "teal")
    p.zone("Proveedores externos y persistencia", 1640, 100, 725, 1160, "purple", dashed=True)
    producer = p.box("Transfer Service", "Contenedor C2\nPublica solo resultado confirmado", 85, 230, 225, 120, "teal")
    bus = p.box("Service Bus", "Contenedor C2\nTopic / retry / DLQ", 85, 510, 225, 120, "gold")
    consumer = p.box("Notification Event Consumer", "<<Component>>\nSchema/version validation\nDedup by eventId", 405, 210, 280, 135, "teal")
    pref = p.box("Preference Resolver", "<<Component>>\nCanal permitido / destino verificado\nOpt-in / quiet hours", 720, 210, 290, 135, "teal")
    template = p.box("Template & PII Renderer", "<<Component>>\nPlantilla versionada\nMinimiza datos financieros", 1045, 210, 300, 135, "teal")
    router = p.box("Channel Router", "<<Component>>\nPrioridad / fallback\nCircuit breaker por proveedor", 405, 465, 280, 135, "teal")
    pushad = p.box("Push Provider Adapter", "<<Component>>\nFCM / APNs contract", 720, 465, 290, 135, "teal")
    msgad = p.box("Email/SMS Provider Adapter", "<<Component>>\nProvider abstraction / TLS", 1045, 465, 300, 135, "teal")
    delivery = p.box("Delivery State Repository", "<<Component>>\nAccepted / failed / retrying\nIdempotent status updates", 405, 715, 280, 130, "blue")
    retry = p.box("Retry & DLQ Handler", "<<Component>>\nBackoff · bounded retries\nOperator redrive policy", 720, 715, 290, 130, "gold")
    audit = p.box("Notification Audit Publisher", "<<Component>>\nAttempt + provider response\nCorrelationId / eventId", 1045, 715, 300, 130, "red")
    push = p.box("Push systems", "FCM / APNs\nDelivery receipt if supported", 1675, 220, 285, 120, "purple")
    email = p.box("Email / SMS providers", "Independent delivery route\nProvider-specific status", 1985, 220, 340, 120, "purple")
    db = p.box("PostgreSQL HA", "Container C2 data service\nNotification state / attempts", 1675, 500, 285, 120, "blue")
    auditbus = p.box("Audit Event Bus / Store", "Container C2\nAppend-only evidence pipeline", 1985, 500, 340, 120, "red")
    p.edge(producer, bus, "TransactionPosted · Outbox", color="goldLine")
    p.edge(bus, consumer, "At-least-once", color="goldLine")
    p.edge(consumer, pref, "Validated event", color="tealLine")
    p.edge(pref, template, "Authorized destination", color="tealLine")
    p.edge(template, router, "Rendered safe payload", color="tealLine")
    p.edge(router, pushad, "Preferred / fallback route", color="tealLine")
    p.edge(router, msgad, "Fallback route", color="tealLine")
    p.edge(pushad, push, "TLS provider API", color="purpleLine")
    p.edge(msgad, email, "TLS provider API", color="purpleLine")
    p.edge(pushad, delivery, "Provider response", color="blueLine")
    p.edge(msgad, delivery, "Provider response", color="blueLine")
    p.edge(delivery, db, "Persist status", color="blueLine")
    p.edge(delivery, retry, "Failed / timeout", color="goldLine")
    p.edge(retry, bus, "Retry / DLQ", color="goldLine")
    p.edge(delivery, audit, "Attempt outcome", color="redLine", dashed=True)
    p.edge(audit, auditbus, "AuditEvent", color="redLine")
    p.note("BIAN / alcance", "Customer Event History puede registrar el evento de negocio del cliente; la entrega Push/Email/SMS se modela aquí como capacidad de solución y adaptadores técnicos, no como un Service Domain inventado. Notificar solo tras estado de movimiento confirmado y evitar montos/datos sensibles innecesarios en lock-screen o correo.", 405, 925, 1005, 145)
    return p


def page_infrastructure():
    p = Page("Despliegue C4 - Azure HA y DR", "infra-azure", 3000, 1850)
    p.box("VISTA DE DESPLIEGUE C4 | BANCA DIGITAL BP", "Vista complementaria de C2: contenedores desplegados en nodos Azure · HA por zonas · DR regional · red privada · seguridad y operación", 35, 20, 2930, 65, "blue")

    users = p.box("Clientes", "Banca web SPA\nAplicación móvil", 45, 215, 230, 120, "blue")
    afd = p.box("Azure Front Door Premium", "WAF + protección DDoS\nHealth probes / failover regional\nPrivate Link hacia orígenes", 315, 195, 340, 160, "gold")

    p.zone("REGIÓN PRIMARIA | Activa | 3 Availability Zones", 700, 110, 1200, 1260, "blue")
    p.zone("Hub de red y conectividad privada", 725, 160, 1150, 125, "gray")
    hub1 = p.box("Hub VNet", "Azure Firewall · NAT de egreso\nExpressRoute a BP + VPN S2S de respaldo\nPrivate DNS / Private Endpoints", 755, 200, 1090, 70, "gray")

    p.zone("Entrada regional y orígenes web", 725, 300, 1150, 175, "teal")
    apim1 = p.box("API Management Premium", "Gateway regional · zone redundant\nPolicies / JWT / quotas / API routing", 755, 345, 340, 100, "gold")
    web1 = p.box("Azure Storage Static Website", "Origen privado de la SPA\nPrivate Link desde Front Door", 1130, 345, 330, 100, "blue")
    intlb1 = p.box("Internal Load Balancer", "Solo tráfico privado hacia AKS\nSin endpoint público de aplicación", 1495, 345, 350, 100, "gray")

    p.zone("AKS privado | nodos y réplicas distribuidos entre zonas", 725, 495, 1150, 365, "teal")
    p.zone("AZ 1", 750, 545, 350, 285, "gray")
    p.zone("AZ 2", 1125, 545, 350, 285, "gray")
    p.zone("AZ 3", 1500, 545, 350, 285, "gray")
    az1 = p.box("Node pool", "BFF / API services\nRéplicas y probes", 775, 610, 300, 150, "teal")
    az2 = p.box("Node pool", "Servicios de dominio\nHPA / PDB / anti-affinity", 1150, 610, 300, 150, "teal")
    az3 = p.box("Node pool", "Workers de eventos\nAutoscaler / self-healing", 1525, 610, 300, 150, "teal")

    p.zone("Datos y mensajería | endpoints privados", 725, 880, 1150, 450, "gold")
    pg1 = p.box("Azure Database for PostgreSQL", "Primary + standby síncrono\nHA zone-redundant · endpoint privado", 750, 930, 260, 145, "blue")
    redis1 = p.box("Azure Managed Redis", "Cache de lecturas permitidas\nRecrear / repoblar en DR", 1025, 930, 245, 145, "blue")
    bus1 = p.box("Service Bus Premium", "Zone redundant · Topics / DLQ\nTransactional Outbox en servicios", 1285, 930, 265, 145, "gold")
    blob1 = p.box("Blob Storage de auditoría", "Immutable / WORM\nZRS en región primaria", 1565, 930, 280, 145, "red")
    kv1 = p.box("Key Vault + Managed Identity", "Secretos / certificados / CMK\nPrivate Endpoint + rotación", 850, 1120, 370, 120, "gold")
    mon1 = p.box("Monitorización regional", "Azure Monitor · App Insights · OTel\nLogs, métricas, trazas y alertas", 1260, 1120, 500, 120, "gold")

    p.zone("REGIÓN SECUNDARIA | DR | warm standby", 1920, 110, 1045, 1260, "purple")
    p.zone("Hub y conectividad de contingencia", 1945, 160, 995, 125, "gray")
    hub2 = p.box("Hub VNet DR", "Firewall / egress controlado\nExpressRoute o VPN redundante\nPrivate DNS y endpoints", 1975, 200, 935, 70, "gray")
    p.zone("Gateway, orígenes web y aplicación", 1945, 300, 995, 175, "teal")
    apim2 = p.box("API Management Premium", "Gateway regional secundario\nMisma configuración lógica multi-región", 1975, 345, 420, 100, "gold")
    web2 = p.box("Static Website secundario", "Origen de SPA para failover\nArtefacto publicado por CI/CD", 2420, 345, 490, 100, "blue")
    p.zone("AKS DR preaprovisionado", 1945, 495, 995, 365, "teal")
    aks2 = p.box("AKS warm standby", "Cluster independiente en la región DR\nCapacidad mínima activa; escala al failover\nRéplicas de servicios + health probes", 1980, 565, 925, 220, "teal")
    p.zone("Persistencia y recuperación de datos", 1945, 880, 995, 450, "gold")
    pg2 = p.box("PostgreSQL cross-region replica", "Replicación asíncrona\nPromoción controlada en desastre\nRPO depende de lag; medir y alertar", 1975, 930, 285, 155, "blue")
    bus2 = p.box("Service Bus DR namespace", "Geo-DR replica configuración / alias\nNo replica mensajes: reproceso desde Outbox", 2275, 930, 300, 155, "gold")
    blob2 = p.box("Auditoría / backups DR", "Geo-redundant copy / restore\nRetención según política", 2590, 930, 320, 155, "red")
    kv2 = p.box("Key Vault región DR", "Secretos / certificados sincronizados\nManaged Identity en workloads DR", 1975, 1130, 400, 120, "gold")
    mon2 = p.box("Health y runbooks DR", "Azure Monitor / alertas regionales\nFailover validado por runbook", 2390, 1130, 520, 120, "gold")

    p.zone("Dependencias corporativas, terceros y operación compartida", 35, 1390, 2930, 235, "purple", dashed=True)
    core = p.box("Core bancario BP", "Ledger / cuentas / movimientos", 60, 1450, 300, 120, "purple")
    details = p.box("Sistema de perfil detallado", "Fuente complementaria BP", 380, 1450, 300, 120, "purple")
    ci = p.box("IAM / CIAM existente", "OAuth 2.0 + OIDC\nJWKS / MFA / passkeys", 700, 1450, 330, 120, "purple")
    kyc = p.box("Proveedor facial / KYC", "Liveness / verificación de identidad", 1050, 1450, 330, 120, "purple")
    rail = p.box("Riel interbancario", "SPI/BCE o Banred\nsegún contrato y ruta", 1400, 1450, 330, 120, "purple")
    push = p.box("Proveedor Push", "FCM / APNs", 1750, 1450, 330, 120, "purple")
    msg = p.box("Proveedor Email / SMS", "Segunda ruta independiente", 2100, 1450, 330, 120, "purple")
    ops = p.box("Operación segura", "Sentinel / Defender for Cloud\nIaC + CI/CD", 2450, 1450, 470, 120, "red")

    p.edge(users, afd, "HTTPS / TLS", color="blueLine")
    p.edge(afd, apim1, "API · origin health", color="goldLine")
    p.edge(afd, web1, "SPA · Private Link", color="goldLine")
    p.edge(afd, apim2, "Failover por health probe", color="goldLine", dashed=True)
    p.edge(afd, web2, "Failover de origen SPA", color="goldLine", dashed=True)
    p.edge(hub1, apim1, "VNet privada", color="grayLine")
    p.edge(apim1, intlb1, "VNet integration", color="tealLine")
    p.edge(intlb1, az1, "Balanceo interno", color="tealLine")
    p.edge(intlb1, az2, "Balanceo interno", color="tealLine")
    p.edge(intlb1, az3, "Balanceo interno", color="tealLine")
    p.edge(az1, pg1, "TLS / Private Link", color="blueLine")
    p.edge(az2, redis1, "Cache privada", color="blueLine")
    p.edge(az2, bus1, "Outbox / eventos", color="goldLine")
    p.edge(az3, blob1, "Auditoría append-only", color="redLine")
    p.edge(az1, kv1, "Managed Identity", color="goldLine")
    p.edge(az3, mon1, "OTel / telemetría", color="goldLine")
    p.edge(pg1, pg2, "Replicación asíncrona", color="blueLine", dashed=True)
    p.edge(bus1, bus2, "Geo-DR: configuración; no payload", color="goldLine", dashed=True)
    p.edge(blob1, blob2, "Geo-redundancia / recuperación", color="redLine", dashed=True)
    p.edge(apim2, aks2, "VNet privada al activar DR", color="tealLine")
    p.edge(aks2, pg2, "Tras promoción / endpoint DR", color="blueLine")
    p.edge(aks2, bus2, "Reproceso Outbox tras failover", color="goldLine")
    p.edge(aks2, kv2, "Managed Identity", color="goldLine")
    p.edge(aks2, mon2, "OTel / health", color="goldLine")
    p.edge(hub1, core, "ExpressRoute + VPN backup", color="purpleLine")
    p.edge(hub1, details, "Private API / mTLS", color="purpleLine")
    p.edge(hub2, core, "Conectividad DR", color="purpleLine", dashed=True)
    p.edge(hub2, details, "Conectividad DR", color="purpleLine", dashed=True)
    p.edge(hub1, rail, "Firewall egress · mTLS", color="purpleLine")
    p.edge(hub1, kyc, "Firewall egress · TLS", color="purpleLine")
    p.edge(hub1, push, "TLS · retry / circuit breaker", color="purpleLine")
    p.edge(hub1, msg, "TLS · fallback", color="purpleLine")
    p.edge(apim1, ci, "OIDC discovery / JWKS", color="purpleLine", dashed=True)
    p.edge(mon1, ops, "Alertas / SIEM", color="redLine", dashed=True)

    p.note("Nodos de despliegue, contenedores C2 y límites HA/DR", "Los contenedores de BFF, APIs de dominio y workers de C2 corren como réplicas sobre AKS; PaaS como PostgreSQL, Redis y Service Bus se muestra como servicio administrado. HA primaria: distribución multi-AZ y PostgreSQL zone-redundant. DR: AKS warm standby y réplica PostgreSQL asíncrona; definir RTO/RPO y probar failover/failback. La réplica puede tener lag y exige promoción controlada. Service Bus Geo-DR replica configuración/alias, no mensajes; Outbox permite reprocesarlos. Orígenes privados, identidades administradas, IaC, health probes, autoscaling y runbooks.", 35, 1640, 2930, 125)
    return p


def main():
    pages = [page_c1_context(), page_containers(), page_components(),
             page_components_movements(), page_components_onboarding(),
             page_components_notifications(), page_infrastructure()]
    root = Element("mxfile", {
        "host": "app.diagrams.net", "modified": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "agent": "Codex - BP Solution Architecture", "version": "24.7.17", "type": "device",
        "pages": str(len(pages)), "compressed": "false",
    })
    for p in pages:
        root.append(p.diagram)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ElementTree(root).write(OUT, encoding="utf-8", xml_declaration=True)
    print(OUT)


if __name__ == "__main__":
    main()
