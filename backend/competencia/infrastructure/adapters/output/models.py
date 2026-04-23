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

    class Meta:
        db_table = "competencia_tournament"

    def __str__(self):
        return f"Tournament({self.id} - {self.name})"
