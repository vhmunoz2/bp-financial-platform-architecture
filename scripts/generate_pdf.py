from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Flowable, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "Propuesta_Arquitectura_Banca_Digital_BP.pdf"
SOURCE = ROOT / "docs" / "arquitectura.md"
PAGE = landscape(letter)
W, H = PAGE
NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#176B87")
TEAL = colors.HexColor("#D8F3EF")
PALE = colors.HexColor("#EAF1F8")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
ORANGE = colors.HexColor("#FFF1D6")
GREEN = colors.HexColor("#E3F5E8")
RED = colors.HexColor("#FCE8E6")


class ArchitectureDiagram(Flowable):
    """Compact, vector architecture diagram suitable for print and zoom."""
    def __init__(self, title, nodes, edges, width=730, height=420):
        super().__init__()
        self.title, self.nodes, self.edges = title, nodes, edges
        self.width, self.height = width, height

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(0, self.height - 22, self.title)
        c.setStrokeColor(colors.HexColor("#D9E2EC"))
        c.setLineWidth(.7)
        c.line(0, self.height - 31, self.width, self.height - 31)
        boxes = {n[0]: n[1:] for n in self.nodes}
        for src, dst, label in self.edges:
            x, y, w, h, *_ = boxes[src]
            x2, y2, w2, h2, *_ = boxes[dst]
            sx, sy = x + w/2, y + h/2
            ex, ey = x2 + w2/2, y2 + h2/2
            dx, dy = ex - sx, ey - sy
            if abs(dx) >= abs(dy):
                sx = x + (w if dx > 0 else 0)
                ex = x2 + (0 if dx > 0 else w2)
                sy, ey = y+h/2, y2+h2/2
            else:
                sy = y + (h if dy > 0 else 0)
                ey = y2 + (0 if dy > 0 else h2)
                sx, ex = x+w/2, x2+w2/2
            c.setStrokeColor(BLUE)
            c.setFillColor(BLUE)
            c.setLineWidth(1.05)
            c.line(sx, sy, ex, ey)
            import math
            ang = math.atan2(ey-sy, ex-sx)
            ah = 5
            p = c.beginPath()
            p.moveTo(ex, ey)
            p.lineTo(ex-ah*math.cos(ang-.45), ey-ah*math.sin(ang-.45))
            p.lineTo(ex-ah*math.cos(ang+.45), ey-ah*math.sin(ang+.45))
            p.close()
            c.drawPath(p, fill=1, stroke=0)
            if label:
                mx, my = (sx+ex)/2, (sy+ey)/2
                c.setFont("Helvetica", 6.5)
                tw = c.stringWidth(label, "Helvetica", 6.5)
                c.setFillColor(colors.white)
                c.rect(mx-tw/2-3, my-2, tw+6, 10, fill=1, stroke=0)
                c.setFillColor(INK)
                c.drawCentredString(mx, my+1, label)
        for node in self.nodes:
            key, x, y, w, h, text, tone = node
            fill = {"blue": PALE, "green": GREEN, "orange": ORANGE, "teal": TEAL, "red": RED}.get(tone, PALE)
            c.setFillColor(fill)
            c.setStrokeColor(BLUE if tone != "red" else colors.HexColor("#B42318"))
            c.setLineWidth(1)
            c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
            lines = text.split("\n")
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 8.3)
            line_h = 11
            start_y = y+h/2+(len(lines)-1)*line_h/2-3
            for i, line in enumerate(lines):
                c.drawCentredString(x+w/2, start_y-i*line_h, line)


def make_diagrams():
    return {
        "c1": ArchitectureDiagram("C1 | Contexto del sistema", [
            ("customer", 285, 315, 155, 54, "Cliente\nConsulta y ordena operaciones", "green"),
            ("sbi", 285, 205, 155, 62, "BP | Banca digital\nCanales, reglas y trazabilidad", "teal"),
            ("ops", 42, 213, 165, 50, "Operaciones y contact center\nSoporte con RBAC", "orange"),
            ("soc", 42, 92, 165, 50, "SOC / Seguridad\nAlertas e investigación", "orange"),
            ("idp", 520, 340, 175, 52, "IAM / CIAM\nOIDC, MFA, passkeys", "blue"),
            ("kyc", 520, 260, 175, 52, "Proveedor KYC\nDocumento + liveness", "blue"),
            ("core", 520, 180, 175, 52, "Core BP\nProductos, ledger, movimientos", "blue"),
            ("detail", 520, 100, 175, 52, "Perfil / detalle cliente\nDatos complementarios", "blue"),
            ("rail", 285, 65, 155, 50, "Red interbancaria\nEstado y liquidación", "orange"),
            ("channels", 285, 0, 155, 48, "FCM/APNs + Email/SMS\nEntrega multicanal", "orange"),
        ], [("customer","sbi","HTTPS"),("sbi","idp","OIDC"),("sbi","kyc","Onboarding"),
            ("sbi","core","API privada"),("sbi","detail","API privada"),("sbi","rail","Pago firmado"),
            ("sbi","channels","Eventos"),("ops","sbi","Consola"),("soc","sbi","Telemetría")], height=445),
        "c2": ArchitectureDiagram("C2 | Contenedores y límites de confianza", [
            ("web", 25, 340, 145, 50, "Angular SPA\nStatic hosting + CDN", "green"),
            ("mob", 25, 265, 145, 50, "React Native\nSystem browser + PKCE", "green"),
            ("edge", 210, 300, 155, 58, "Front Door + WAF\nDDoS / bot / TLS", "orange"),
            ("apim", 405, 300, 155, 58, "API Management\nJWT / quotas / routing", "orange"),
            ("bff", 600, 300, 125, 58, "Web + Mobile BFF\nSession / API", "teal"),
            ("domain", 240, 170, 250, 82, "Dominio\nProfile | Onboarding | Movements\nTransfers | Notifications", "teal"),
            ("adapters", 545, 170, 180, 82, "Integration ACL\nCore | Detail | Payment rail", "blue"),
            ("pg", 35, 50, 150, 62, "PostgreSQL HA\nState + Outbox per service", "blue"),
            ("redis", 220, 50, 150, 62, "Managed Redis\nAllowlisted cache", "blue"),
            ("bus", 405, 50, 150, 62, "Service Bus Premium\nTopics / DLQ", "orange"),
            ("audit", 590, 50, 135, 62, "Immutable audit\nBlob WORM", "red"),
            ("legacy", 545, 0, 180, 40, "Dependencias BP: Core | Detail | Rail", "orange"),
        ], [("web","edge","HTTPS"),("mob","edge","HTTPS"),("edge","apim","WAF"),
            ("apim","bff","OAuth2"),("bff","domain","REST"),("domain","adapters","REST/mTLS"),
            ("domain","pg","ACID"),("domain","redis","Cache-Aside"),("domain","bus","Outbox"),
            ("bus","audit","Events"),("adapters","legacy","mTLS / private")], height=440),
        "c3": ArchitectureDiagram("C3 | Componentes del servicio de transferencias", [
            ("client", 15, 310, 130, 56, "Canal + BFF\nCSRF/session", "green"),
            ("apim", 180, 310, 145, 56, "APIM\nJWT aud/scope", "orange"),
            ("api", 365, 310, 150, 56, "Transfer API\nOwnership + validation", "teal"),
            ("idem", 555, 310, 160, 56, "Idempotency handler\nUnique key + hash", "orange"),
            ("risk", 25, 205, 155, 62, "Policy / risk adapter\nLimits + step-up", "teal"),
            ("saga", 230, 200, 190, 72, "Persisted orchestrator\nState machine + reconciliation", "teal"),
            ("core", 485, 220, 115, 52, "Core adapter\nLedger", "blue"),
            ("rail", 620, 220, 115, 52, "Rail adapter\nSigned callback", "blue"),
            ("db", 60, 70, 190, 62, "PostgreSQL HA\nState + idempotency + Outbox", "blue"),
            ("relay", 300, 70, 125, 62, "Outbox relay\nAt-least-once", "orange"),
            ("bus", 480, 70, 120, 62, "Service Bus\nRetry + DLQ", "orange"),
            ("cons", 630, 70, 115, 62, "Audit + notify\nDedup eventId", "red"),
        ], [("client","apim","HTTPS"),("apim","api","JWT"),("api","idem","Order"),
            ("idem","risk","New key"),("risk","saga","Authorize"),("saga","core","Private mTLS"),
            ("saga","rail","mTLS"),("saga","db","ACID"),("db","relay","Outbox"),
            ("relay","bus","Event"),("bus","cons","Retry")], height=435),
        "onboarding": ArchitectureDiagram("Secuencia | Onboarding y autenticación", [
            ("c", 15, 265, 105, 52, "Cliente", "green"),("app", 155, 265, 120, 52, "Mobile app", "green"),
            ("ob", 310, 265, 130, 52, "Onboarding svc", "teal"),("kyc", 480, 265, 130, 52, "KYC + liveness", "orange"),
            ("iam", 635, 265, 110, 52, "CIAM OIDC", "blue"),
            ("core", 230, 95, 130, 52, "Core: alta", "blue"),("db", 425, 95, 145, 52, "DB + Outbox", "blue"),
        ], [("c","app","Inicia alta"),("app","ob","Sesión onboarding"),("ob","kyc","SDK cifrado"),
            ("kyc","ob","Resultado + referencia"),("ob","core","Alta idempotente"),("ob","db","Aprobado + Outbox"),
            ("app","iam","Code + PKCE S256"),("iam","app","Token / deep link")], height=390),
        "dr": ArchitectureDiagram("Infraestructura | Alta disponibilidad y recuperación", [
            ("user", 15, 315, 120, 52, "Clientes", "green"),("fd", 180, 315, 150, 52, "Front Door + WAF\nHealth probes", "orange"),
            ("region1", 375, 270, 165, 112, "Primaria - AZ A/B/C\nAPIM + compute + DB HA\nService Bus + Redis", "teal"),
            ("region2", 590, 270, 155, 112, "DR warm standby\nScale to ready\nPromoción controlada", "blue"),
            ("pg", 370, 100, 170, 55, "PITR / geo backup\nRPO objetivo <= 5 min*", "blue"),
            ("obs", 590, 100, 155, 55, "Azure Monitor / OTel\nAlertas + runbooks", "orange"),
            ("audit", 100, 100, 180, 55, "Audit Blob WORM\nRetención gobernada", "red"),
        ], [("user","fd","HTTPS"),("fd","region1","Primary"),("fd","region2","Failover"),
            ("region1","region2","Replicación"),("region1","pg","Backup"),("region1","audit","Eventos"),
            ("region1","obs","Métricas")], height=425),
    }


def md_inline(s):
    s = escape(s.strip())
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#176B87">\1</link>', s)
    s = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return s


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(30, 18, "BP | Propuesta de arquitectura de banca digital | 25 sep 2026")
    canvas.drawRightString(W-30, 18, f"{doc.page}")
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(30, 27, W-30, 27)
    canvas.restoreState()


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodyBP", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.1, leading=13, textColor=INK, spaceAfter=6))
    styles.add(ParagraphStyle(name="H1BP", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=NAVY, spaceBefore=10, spaceAfter=9, keepWithNext=True))
    styles.add(ParagraphStyle(name="H2BP", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=BLUE, spaceBefore=11, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle(name="H3BP", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle(name="SmallBP", parent=styles["BodyBP"], fontSize=7.3, leading=9, spaceAfter=2))
    styles.add(ParagraphStyle(name="CoverTitle", fontName="Helvetica-Bold", fontSize=30, leading=36, textColor=NAVY, alignment=TA_LEFT, spaceAfter=12))
    styles.add(ParagraphStyle(name="CoverSub", fontName="Helvetica", fontSize=14, leading=20, textColor=BLUE, spaceAfter=14))
    doc = BaseDocTemplate(str(OUT), pagesize=PAGE, title="Propuesta de arquitectura de banca digital para BP", author="Propuesta técnica")
    frame = Frame(38, 40, W-76, H-78, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="normal")
    doc.addPageTemplates([PageTemplate(id="landscape", frames=[frame], onPage=footer)])
    story = [Spacer(1, 60), Paragraph("Propuesta de arquitectura<br/>de banca digital para BP", styles["CoverTitle"]),
             Paragraph("Diseño C4, seguridad, operaciones financieras y resiliencia sobre Azure", styles["CoverSub"]),
             Spacer(1, 18), Paragraph("Una arquitectura para web y móvil que integra el Core y los sistemas de cliente, protege las operaciones y desacopla auditoría y notificaciones sin duplicar el ledger.", styles["BodyBP"]),
             Spacer(1, 90), Paragraph("Ejercicio de Arquitecto de Soluciones | Devsu", styles["H2BP"]),
             Paragraph("Documento de diseño · 25 de septiembre de 2026", styles["BodyBP"]), PageBreak()]
    diagrams = make_diagrams()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    i, para = 0, []
    def flush():
        nonlocal para
        if para:
            txt = " ".join(x.strip() for x in para)
            story.append(Paragraph(md_inline(txt), styles["BodyBP"]))
            para = []
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush(); i += 1; continue
        if line.startswith("#"):
            flush()
            level = len(line)-len(line.lstrip("#"))
            title = line[level:].strip()
            if level == 1 and title.startswith("Propuesta de arquitectura"):
                i += 1; continue
            if title == "3. C4":
                i += 1; continue
            if title == "Fuentes oficiales y estándares":
                story.append(PageBreak())
            if title.startswith("C1 -"):
                story += [PageBreak(), Paragraph(md_inline(title), styles["H2BP"]), diagrams["c1"], Spacer(1, 10)]
            elif title.startswith("C2 -"):
                story += [PageBreak(), Paragraph(md_inline(title), styles["H2BP"]), diagrams["c2"], Spacer(1, 10)]
            elif title.startswith("C3 -"):
                story += [PageBreak(), Paragraph(md_inline(title), styles["H2BP"]), diagrams["c3"], Spacer(1, 10)]
            else:
                style = styles["H1BP"] if level == 1 else styles["H2BP"] if level == 2 else styles["H3BP"]
                story.append(Paragraph(md_inline(title), style))
            i += 1; continue
        if line.startswith("|"):
            flush(); rows=[]
            while i < len(lines) and lines[i].startswith("|"):
                vals=[v.strip() for v in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", v or "-") for v in vals):
                    rows.append([Paragraph(md_inline(v), styles["SmallBP"]) for v in vals])
                i += 1
            if rows:
                t=Table(rows, repeatRows=1, hAlign="LEFT")
                t.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#CBD5E1")),
                    ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,PALE]),
                    ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
                    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ]))
                story += [t, Spacer(1,7)]
            continue
        if re.match(r"^[-*] ",line):
            flush(); story.append(Paragraph("•  "+md_inline(line[2:]), styles["BodyBP"])); i += 1; continue
        if re.match(r"^\d+\. ",line):
            flush(); story.append(Paragraph(md_inline(line), styles["BodyBP"])); i += 1; continue
        if line.startswith(">"):
            flush(); story.append(Paragraph('<font color="#176B87"><i>'+md_inline(line[1:])+'</i></font>', styles["BodyBP"])); i += 1; continue
        para.append(line); i += 1
    flush()
    story += [PageBreak(), Paragraph("Diagramas de apoyo", styles["H1BP"]),
              Paragraph("Estos diagramas resumen los flujos y despliegue. Los archivos Mermaid fuente se entregan en la carpeta diagrams.", styles["BodyBP"]),
              diagrams["onboarding"], Spacer(1, 10),
              Paragraph("El proveedor biométrico valida identidad durante el alta. En autenticación habitual, la biometría permanece en el dispositivo y desbloquea una credencial criptográfica.", styles["BodyBP"]),
              PageBreak(), diagrams["dr"], Spacer(1, 10),
              Paragraph("* Objetivos de ejemplo para discusión. Deben validarse en el análisis de impacto y con los SLA del Core; el Core mantiene autoridad contable.", styles["SmallBP"])]
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
