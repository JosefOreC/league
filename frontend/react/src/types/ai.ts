import { TipoTorneo, ConfigTorneo } from "./tournament";

// Posibles estados del análisis de texto libre por parte de la IA
export enum EstadoAnalisisIA {
  COMPLETO = "COMPLETO",
  AMBIGUO = "AMBIGUO",
  INCOMPLETO = "INCOMPLETO",
}

// Estructura de un campo extraído por la IA (con confianza y flag de faltante)
export interface FieldExtraction<T> {
  value: T | null;
  confidence: number;
  missing: boolean;
}

// Estructura REAL de la respuesta del backend (NLPAnalysis.to_dict())
export interface AnalisisIAResponse {
  numero_equipos:       FieldExtraction<number>;
  categoria:            FieldExtraction<string>;
  nivel_tecnico:        FieldExtraction<string>;
  tipo_torneo_sugerido: FieldExtraction<string>;
  nombre:               FieldExtraction<string>;
  fecha_inicio:         FieldExtraction<string>;
  fecha_fin:            FieldExtraction<string>;
  descripcion:          FieldExtraction<string>;
  nivel_confianza:      Record<string, number>;
  intencion_usuario:    string;
  estado_analisis:      EstadoAnalisisIA;
  campos_faltantes:     string[];
  advertencias?:        string[];
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

// Criterio generado por IA (HU-IA-05) — coincide con CriterioIA.to_dict() del backend
export interface CriterioEvaluacionIA {
  id: string;
  torneo_id: string;
  sesion_ia_id: string;
  nombre: string;
  descripcion: string;
  tipo_dato: string;            // "NUMERICO" | "BOOLEANO"
  peso_porcentual: number;      // 0.01 – 100.00; suma del conjunto = 100
  valor_minimo: number | null;
  valor_maximo: number | null;
  mayor_es_mejor: boolean;
  orden: number;
  estado: string;               // "SUGERIDO" | "MODIFICADO" | "ACEPTADO" | "RECHAZADO"
}

// Respuesta a recomendación (HU-IA-06)
export interface AccionRecomendacionRequest {
  accion: "ACEPTAR" | "RECHAZAR" | "MODIFICAR";
  motivo?: string;
  valor_final?: any;
}
