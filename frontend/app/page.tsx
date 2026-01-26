"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import GameCard from "@/components/GameCard";
import { getGames, getLiveGames, Game } from "@/lib/api";

export default function Home() {
  const [todayGames, setTodayGames] = useState<Game[]>([]);
  const [liveGames, setLiveGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch today's games
        const today = new Date().toISOString().split("T")[0];
        const games = await getGames({ date: today });
        setTodayGames(games);

        // Fetch live games
        const live = await getLiveGames();
        setLiveGames(live);
      } catch (error) {
        console.error("Error fetching games:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">
          Bem-vindo ao Capivara Bet - Sistema de análise de apostas em esports
        </p>
      </div>

      {/* Live Games Section */}
      {liveGames.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-2xl font-bold text-white">Jogos ao Vivo</h2>
            <Badge variant="destructive" className="animate-pulse">
              {liveGames.length} LIVE
            </Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {liveGames.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-400">
              Jogos Hoje
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {todayGames.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-400">
              Jogos ao Vivo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-500">
              {liveGames.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-400">
              Próximas Partidas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-500">
              {todayGames.filter((g) => !g.finished && !g.is_live).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Today's Games */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Jogos de Hoje</h2>
        {loading ? (
          <div className="text-center text-slate-400 py-8">Carregando...</div>
        ) : todayGames.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-slate-400">
              Nenhum jogo agendado para hoje
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {todayGames.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
