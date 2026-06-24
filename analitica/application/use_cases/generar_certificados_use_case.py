import hashlib
import uuid
from io import BytesIO
from zipfile import ZipFile

from ...domain.ports.certificados_repository_port import ICertificadosRepository
from ...domain.entities.certificado_digital import CertificadoDigital
from ...domain.exceptions import (
    TorneoNoEncontradoException,
    TorneoNoFinalizadoException,
    EquipoNoEncontradoException,
)


def _codigo_verificacion() -> str:
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()


class GenerarCertificadosUseCase:
    """
    Orquesta HU-AN-06.
    PARTICIPACION → certifica a cada participante con autorizacion_datos=TRUE.
    GANADOR       → diploma para el equipo con medalla ORO.
    """

    def __init__(self, repository: ICertificadosRepository) -> None:
        self._repo = repository

    # ── PARTICIPACION ─────────────────────────────────────────────────────────

    def ejecutar_participacion(self, torneo_id: str) -> dict:
        """
        Retorna:
        {
            "total_generados": int,
            "excluidos": [{"participante_id": str, "razon": str}],
            "zip_buffer": BytesIO,           ← ZIP con todos los PDFs
        }
        """
        self._validar_torneo_finished(torneo_id)

        participantes = self._repo.obtener_participantes(torneo_id)
        generados: list[CertificadoDigital] = []
        excluidos: list[dict] = []
        buffers: dict[str, bytes] = {}   # nombre_archivo → bytes

        for p in participantes:
            if not p.autorizacion_datos:
                excluidos.append({
                    "participante_id": p.participante_id,
                    "razon": "sin_autorizacion_datos",
                })
                continue

            cert = self._repo.guardar_certificado(
                torneo_id=torneo_id,
                tipo_certificado='PARTICIPACION',
                nombres_destinatario=f"{p.nombres} {p.apellidos}",
                institucion=p.institucion_nombre,
                codigo_verificacion=_codigo_verificacion(),
                participante_id=p.participante_id,
                equipo_id=p.equipo_id,
                posicion_final=None,
                medalla=None,
            )
            generados.append(cert)
            pdf_bytes = _generar_pdf_participacion(p, cert.codigo_verificacion)
            nombre = f"cert_{p.apellidos}_{p.nombres}_{p.participante_id[:8]}.pdf"
            buffers[nombre] = pdf_bytes

        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zf:
            for nombre, pdf in buffers.items():
                zf.writestr(nombre, pdf)
        zip_buffer.seek(0)

        return {
            "total_generados": len(generados),
            "excluidos":       excluidos,
            "zip_buffer":      zip_buffer,
        }

    # ── GANADOR ───────────────────────────────────────────────────────────────

    def ejecutar_ganador(self, torneo_id: str, equipo_id: str) -> dict:
        """
        Retorna:
        {
            "pdf_buffer": BytesIO,
            "equipo_nombre": str,
            "medalla": str,
            "codigo_verificacion": str,
        }
        """
        self._validar_torneo_finished(torneo_id)

        datos = self._repo.obtener_datos_ganador(torneo_id, equipo_id)
        if datos is None:
            raise EquipoNoEncontradoException(equipo_id, torneo_id)

        cert = self._repo.guardar_certificado(
            torneo_id=torneo_id,
            tipo_certificado='GANADOR',
            nombres_destinatario=datos.equipo_nombre,
            institucion=datos.institucion_nombre,
            codigo_verificacion=_codigo_verificacion(),
            participante_id=None,
            equipo_id=equipo_id,
            posicion_final=datos.posicion_final,
            medalla=datos.medalla,
        )

        pdf_bytes = _generar_pdf_ganador(datos, cert.codigo_verificacion)
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)

        return {
            "pdf_buffer":          pdf_buffer,
            "equipo_nombre":       datos.equipo_nombre,
            "medalla":             datos.medalla,
            "codigo_verificacion": cert.codigo_verificacion,
        }

    # ── privados ─────────────────────────────────────────────────────────────

    def _validar_torneo_finished(self, torneo_id: str) -> None:
        estado = self._repo.obtener_estado_torneo(torneo_id)
        if estado is None:
            raise TorneoNoEncontradoException(torneo_id)
        if (estado or '').lower() != 'finalized':
            raise TorneoNoFinalizadoException(torneo_id, estado)


# ── Generadores de PDF (reportlab) ────────────────────────────────────────────

def _generar_pdf_participacion(p, codigo: str) -> bytes:
    from io import BytesIO
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=3*cm, rightMargin=3*cm)

    titulo  = ParagraphStyle('T', fontSize=28, leading=34, alignment=TA_CENTER,
                             textColor=colors.HexColor('#1a1a2e'), fontName='Helvetica-Bold')
    subtit  = ParagraphStyle('S', fontSize=14, leading=18, alignment=TA_CENTER,
                             textColor=colors.HexColor('#444'))
    nombre_ = ParagraphStyle('N', fontSize=22, leading=28, alignment=TA_CENTER,
                             textColor=colors.HexColor('#1a1a2e'), fontName='Helvetica-Bold')
    body_   = ParagraphStyle('B', fontSize=12, leading=16, alignment=TA_CENTER,
                             textColor=colors.HexColor('#333'))
    code_   = ParagraphStyle('C', fontSize=8, leading=10, alignment=TA_CENTER,
                             textColor=colors.grey)

    story = [
        Spacer(1, 0.5*cm),
        Paragraph("CERTIFICADO DE PARTICIPACIÓN", titulo),
        Spacer(1, 0.4*cm),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')),
        Spacer(1, 0.6*cm),
        Paragraph("Se certifica que", subtit),
        Spacer(1, 0.3*cm),
        Paragraph(f"{p.nombres} {p.apellidos}", nombre_),
        Spacer(1, 0.4*cm),
        Paragraph(
            f"participó representando al equipo <b>{p.equipo_nombre}</b> "
            f"de la institución <b>{p.institucion_nombre}</b> "
            f"en el torneo <b>{p.torneo_nombre}</b>.",
            body_,
        ),
        Spacer(1, 0.3*cm),
        Paragraph(f"Fecha del torneo: {p.torneo_fecha[:10]}", body_),
        Spacer(1, 0.8*cm),
        HRFlowable(width="100%", thickness=1, color=colors.grey),
        Spacer(1, 0.2*cm),
        Paragraph(f"Código de verificación: {codigo}", code_),
    ]

    doc.build(story)
    buf.seek(0)
    return buf.read()


def _generar_pdf_ganador(datos, codigo: str) -> bytes:
    from io import BytesIO
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    MEDALLA_COLOR = {
        'ORO':   colors.HexColor('#FFD700'),
        'PLATA': colors.HexColor('#C0C0C0'),
        'BRONCE': colors.HexColor('#CD7F32'),
    }

    buf  = BytesIO()
    doc  = SimpleDocTemplate(buf, pagesize=landscape(A4),
                             topMargin=1.5*cm, bottomMargin=2*cm,
                             leftMargin=3*cm, rightMargin=3*cm)
    color_medalla = MEDALLA_COLOR.get(datos.medalla, colors.grey)

    titulo  = ParagraphStyle('T', fontSize=30, leading=36, alignment=TA_CENTER,
                             textColor=color_medalla, fontName='Helvetica-Bold')
    subtit  = ParagraphStyle('S', fontSize=13, leading=18, alignment=TA_CENTER,
                             textColor=colors.HexColor('#444'))
    nombre_ = ParagraphStyle('N', fontSize=24, leading=30, alignment=TA_CENTER,
                             textColor=colors.HexColor('#1a1a2e'), fontName='Helvetica-Bold')
    body_   = ParagraphStyle('B', fontSize=11, leading=15, alignment=TA_CENTER,
                             textColor=colors.HexColor('#333'))
    code_   = ParagraphStyle('C', fontSize=8, leading=10, alignment=TA_CENTER,
                             textColor=colors.grey)

    participantes_txt = " • ".join(
        f"{n} {a}" for n, a in datos.participantes
    )

    story = [
        Spacer(1, 0.3*cm),
        Paragraph(f"🏆 DIPLOMA DE {datos.medalla}", titulo),
        Spacer(1, 0.3*cm),
        HRFlowable(width="100%", thickness=3, color=color_medalla),
        Spacer(1, 0.4*cm),
        Paragraph("Se otorga el presente reconocimiento al equipo", subtit),
        Spacer(1, 0.2*cm),
        Paragraph(datos.equipo_nombre, nombre_),
        Spacer(1, 0.3*cm),
        Paragraph(
            f"de la institución <b>{datos.institucion_nombre}</b>, "
            f"por haber obtenido el <b>puesto {datos.posicion_final}</b> "
            f"en el torneo <b>{datos.torneo_nombre}</b> "
            f"con un puntaje de <b>{datos.puntaje_total_acumulado:.2f}</b>.",
            body_,
        ),
        Spacer(1, 0.3*cm),
        Paragraph(f"Integrantes: {participantes_txt}", body_),
    ]

    if datos.mencion_especial:
        story += [
            Spacer(1, 0.2*cm),
            Paragraph(f"Mención especial: {datos.mencion_especial}", body_),
        ]

    story += [
        Spacer(1, 0.3*cm),
        Paragraph(f"Fecha: {datos.torneo_fecha[:10]}", body_),
        Spacer(1, 0.6*cm),
        HRFlowable(width="100%", thickness=1, color=colors.grey),
        Spacer(1, 0.2*cm),
        Paragraph(f"Código de verificación: {codigo}", code_),
    ]

    doc.build(story)
    buf.seek(0)
    return buf.read()
