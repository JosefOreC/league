import { PlayCircle, Shuffle, Swords, User, Trophy, GitFork } from "lucide-react";
import { useState } from "react";

export function Competitions() {
  const [activeFase, setActiveFase] = useState("Grupos");

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Competencias
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Visualiza y administra las llaves, fases y rondas del torneo activo.
          </p>
        </div>
        <button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm">
          <Shuffle className="mr-2 h-4 w-4" />
          Generar emparejamientos
        </button>
      </div>

      <div className="flex bg-white rounded-lg border border-slate-200 p-1 space-x-1 overflow-x-auto w-full md:w-max">
        <button
          onClick={() => setActiveFase("Grupos")}
          className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeFase === "Grupos"
              ? "bg-slate-100 text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
          }`}
        >
          <Swords className="mr-2 h-4 w-4" />
          Fases del torneo
        </button>
        <button
          onClick={() => setActiveFase("Rondas")}
          className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeFase === "Rondas"
              ? "bg-slate-100 text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
          }`}
        >
          <PlayCircle className="mr-2 h-4 w-4" />
          Rondas
        </button>
        <button
          onClick={() => setActiveFase("Llaves")}
          className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeFase === "Llaves"
              ? "bg-slate-100 text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
          }`}
        >
          <GitFork className="mr-2 h-4 w-4 transform -rotate-90" />
          Llaves
        </button>
      </div>

      {activeFase === "Llaves" ? (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 overflow-x-auto">
          <h2 className="text-lg font-semibold text-slate-900 mb-6 flex items-center">
            <Trophy className="mr-2 h-5 w-5 text-yellow-500" />
            Llave de Eliminación Directa
          </h2>
          
          <div className="flex gap-16 min-w-[800px] py-4 px-2">
            {/* Cuartos de final */}
            <div className="flex flex-col justify-around gap-8 w-64">
              <div className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wide text-center">Cuartos de final</div>
              
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 shadow-sm relative">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-200">
                  <span className="text-sm font-medium text-slate-900 truncate">RoboKids Alpha</span>
                  <span className="text-sm font-bold text-green-600">2</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-500 truncate">InnovaBots</span>
                  <span className="text-sm font-bold text-slate-400">1</span>
                </div>
                {/* Connector */}
                <div className="absolute top-1/2 -right-8 w-8 h-[2px] bg-slate-300"></div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 shadow-sm relative">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-200">
                  <span className="text-sm font-medium text-slate-500 truncate">TechSchool</span>
                  <span className="text-sm font-bold text-slate-400">0</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-900 truncate">CyberMentes</span>
                  <span className="text-sm font-bold text-green-600">3</span>
                </div>
                {/* Connectors */}
                <div className="absolute top-1/2 -right-8 w-8 h-[2px] bg-slate-300"></div>
                <div className="absolute -top-[calc(50%+1rem)] -right-8 w-[2px] h-[calc(100%+2rem)] bg-slate-300"></div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 shadow-sm relative">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-200">
                  <span className="text-sm font-medium text-slate-900 truncate">AndesBot</span>
                  <span className="text-sm font-bold text-green-600">2</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-500 truncate">Mecatrones</span>
                  <span className="text-sm font-bold text-slate-400">1</span>
                </div>
                {/* Connector */}
                <div className="absolute top-1/2 -right-8 w-8 h-[2px] bg-slate-300"></div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 shadow-sm relative">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-200">
                  <span className="text-sm font-medium text-slate-900 truncate">Pioneros</span>
                  <span className="text-sm font-bold text-green-600">2</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-500 truncate">Valle del Mantaro</span>
                  <span className="text-sm font-bold text-slate-400">0</span>
                </div>
                {/* Connectors */}
                <div className="absolute top-1/2 -right-8 w-8 h-[2px] bg-slate-300"></div>
                <div className="absolute -top-[calc(50%+1rem)] -right-8 w-[2px] h-[calc(100%+2rem)] bg-slate-300"></div>
              </div>
            </div>

            {/* Semifinales */}
            <div className="flex flex-col justify-center gap-16 w-64 relative py-12">
              <div className="absolute top-0 w-full text-center">
                <div className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wide">Semifinales</div>
              </div>
              
              <div className="bg-white border-2 border-blue-500 rounded-lg p-3 shadow-md relative z-10 ring-4 ring-blue-50">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-200">
                  <span className="text-sm font-bold text-slate-900 truncate">RoboKids Alpha</span>
                  <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-bold">En juego</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-bold text-slate-900 truncate">CyberMentes</span>
                  <span className="text-sm font-bold text-slate-400"></span>
                </div>
                {/* Connector */}
                <div className="absolute top-1/2 -right-8 w-8 h-[2px] bg-slate-300"></div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 shadow-sm relative z-10 opacity-70">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-200">
                  <span className="text-sm font-medium text-slate-500 truncate">AndesBot</span>
                  <span className="text-sm font-bold text-slate-400">-</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-500 truncate">Pioneros</span>
                  <span className="text-sm font-bold text-slate-400">-</span>
                </div>
                {/* Connectors */}
                <div className="absolute top-1/2 -right-8 w-8 h-[2px] bg-slate-300"></div>
                <div className="absolute -top-[calc(50%+2rem)] -right-8 w-[2px] h-[calc(100%+4rem)] bg-slate-300"></div>
              </div>
            </div>

            {/* Final */}
            <div className="flex flex-col justify-center w-64 relative">
              <div className="absolute top-0 w-full text-center">
                <div className="text-xs font-semibold text-yellow-600 mb-2 uppercase tracking-wide flex justify-center items-center">
                  <Trophy className="w-4 h-4 mr-1" /> Gran Final
                </div>
              </div>
              
              <div className="bg-slate-50 border border-dashed border-slate-300 rounded-lg p-3 relative z-10 opacity-50">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-200">
                  <span className="text-sm font-medium text-slate-400 italic">TBD</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-400 italic">TBD</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-12 text-center flex flex-col items-center justify-center">
          <div className="h-16 w-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mb-4">
            <Swords className="h-8 w-8" />
          </div>
          <h3 className="text-lg font-medium text-slate-900 mb-2">Vista de {activeFase}</h3>
          <p className="text-slate-500 max-w-md">Selecciona la pestaña "Llaves" para visualizar el árbol del torneo completo o utiliza las otras vistas para administrar los grupos y rondas de clasificación.</p>
        </div>
      )}
    </div>
  );
}
