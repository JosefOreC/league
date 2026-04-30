import re
from datetime import datetime, timedelta
from ...domain.entities.nlp_analysis import NLPAnalysis, FieldExtraction
from ...domain.ports.nlp_analyzer_port import NLPAnalyzerPort
from ...domain.value_objects.enums.categoria import Categoria
from ...domain.value_objects.enums.nivel_tecnico import NivelTecnico
from ...domain.value_objects.enums.tipo_torneo import TipoTorneo
from ...domain.value_objects.enums.estado_analisis import EstadoAnalisis


class RulesBasedNLPAdapter(NLPAnalyzerPort):
    """
    Adaptador NLP basado en reglas y regex para texto libre en español.
    No requiere APIs externas; es reemplazable vía NLPAnalyzerPort.
    """

    _WORD_NUMBERS: dict[str, int] = {
        "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
        "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11,
        "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
        "dieciséis": 16, "dieciseis": 16, "diecisiete": 17,
        "dieciocho": 18, "diecinueve": 19, "veinte": 20,
        "veintiuno": 21, "veintidós": 22, "veintidos": 22,
        "veinticuatro": 24, "treinta": 30, "treintaidós": 32,
    }

    _CATEGORIA_PATTERNS: dict[Categoria, list[str]] = {
        Categoria.SECONDARY: [
            r"\bsecundari[ao]\b",
            r"\bbachiller(ato)?\b",
            r"\bsecondary\b",
        ],
        Categoria.PRIMARY: [
            r"\bprimari[ao]\b",
            r"\belemental\b",
            r"\bprimary\b",
        ],
    }

    _NIVEL_PATTERNS: dict[NivelTecnico, list[str]] = {
        NivelTecnico.BASICO: [
            r"\bb[aá]sico\b",
            r"\bprincipiante[s]?\b",
            r"\bnovato[s]?\b",
            r"\bbeginner[s]?\b",
        ],
        NivelTecnico.INTERMEDIO: [
            r"\bintermedi[ao]\b",
            r"\bintermediate\b",
        ],
        NivelTecnico.AVANZADO: [
            r"\bavanzad[ao]\b",
            r"\badvanced\b",
            r"\bexperto[s]?\b",
            r"\bprofesional(es)?\b",
        ],
    }

    _TIPO_PATTERNS: dict[TipoTorneo, list[str]] = {
        TipoTorneo.KNOCKOUT: [
            r"\belimi\w*\s+directa\b",
            r"\belimi\w*\s+simple\b",
            r"\bknockout\b",
            r"\bsingle\s+elimination\b",
        ],
        TipoTorneo.ROUND_ROBIN: [
            r"\btodos\s+contra\s+todos\b",
            r"\bliga\b",
            r"\bround[\s\-]?robin\b",
            r"\bfase\s+de\s+grupo[s]?\b",
            r"\bgrupo[s]?\b",
        ],
        TipoTorneo.HYBRID: [
            r"\bh[ií]brid[ao]\b",
        ],
    }

    _UNCATALOGUED_NIVEL: list[str] = [
        r"\buniversitari[ao]\b",
        r"\bsuperior\b",
    ]

    def analyze(self, text: str) -> NLPAnalysis:
        t = text.lower()

        numero_equipos = self._extract_numero_equipos(t)
        categoria      = self._extract_categoria(t)
        nivel_tecnico  = self._extract_nivel_tecnico(t)
        tipo_torneo    = self._extract_tipo_torneo(t)
        nombre         = self._extract_nombre(text)
        fecha_inicio   = self._extract_fecha_inicio(t)
        fecha_fin      = self._extract_fecha_fin(t, fecha_inicio.value if not fecha_inicio.missing else None)
        descripcion    = self._extract_descripcion(t, {
            "nombre": nombre.value,
            "categoria": categoria.value,
            "max_equipos": numero_equipos.value
        })
        intencion      = self._extract_intencion(text, t)

        campos_faltantes: list[str] = []
        advertencias: list[str] = []

        field_map = {
            "nombre":               nombre,
            "numero_equipos":       numero_equipos,
            "categoria":            categoria,
            "nivel_tecnico":        nivel_tecnico,
            "tipo_torneo_sugerido": tipo_torneo,
            "fecha_inicio":         fecha_inicio,
            "fecha_fin":            fecha_fin,
            "descripcion":          descripcion,
        }

        for nom, fe in field_map.items():
            if fe.missing:
                campos_faltantes.append(nom)
            elif fe.confidence < 0.6:
                val = fe.value.value if hasattr(fe.value, "value") else fe.value
                advertencias.append(
                    f"El campo '{nom}' fue extraído con baja confianza "
                    f"({fe.confidence:.2f}). Valor sugerido: {val}. "
                    "Por favor confirme antes de continuar."
                )

        if self._has_uncatalogued_nivel(t) and not nivel_tecnico.missing:
            advertencias.append(
                "El nivel mencionado no está en el catálogo "
                "(BASICO | INTERMEDIO | AVANZADO). "
                f"Nivel más cercano sugerido: {nivel_tecnico.value.value}."
            )

        return NLPAnalysis(
            numero_equipos=numero_equipos,
            categoria=categoria,
            nivel_tecnico=nivel_tecnico,
            tipo_torneo_sugerido=tipo_torneo,
            nombre=nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            descripcion=descripcion,
            intencion_usuario=intencion,
            estado_analisis=self._compute_estado(campos_faltantes),
            campos_faltantes=campos_faltantes,
            advertencias=advertencias,
        )

    def _extract_descripcion(self, text: str, info: dict) -> FieldExtraction:
        # Si el texto es muy largo, quizás ya es la descripción
        if len(text) > 100:
            return FieldExtraction(value=text.strip().capitalize(), confidence=0.7)
        
        # Si no, proponer una basada en lo que sabemos
        nombre = info.get("nombre") or "Torneo de Robótica"
        cat = info.get("categoria") or "Abierta"
        equipos = info.get("max_equipos") or "varios"
        
        propuesta = f"Competencia de robótica '{nombre}' diseñada para la categoría {cat}. Contaremos con la participación de hasta {equipos} equipos compitiendo por la excelencia técnica."
        return FieldExtraction(value=propuesta, confidence=0.8)

    def _extract_nombre(self, text: str) -> FieldExtraction:
        # Busca patrones como "nombre HOLA", "llamado HOLA", "torneo HOLA"
        patterns = [
            r"\bnombre\s+([A-Z0-9áéíóúÁÉÍÓÚñÑ ]+?)(?:\.|\s+y\s+|\s+que\s+|\s+será\b|$)",
            r"\bllamado\s+([A-Z0-9áéíóúÁÉÍÓÚñÑ ]+?)(?:\.|\s+y\s+|\s+que\s+|\s+será\b|$)",
            r"\btorneo\s+([A-Z0-9áéíóúÁÉÍÓÚñÑ ]+?)(?:\.|\s+y\s+|\s+que\s+|\s+será\b|$)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                if name:
                    return FieldExtraction(value=name, confidence=0.85)
        
        return FieldExtraction(value=None, confidence=0.0, missing=True)

    def _extract_numero_equipos(self, text: str) -> FieldExtraction:
        for pattern in (
            r"(?:para|con|de|máximo|maximo)\s+(\d+)\s*equipos?",
            r"(\d+)\s*equipos?\s*(?:participantes?|inscritos?)?",
            r"(\d+)\s*teams?",
        ):
            m = re.search(pattern, text)
            if m:
                return FieldExtraction(value=int(m.group(1)), confidence=0.95)

        for word, num in self._WORD_NUMBERS.items():
            if re.search(rf"\b{re.escape(word)}\s+equipos?\b", text):
                return FieldExtraction(value=num, confidence=0.85)

        return FieldExtraction(value=None, confidence=0.0, missing=True)

    def _extract_categoria(self, text: str) -> FieldExtraction:
        matches: dict[Categoria, int] = {}
        for cat, patterns in self._CATEGORIA_PATTERNS.items():
            for p in patterns:
                if re.search(p, text):
                    matches[cat] = matches.get(cat, 0) + 1

        if not matches:
            return FieldExtraction(value=None, confidence=0.0, missing=True)

        best = max(matches, key=matches.get)
        return FieldExtraction(value=best, confidence=0.92 if matches[best] > 1 else 0.87)

    def _extract_nivel_tecnico(self, text: str) -> FieldExtraction:
        matches: dict[NivelTecnico, int] = {}
        for nivel, patterns in self._NIVEL_PATTERNS.items():
            for p in patterns:
                if re.search(p, text):
                    matches[nivel] = matches.get(nivel, 0) + 1

        if not matches:
            return FieldExtraction(value=None, confidence=0.0, missing=True)

        best = max(matches, key=matches.get)
        confidence = 0.93 if matches[best] > 1 else 0.87

        if self._has_uncatalogued_nivel(text):
            confidence = 0.55

        return FieldExtraction(value=best, confidence=confidence)

    def _extract_tipo_torneo(self, text: str) -> FieldExtraction:
        matches: dict[TipoTorneo, int] = {}
        for tipo, patterns in self._TIPO_PATTERNS.items():
            for p in patterns:
                if re.search(p, text):
                    matches[tipo] = matches.get(tipo, 0) + 1

        if not matches:
            return FieldExtraction(value=None, confidence=0.0, missing=True)

        best = max(matches, key=matches.get)
        return FieldExtraction(value=best, confidence=0.92 if matches[best] > 1 else 0.88)

    def _extract_fecha_inicio(self, text: str) -> FieldExtraction:
        # "dentro de 20 días"
        m = re.search(r"dentro\s+de\s+(\d+|[\w]+)\s+d[ií]as?", text)
        if m:
            val = m.group(1)
            num = int(val) if val.isdigit() else self._WORD_NUMBERS.get(val, 0)
            if num:
                dt = datetime.now() + timedelta(days=num)
                return FieldExtraction(value=dt.strftime("%Y-%m-%d"), confidence=0.9)

        # "en 20 días"
        m = re.search(r"\ben\s+(\d+|[\w]+)\s+d[ií]as?", text)
        if m:
            val = m.group(1)
            num = int(val) if val.isdigit() else self._WORD_NUMBERS.get(val, 0)
            if num:
                dt = datetime.now() + timedelta(days=num)
                return FieldExtraction(value=dt.strftime("%Y-%m-%d"), confidence=0.85)

        return FieldExtraction(value=None, confidence=0.0, missing=True)

    def _extract_fecha_fin(self, text: str, start_date: str = None) -> FieldExtraction:
        # "termine en una semana"
        # "dure una semana"
        m = re.search(r"(?:termine|dure)\s+en\s+(una|1)\s+semana", text)
        if m:
            base = datetime.fromisoformat(start_date) if start_date else datetime.now()
            dt = base + timedelta(days=7)
            return FieldExtraction(value=dt.strftime("%Y-%m-%d"), confidence=0.9)

        # "dure X días"
        m = re.search(r"(?:termine|dure)\s+(?:en\s+)?(\d+|[\w]+)\s+d[ií]as?", text)
        if m:
            val = m.group(1)
            num = int(val) if val.isdigit() else self._WORD_NUMBERS.get(val, 0)
            if num:
                base = datetime.fromisoformat(start_date) if start_date else datetime.now()
                dt = base + timedelta(days=num)
                return FieldExtraction(value=dt.strftime("%Y-%m-%d"), confidence=0.85)

        return FieldExtraction(value=None, confidence=0.0, missing=True)

    def _has_uncatalogued_nivel(self, text: str) -> bool:
        return any(re.search(p, text) for p in self._UNCATALOGUED_NIVEL)

    def _extract_intencion(self, original: str, text_lower: str) -> str:
        parts: list[str] = []

        if any(w in text_lower for w in ("organizar", "crear", "hacer", "quiero", "necesito")):
            parts.append("organizar torneo")

        if any(w in text_lower for w in ("rápido", "rapido", "corto", "veloz")):
            parts.append("formato rápido")
        elif any(w in text_lower for w in ("más partidos", "mas partidos", "maximizar")):
            parts.append("maximizar partidos")

        for kw in ("robots", "robótica", "robotica", "fútbol", "futbol",
                   "básquet", "basquet", "baloncesto"):
            if kw in text_lower:
                parts.append(kw)
                break

        return ", ".join(parts) if parts else original[:500]

    @staticmethod
    def _compute_estado(campos_faltantes: list[str]) -> EstadoAnalisis:
        return EstadoAnalisis.COMPLETO if not campos_faltantes else EstadoAnalisis.AMBIGUO

    def _extract_numero_equipos(self, text: str) -> FieldExtraction:
        for pattern in (
            r"(?:para|con|de)\s+(\d+)\s*equipos?",
            r"(\d+)\s*equipos?\s*(?:participantes?|inscritos?)?",
            r"(\d+)\s*teams?",
        ):
            m = re.search(pattern, text)
            if m:
                return FieldExtraction(value=int(m.group(1)), confidence=0.95)

        for word, num in self._WORD_NUMBERS.items():
            if re.search(rf"\b{re.escape(word)}\s+equipos?\b", text):
                return FieldExtraction(value=num, confidence=0.85)

        return FieldExtraction(value=None, confidence=0.0, missing=True)

    def _extract_categoria(self, text: str) -> FieldExtraction:
        matches: dict[Categoria, int] = {}
        for cat, patterns in self._CATEGORIA_PATTERNS.items():
            for p in patterns:
                if re.search(p, text):
                    matches[cat] = matches.get(cat, 0) + 1

        if not matches:
            return FieldExtraction(value=None, confidence=0.0, missing=True)

        best = max(matches, key=matches.get)
        return FieldExtraction(value=best, confidence=0.92 if matches[best] > 1 else 0.87)

    def _extract_nivel_tecnico(self, text: str) -> FieldExtraction:
        matches: dict[NivelTecnico, int] = {}
        for nivel, patterns in self._NIVEL_PATTERNS.items():
            for p in patterns:
                if re.search(p, text):
                    matches[nivel] = matches.get(nivel, 0) + 1

        if not matches:
            return FieldExtraction(value=None, confidence=0.0, missing=True)

        best = max(matches, key=matches.get)
        confidence = 0.93 if matches[best] > 1 else 0.87

        if self._has_uncatalogued_nivel(text):
            confidence = 0.55

        return FieldExtraction(value=best, confidence=confidence)

    def _extract_tipo_torneo(self, text: str) -> FieldExtraction:
        matches: dict[TipoTorneo, int] = {}
        for tipo, patterns in self._TIPO_PATTERNS.items():
            for p in patterns:
                if re.search(p, text):
                    matches[tipo] = matches.get(tipo, 0) + 1

        if not matches:
            return FieldExtraction(value=None, confidence=0.0, missing=True)

        best = max(matches, key=matches.get)
        return FieldExtraction(value=best, confidence=0.92 if matches[best] > 1 else 0.88)

    def _has_uncatalogued_nivel(self, text: str) -> bool:
        return any(re.search(p, text) for p in self._UNCATALOGUED_NIVEL)

    def _extract_intencion(self, original: str, text_lower: str) -> str:
        parts: list[str] = []

        if any(w in text_lower for w in ("organizar", "crear", "hacer", "quiero", "necesito")):
            parts.append("organizar torneo")

        if any(w in text_lower for w in ("rápido", "rapido", "corto", "veloz")):
            parts.append("formato rápido")
        elif any(w in text_lower for w in ("más partidos", "mas partidos", "maximizar")):
            parts.append("maximizar partidos")

        for kw in ("robots", "robótica", "robotica", "fútbol", "futbol",
                   "básquet", "basquet", "baloncesto"):
            if kw in text_lower:
                parts.append(kw)
                break

        return ", ".join(parts) if parts else original[:500]

    @staticmethod
    def _compute_estado(campos_faltantes: list[str]) -> EstadoAnalisis:
        return EstadoAnalisis.COMPLETO if not campos_faltantes else EstadoAnalisis.AMBIGUO
