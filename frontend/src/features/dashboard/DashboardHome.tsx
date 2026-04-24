import {
  Trophy,
  Users,
  Award,
  TrendingUp,
  BrainCircuit,
  ArrowRight,
  MoreVertical,
  Zap
} from "lucide-react";
import { Link } from "react-router";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ImageWithFallback } from "../../components/ui/ImageWithFallback";

const data = [
  { name: "Ene", equipos: 10 },
  { name: "Feb", equipos: 25 },
  { name: "Mar", equipos: 45 },
  { name: "Abr", equipos: 60 },
  { name: "May", equipos: 90 },
  { name: "Jun", equipos: 120 },
  { name: "Jul", equipos: 150 },
];

export function DashboardHome() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Resumen General
        </h1>
        <div className="flex space-x-3">
          <Link
            to="/dashboard/torneos/nuevo"
            className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2"
          >
            Nuevo Torneo
          </Link>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* KPI Cards */}
        <div className="rounded-xl border border-slate-200 bg-white text-slate-950 shadow-sm p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium text-slate-500">
              Torneos Activos
            </h3>
            <Trophy className="h-4 w-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold">4</div>
          <p className="text-xs text-slate-500 flex items-center mt-1">
            <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
            <span className="text-green-600 font-medium">+2</span> desde el mes pasado
          </p>
        </div>
        
        <div className="rounded-xl border border-slate-200 bg-white text-slate-950 shadow-sm p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium text-slate-500">
              Equipos Inscritos
            </h3>
            <Users className="h-4 w-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold">150</div>
          <p className="text-xs text-slate-500 flex items-center mt-1">
            <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
            <span className="text-green-600 font-medium">+15%</span> crecimiento
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white text-slate-950 shadow-sm p-6">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium text-slate-500">
              Partidas Hoy
            </h3>
            <Zap className="h-4 w-4 text-yellow-500" />
          </div>
          <div className="text-2xl font-bold">24</div>
          <p className="text-xs text-slate-500 flex items-center mt-1">
            Fase de grupos en curso
          </p>
        </div>

        <div className="rounded-xl border border-purple-200 bg-purple-900 text-white shadow-sm relative overflow-hidden group">
          <ImageWithFallback
            src="https://images.unsplash.com/photo-1770233621425-5d9ee7a0a700?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhYnN0cmFjdCUyMGFpJTIwYnJhaW4lMjB0ZWNobm9sb2d5fGVufDF8fHx8MTc3NTc0Mjg4Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
            alt="AI Brain"
            className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-40 group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-purple-900/90 to-purple-800/80 z-10"></div>
          
          <div className="p-6 relative z-20 flex flex-col h-full justify-between">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-bold text-purple-100 flex items-center">
                <BrainCircuit className="h-4 w-4 mr-2 text-purple-300" />
                Recomendación IA
              </h3>
            </div>
            <div>
              <div className="text-sm font-medium mt-1 text-white leading-snug">
                Sugerimos dividir el "Torneo Regional Huancayo" en 2 categorías por edad.
              </div>
              <Link to="/dashboard/ia" className="inline-flex items-center mt-4 text-xs font-semibold bg-white/20 hover:bg-white/30 text-white px-3 py-1.5 rounded-full transition-colors backdrop-blur-sm">
                Ver análisis <ArrowRight className="h-3 w-3 ml-1.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col">
          <div className="flex flex-col space-y-1.5 p-6 pb-2">
            <h3 className="font-semibold leading-none tracking-tight">Crecimiento de Equipos</h3>
            <p className="text-sm text-slate-500">Equipos inscritos en los últimos 7 meses</p>
          </div>
          <div className="p-6 pt-0 flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} id="dashboard-area-chart">
                <defs key="defs">
                  <linearGradient id="colorEquipos" x1="0" y1="0" x2="0" y2="1">
                    <stop key="top" offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop key="bottom" offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis key="x-axis" dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis key="y-axis" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                <CartesianGrid key="grid" strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <Tooltip 
                  key="tooltip"
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                  itemStyle={{ color: '#0F172A', fontWeight: 600 }}
                />
                <Area key="area" type="monotone" dataKey="equipos" stroke="#3B82F6" strokeWidth={3} fillOpacity={1} fill="url(#colorEquipos)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="col-span-3 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="font-semibold leading-none tracking-tight">Resultados Recientes</h3>
            <p className="text-sm text-slate-500">Últimos enfrentamientos finalizados</p>
          </div>
          <div className="p-6 pt-0 flex-1">
            <div className="space-y-6">
              {[
                { time: "Hace 10 min", team1: "RoboKids Hyo.", score1: 150, team2: "InnovaBots", score2: 120, winner: 1, img1: "https://i.pravatar.cc/150?u=robokids", img2: "https://i.pravatar.cc/150?u=innova" },
                { time: "Hace 45 min", team1: "TechSchool", score1: 95, team2: "CyberMentes", score2: 110, winner: 2, img1: "https://i.pravatar.cc/150?u=tech", img2: "https://i.pravatar.cc/150?u=cyber" },
                { time: "Hace 2 hrs", team1: "AndesBot", score1: 200, team2: "Mecatrones", score2: 195, winner: 1, img1: "https://i.pravatar.cc/150?u=andes", img2: "https://i.pravatar.cc/150?u=meca" },
                { time: "Ayer", team1: "V. Mantaro", score1: 180, team2: "Pioneros", score2: 160, winner: 1, img1: "https://i.pravatar.cc/150?u=valle", img2: "https://i.pravatar.cc/150?u=pion" },
              ].map((match, i) => (
                <div key={i} className="flex items-center justify-between border-b border-slate-100 pb-4 last:border-0 last:pb-0">
                  <div className="flex flex-col items-center flex-1">
                    <img src={match.img1} alt={match.team1} className="w-8 h-8 rounded-full mb-2 border-2 border-white shadow-sm" />
                    <span className={`text-xs font-semibold truncate max-w-[90px] ${match.winner === 1 ? 'text-slate-900' : 'text-slate-500'}`}>
                      {match.team1}
                    </span>
                    <span className={`text-lg font-bold mt-1 ${match.winner === 1 ? 'text-green-600' : 'text-slate-400'}`}>
                      {match.score1}
                    </span>
                  </div>
                  <div className="px-2 text-xs font-medium text-slate-400 flex flex-col items-center">
                    <span className="text-slate-300">vs</span>
                    <span className="mt-2 text-[10px] bg-slate-100 px-2 py-1 rounded-full whitespace-nowrap">{match.time}</span>
                  </div>
                  <div className="flex flex-col items-center flex-1">
                    <img src={match.img2} alt={match.team2} className="w-8 h-8 rounded-full mb-2 border-2 border-white shadow-sm" />
                    <span className={`text-xs font-semibold truncate max-w-[90px] ${match.winner === 2 ? 'text-slate-900' : 'text-slate-500'}`}>
                      {match.team2}
                    </span>
                    <span className={`text-lg font-bold mt-1 ${match.winner === 2 ? 'text-green-600' : 'text-slate-400'}`}>
                      {match.score2}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <Link to="/dashboard/resultados" className="mt-6 block text-center text-sm text-blue-600 font-medium hover:underline">
              Ver todos los resultados
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
