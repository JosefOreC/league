from django.db import models

class TournamentRuleModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    min_members = models.IntegerField()
    max_members = models.IntegerField()
    min_teams = models.IntegerField()
    max_teams = models.IntegerField()
    access_type = models.CharField(max_length=20)
    validation_list = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    date_start_inscription = models.DateTimeField(blank=True, null=True)
    date_end_inscription = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = "competencia_tournament_rule"

    def __str__(self):
        return f"TournamentRule({self.id})"

class CriteriaModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    value = models.FloatField()
    min_value_qualification = models.FloatField(default=0.0)
    max_value_qualification = models.FloatField(default=10.0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    tournament = models.ForeignKey(
        'TournamentModel',
        on_delete=models.CASCADE,
        related_name="criterias",
        null=True
    )
    class Meta:
        db_table = "competencia_criteria"
    def __str__(self):
        return f"Criteria({self.id} - {self.name})"

class TournamentMemberModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user_id = models.CharField(max_length=36)
    tournament_id = models.CharField(max_length=36)
    rol = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    class Meta:
        db_table = "competencia_tournament_member"
    def __str__(self):
        return f"TournamentMember({self.id} - {self.user_id})"

class TournamentModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    state = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    creator_user_id = models.CharField(max_length=36)
    tournament_rule = models.OneToOneField(
        TournamentRuleModel,
        on_delete=models.PROTECT,
        related_name="tournament",
    )
    tournament_members = models.ManyToManyField(
        TournamentMemberModel,
        related_name="tournament",
    )
    config_tournament = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "competencia_tournament"

    def __str__(self):
        return f"Tournament({self.id} - {self.name})"


import uuid as _uuid


class CriterioIAModel(models.Model):
    id = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    torneo_id = models.CharField(max_length=36)
    sesion_ia_id = models.CharField(max_length=36, db_index=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, default="")
    tipo_dato = models.CharField(max_length=10)
    peso_porcentual = models.DecimalField(max_digits=5, decimal_places=2)
    valor_minimo = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    valor_maximo = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    mayor_es_mejor = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    estado = models.CharField(max_length=15, default="SUGERIDO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "competencia_criterio_ia"
        ordering = ["sesion_ia_id", "orden"]

    def __str__(self):
        return f"CriterioIA({self.nombre} – {self.peso_porcentual}%)"


class NLPAnalysisModel(models.Model):
    id = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    input_texto = models.TextField()
    numero_equipos = models.IntegerField(null=True, blank=True)
    categoria = models.CharField(max_length=20, null=True, blank=True)
    nivel_tecnico = models.CharField(max_length=20, null=True, blank=True)
    tipo_torneo_sugerido = models.CharField(max_length=20, null=True, blank=True)
    nombre_torneo = models.CharField(max_length=255, null=True, blank=True)
    fecha_inicio_sugerida = models.DateField(null=True, blank=True)
    fecha_fin_sugerida = models.DateField(null=True, blank=True)
    descripcion_sugerida = models.TextField(null=True, blank=True)
    intencion_usuario = models.TextField(blank=True, default="")
    nivel_confianza = models.JSONField(default=dict)
    estado_analisis = models.CharField(max_length=20)
    campos_faltantes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "competencia_nlp_analysis"
        ordering = ["-created_at"]

    def __str__(self):
        return f"NLPAnalysis({self.id} - {self.estado_analisis})"

class InstitutionModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=300)
    type = models.CharField(max_length=50) # PUBLICA | PRIVADA | CONCERTADA
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100) # ISO 3166-1 alpha-2
    class Meta:
        db_table = "competencia_institution"

class DocenteAsesorModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    institution = models.ForeignKey(InstitutionModel, on_delete=models.CASCADE)
    class Meta:
        db_table = "competencia_docente_asesor"

class TeamModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tournament = models.ForeignKey(TournamentModel, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50) # PRIMARY | SECONDARY
    institution = models.ForeignKey(InstitutionModel, on_delete=models.CASCADE)
    nivel_tecnico_declarado = models.CharField(max_length=50) # BASICO | INTERMEDIO | AVANZADO
    estado_inscripcion = models.CharField(max_length=50) # PENDIENTE | APROBADO | RECHAZADO
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    representante_id = models.CharField(max_length=36)
    docente_asesor = models.ForeignKey(DocenteAsesorModel, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "competencia_team"
        unique_together = ('tournament', 'name')

class ParticipantModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    team = models.ForeignKey(TeamModel, on_delete=models.CASCADE, related_name="participants")
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    edad = models.IntegerField()
    grado_academico = models.CharField(max_length=50)
    rol_en_equipo = models.CharField(max_length=100, blank=True, null=True)
    documento_identidad = models.CharField(max_length=50)
    autorizacion_datos = models.BooleanField()
    class Meta:
        db_table = "competencia_participant"

class GroupModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tournament = models.ForeignKey(TournamentModel, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=50) # Group A, B, C...
    class Meta:
        db_table = "competencia_group"

class MatchModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tournament = models.ForeignKey(TournamentModel, on_delete=models.CASCADE, related_name="matches")
    ronda = models.IntegerField()
    posicion_en_ronda = models.IntegerField()
    equipo_local = models.ForeignKey(TeamModel, on_delete=models.SET_NULL, null=True, related_name="matches_as_local")
    equipo_visitante = models.ForeignKey(TeamModel, on_delete=models.SET_NULL, null=True, related_name="matches_as_visitor")
    es_bye = models.BooleanField(default=False)
    es_descanso = models.BooleanField(default=False)
    grupo = models.ForeignKey(GroupModel, on_delete=models.SET_NULL, null=True, related_name="matches")
    fase = models.CharField(max_length=50, null=True, blank=True) # GRUPOS | FINAL
    estado = models.CharField(max_length=50, default="PENDING") # PENDING | IN_PROGRESS | FINISHED | BYE
    ganador_id = models.CharField(max_length=36, null=True, blank=True)
    partido_siguiente = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="partidos_anteriores")
    fecha_programada = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = "competencia_match"

class MatchResultModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    match = models.ForeignKey(MatchModel, on_delete=models.CASCADE, related_name="results")
    equipo = models.ForeignKey(TeamModel, on_delete=models.CASCADE)
    criterio = models.ForeignKey(CriteriaModel, on_delete=models.CASCADE)
    valor_registrado = models.DecimalField(max_digits=10, decimal_places=4)
    valor_normalizado = models.DecimalField(max_digits=10, decimal_places=4)
    estado_resultado = models.CharField(max_length=50) # PARTIAL | DEFINITIVE
    registrado_por = models.CharField(max_length=36)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "competencia_match_result"

class StandingModel(models.Model):
    tournament = models.ForeignKey(TournamentModel, on_delete=models.CASCADE, related_name="standings")
    team = models.ForeignKey(TeamModel, on_delete=models.CASCADE)
    group = models.ForeignKey(GroupModel, on_delete=models.SET_NULL, null=True, blank=True)
    partidos_jugados = models.IntegerField(default=0)
    victorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    puntos = models.IntegerField(default=0)
    puntaje_favor = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    puntaje_contra = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    diferencia_puntaje = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    posicion = models.IntegerField(default=0)
    
    class Meta:
        db_table = "competencia_standing"

class FinalRankingModel(models.Model):
    tournament = models.ForeignKey(TournamentModel, on_delete=models.CASCADE, related_name="final_ranking")
    team = models.ForeignKey(TeamModel, on_delete=models.CASCADE)
    posicion_final = models.IntegerField()
    puntaje_total_acumulado = models.DecimalField(max_digits=12, decimal_places=4)
    medalla = models.CharField(max_length=50, null=True, blank=True) # ORO | PLATA | BRONCE
    mencion_especial = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = "competencia_final_ranking"

