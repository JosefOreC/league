from django.db import models

class TournamentRuleModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    min_members = models.IntegerField()
    max_members = models.IntegerField()
    min_teams = models.IntegerField()
    max_teams = models.IntegerField()
    access_type = models.CharField(max_length=20)
    # Lista de institution_ids permitidas (solo aplica si access_type=PRIVATE)
    # Se almacena como JSON: ["id1", "id2", ...]
    validation_list = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "competencia_tournament_rule"

    def __str__(self):
        return f"TournamentRule({self.id})"

class CriteriaModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    value = models.FloatField()
    tournament_rule = models.ForeignKey(
        TournamentRuleModel,
        on_delete=models.CASCADE,
        related_name="criterias",
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
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

