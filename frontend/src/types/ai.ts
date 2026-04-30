import { CategoriaTorneo, TipoTorneo, ConfigTorneo, TipoDatoCriterio } from "./tournament";
import { NivelTecnico } from "./team";

// Posibles estados del análisis de texto libre por parte de la IA
export enum EstadoAnalisisIA {
  COMPLETO = "COMPLETO",
  AMBIGUO = "AMBIGUO",
  INCOMPLETO = "INCOMPLETO",
}

// Estructura de la respuesta al analizar el texto libre para crear un torneo
export interface AnalisisIAResponse {
  input_texto: string;
  numero_equipos: number | null;
  categoria: CategoriaTorneo | null;
  nivel_tecnico: NivelTecnico | null;
  tipo_torneo_sugerido: TipoTorneo | null;
  intencion_usuario: string;
  nivel_confianza: Record<string, number>;
  estado_analisis: EstadoAnalisisIA;
  campos_faltantes: string[];
  created_at: string;
}

// Estructura de la respuesta al pedir a la IA que recomiende un nivel de dificultad
export interface RecomendacionDificultadResponse {
  sesion_ia_id: string;
  nivel_recomendado: number; // 1 a 5
  nivel_confianza: number;
  justificacion: string;
  alertas: string[];
}

// Estructura de la respuesta al pedir a la IA que recomiende un formato de torneo
export interface RecomendacionFormatoResponse {
  sesion_ia_id: string;
  torneo_id: string;
  formato_recomendado: TipoTorneo;
  config_sugerida: ConfigTorneo;
  justificacion: string;
  nivel_confianza: number;
}

// Opciones de categorías de reglas que la IA puede generar
export enum CategoriaRegla {
  TIEMPO = "TIEMPO",
  DIMENSION = "DIMENSION",
  PESO = "PESO",
  PENALIZACION = "PENALIZACION",
  SEGURIDAD = "SEGURIDAD",
  OTRO = "OTRO",
}

// Estado de la regla generada
export enum EstadoRegla {
  SUGERIDA = "SUGERIDA",
  ACEPTADA = "ACEPTADA",
  MODIFICADA = "MODIFICADA",
  RECHAZADA = "RECHAZADA",
}

// Estructura de una regla operativa generada por la IA
export interface ReglaOperativa {
  id?: string;
  sesion_ia_id?: string;
  torneo_id: string;
  nombre: string;
  descripcion: string;
  valor: string;
  unidad: string | null;
  categoria_regla: CategoriaRegla;
  nivel_aplicable: number;
  estado: EstadoRegla;
  valor_editado?: string | null;
}

// Criterio generado por IA (HU-IA-05)
export interface CriterioEvaluacionIA {
  id: string;
  torneo_id: string;
  sesion_ia_id: string;
  nombre: string;
  descripcion: string;
  tipo_dato: TipoDatoCriterio;
  peso_porcentual: number;
  valor_minimo?: number;
  valor_maximo?: number;
  mayor_es_mejor: boolean;
  orden: number;
  estado: EstadoRegla;
}

// Respuesta a recomendación (HU-IA-06)
export interface AccionRecomendacionRequest {
  accion: "ACEPTAR" | "RECHAZAR" | "MODIFICAR";
  motivo?: string;
  valor_final?: any;
}
