"""
Comando de datos de prueba para el módulo de Analítica (MVP3).

Inserta un torneo FINALIZADO completo y coherente para poder visualizar
las vistas HU-AN-01, 02, 04 y 08 conectadas al backend real.

Uso:
    python manage.py seed_analitica
    python manage.py seed_analitica --reset   # borra el torneo demo y lo recrea

IDs fijos para que coincidan con los enlaces del frontend:
    torneo_id = "1"
    equipo campeón = "1"  (RoboChampions)

NOTA: Los use cases de analítica esperan state == "FINISHED" y
      estado_resultado == "DEFINITIVE" (en inglés), por eso el seed usa
      esos valores literales.
"""
import random
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from competencia.infrastructure.adapters.output.models import (
    TournamentRuleModel,
    TournamentModel,
    CriteriaModel,
    InstitutionModel,
    DocenteAsesorModel,
    TeamModel,
    ParticipantModel,
    MatchModel,
    MatchResultModel,
    StandingModel,
    FinalRankingModel,
)

TORNEO_ID = "1"

CRITERIOS = [
    ("crit-1", "Precisión de navegación", 25.0),
    ("crit-2", "Tiempo de ejecución", 20.0),
    ("crit-3", "Innovación técnica", 20.0),
    ("crit-4", "Robustez del sistema", 20.0),
    ("crit-5", "Presentación oral", 15.0),
]

INSTITUCIONES = [
    ("ie-1", "I.E. San Ramón", "PUBLICA", "Huancayo"),
    ("ie-2", "I.E. Santa Isabel", "PUBLICA", "Huancayo"),
    ("ie-3", "I.E. Mariscal Castilla", "PRIVADA", "El Tambo"),
    ("ie-4", "I.E. Salesiano", "PRIVADA", "Huancayo"),
]

# (id, nombre, categoria, institucion_id, nivel, base_skill)
EQUIPOS = [
    ("1", "RoboChampions", "SECONDARY", "ie-1", "AVANZADO", 95),
    ("2", "Innova Robots", "SECONDARY", "ie-2", "AVANZADO", 89),
    ("3", "CircuitMasters", "PRIMARY", "ie-3", "INTERMEDIO", 85),
    ("4", "ByteRunners", "SECONDARY", "ie-4", "INTERMEDIO", 80),
    ("5", "TechBots Alpha", "PRIMARY", "ie-2", "BASICO", 76),
    ("6", "NanoBot Jr.", "PRIMARY", "ie-3", "BASICO", 71),
]

NOMBRES = ["Andrea", "Luis", "Diana", "José", "Camila", "Pedro", "Rosa", "Mateo"]
APELLIDOS = ["Quispe Ramos", "Mamani Torres", "Flores Inca", "Ccallo Huanca", "Rojas Vega", "Huamán Soto"]
ROLES = ["Capitán", "Programador", "Constructor", "Programadora"]


class Command(BaseCommand):
    help = "Inserta un torneo finalizado de prueba para el módulo de Analítica (MVP3)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Borra el torneo demo antes de recrearlo.")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        now = timezone.now()

        self._limpiar()
        self.stdout.write(self.style.WARNING("Datos demo previos eliminados."))

        # ── Regla del torneo ─────────────────────────────────────────────────
        rule = TournamentRuleModel.objects.create(
            id="rule-1", min_members=2, max_members=5, min_teams=2, max_teams=16,
            access_type="PUBLIC", validation_list=[], created_at=now, updated_at=now,
        )

        # ── Torneo (FINISHED) ────────────────────────────────────────────────
        torneo = TournamentModel.objects.create(
            id=TORNEO_ID,
            name="Torneo Regional de Robótica 2024",
            description="Torneo demo para visualizar el módulo de analítica MVP3.",
            date_start=now - timedelta(days=30),
            date_end=now - timedelta(days=2),
            state="FINISHED",
            category="constructor",
            creator_user_id="seed",
            tournament_rule=rule,
            config_tournament={},
        )

        # ── Instituciones + docentes ─────────────────────────────────────────
        instituciones = {}
        docentes = {}
        for iid, nombre, tipo, ciudad in INSTITUCIONES:
            inst = InstitutionModel.objects.create(
                id=iid, name=nombre, type=tipo, city=ciudad, country="PE",
            )
            instituciones[iid] = inst
            docentes[iid] = DocenteAsesorModel.objects.create(
                id=f"doc-{iid}", nombre_completo=f"Prof. Asesor {nombre}",
                email=f"asesor.{iid}@robotica.edu.pe", telefono="964000000", institution=inst,
            )

        # ── Criterios ────────────────────────────────────────────────────────
        criterios = []
        for cid, cname, peso in CRITERIOS:
            criterios.append(CriteriaModel.objects.create(
                id=cid, name=cname, description=cname, value=peso,
                min_value_qualification=0.0, max_value_qualification=100.0,
                created_at=now, updated_at=now, tournament=torneo,
            ))

        # ── Equipos + participantes ──────────────────────────────────────────
        equipos = {}
        bases = {}
        for tid, nombre, cat, iid, nivel, base in EQUIPOS:
            team = TeamModel.objects.create(
                id=tid, tournament=torneo, name=nombre, category=cat,
                institution=instituciones[iid], nivel_tecnico_declarado=nivel,
                estado_inscripcion="APROBADO", representante_id=f"rep-{tid}",
                docente_asesor=docentes[iid],
            )
            equipos[tid] = team
            bases[tid] = base
            n_part = 4
            for k in range(n_part):
                ParticipantModel.objects.create(
                    id=f"part-{tid}-{k}", team=team,
                    nombres=NOMBRES[(int(tid) + k) % len(NOMBRES)],
                    apellidos=APELLIDOS[(int(tid) + k) % len(APELLIDOS)],
                    edad=14 + (k % 4), grado_academico=f"{4 + (k % 2)}to Sec",
                    rol_en_equipo=ROLES[k % len(ROLES)],
                    documento_identidad=f"7000{tid}{k}", autorizacion_datos=(k != 2),
                )

        team_ids = [e[0] for e in EQUIPOS]
        total_norm = {tid: 0.0 for tid in team_ids}
        total_partidos = {tid: 0 for tid in team_ids}
        victorias = {tid: 0 for tid in team_ids}

        # ── Partidos por ronda (round-robin simple rotando emparejamientos) ──
        rondas = 5
        match_counter = 0
        for ronda in range(1, rondas + 1):
            rot = team_ids[:1] + team_ids[1:][ (ronda - 1) % (len(team_ids) - 1): ] + \
                  team_ids[1:][ : (ronda - 1) % (len(team_ids) - 1) ]
            pares = [(rot[0], rot[3]), (rot[1], rot[4]), (rot[2], rot[5])]
            for pos, (local, visit) in enumerate(pares):
                match_counter += 1
                mid = f"match-{match_counter}"
                match = MatchModel.objects.create(
                    id=mid, tournament=torneo, ronda=ronda, posicion_en_ronda=pos,
                    equipo_local=equipos[local], equipo_visitante=equipos[visit],
                    es_bye=False, es_descanso=False, fase="GRUPOS",
                    estado="FINISHED",
                    fecha_programada=now - timedelta(days=20 - ronda),
                )
                punt = {}
                for tid in (local, visit):
                    suma = 0.0
                    for crit in criterios:
                        c_off = {"crit-1": 4, "crit-2": -2, "crit-3": 1, "crit-4": -4, "crit-5": -6}[crit.id]
                        val = bases[tid] + c_off + random.uniform(-4, 4)
                        val = max(40.0, min(100.0, val))
                        MatchResultModel.objects.create(
                            id=f"res-{mid}-{tid}-{crit.id}", match=match, equipo=equipos[tid],
                            criterio=crit, valor_registrado=Decimal(str(round(val, 2))),
                            valor_normalizado=Decimal(str(round(val, 2))),
                            estado_resultado="DEFINITIVE", registrado_por="seed",
                        )
                        suma += val
                    punt[tid] = suma
                    total_norm[tid] += suma
                    total_partidos[tid] += 1
                ganador = local if punt[local] >= punt[visit] else visit
                victorias[ganador] += 1
                match.ganador_id = ganador
                match.save(update_fields=["ganador_id"])

        # ── Ranking final + standings ────────────────────────────────────────
        orden = sorted(team_ids, key=lambda t: total_norm[t], reverse=True)
        medallas = {0: "ORO", 1: "PLATA", 2: "BRONCE"}
        for pos, tid in enumerate(orden):
            FinalRankingModel.objects.create(
                tournament=torneo, team=equipos[tid], posicion_final=pos + 1,
                puntaje_total_acumulado=Decimal(str(round(total_norm[tid], 2))),
                medalla=medallas.get(pos),
                mencion_especial="Mejor en Precisión de navegación" if pos == 0 else None,
            )
            StandingModel.objects.create(
                tournament=torneo, team=equipos[tid], partidos_jugados=total_partidos[tid],
                victorias=victorias[tid], empates=0, derrotas=total_partidos[tid] - victorias[tid],
                puntos=victorias[tid] * 3,
                puntaje_favor=Decimal(str(round(total_norm[tid], 2))),
                puntaje_contra=Decimal("0"), diferencia_puntaje=Decimal(str(round(total_norm[tid], 2))),
                posicion=pos + 1,
            )

        self.stdout.write(self.style.SUCCESS("\n✅ Torneo demo creado correctamente.\n"))
        self.stdout.write(f"   Torneo ID:   {TORNEO_ID}  (state=FINISHED)")
        self.stdout.write(f"   Equipos:     {len(EQUIPOS)}   Partidos: {match_counter}   Criterios: {len(CRITERIOS)}")
        self.stdout.write(f"   Campeón:     {equipos[orden[0]].name} (equipo_id={orden[0]})\n")
        self.stdout.write("   Pruébalo en el frontend:")
        self.stdout.write(f"     /dashboard/torneos/{TORNEO_ID}/analisis-integral")
        self.stdout.write(f"     /dashboard/torneos/{TORNEO_ID}/tablero-inteligencia")
        self.stdout.write(f"     /dashboard/torneos/{TORNEO_ID}/equipos/{orden[0]}/reporte-individual")
        self.stdout.write(f"     /dashboard/torneos/{TORNEO_ID}/equipos/{orden[0]}/panel-docente\n")

    def _limpiar(self):
        """Borra el torneo demo y sus dependencias (idempotente)."""
        TournamentModel.objects.filter(pk=TORNEO_ID).delete()  # cascada: teams, matches, results, criteria, ranking, standings, participants
        DocenteAsesorModel.objects.filter(id__startswith="doc-ie-").delete()
        InstitutionModel.objects.filter(id__startswith="ie-").delete()
        TournamentRuleModel.objects.filter(pk="rule-1").delete()
