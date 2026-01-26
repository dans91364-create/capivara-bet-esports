"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import PlayerProps from "@/components/PlayerProps";
import { searchPlayers, getPlayerProps, Player, PlayerProps as PlayerPropsType } from "@/lib/api";

export default function PropsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerPropsType | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const results = await searchPlayers(searchQuery);
      setSearchResults(results);
    } catch (error) {
      console.error("Error searching players:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlayer = async (player: Player) => {
    try {
      setLoading(true);
      const props = await getPlayerProps(player.player_id);
      setSelectedPlayer(props);
    } catch (error) {
      console.error("Error fetching player props:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Player Props</h1>
        <p className="text-slate-400">Análise de props de jogadores</p>
      </div>

      {/* Search */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Buscar Jogador</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Digite o nome do jogador..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? "Buscando..." : "Buscar"}
            </Button>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-4 space-y-2">
              {searchResults.map((player) => (
                <div
                  key={player.player_id}
                  onClick={() => handleSelectPlayer(player)}
                  className="p-3 bg-slate-700 rounded-md hover:bg-slate-600 cursor-pointer transition-colors"
                >
                  <div className="font-medium text-white">{player.player_name}</div>
                  <div className="text-sm text-slate-400">
                    {player.team} - {player.sport?.toUpperCase()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Player Props */}
      {selectedPlayer && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{selectedPlayer.player_name}</CardTitle>
              <p className="text-slate-400">{selectedPlayer.team}</p>
            </CardHeader>
            <CardContent>
              <PlayerProps props={selectedPlayer.props} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Últimos Jogos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {selectedPlayer.recent_games.map((game, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-slate-700 rounded-md flex justify-between items-center"
                  >
                    <div>
                      <div className="font-medium text-white">
                        {game.is_home ? "vs" : "@"} {game.opponent}
                      </div>
                      <div className="text-sm text-slate-400">{game.game_date}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-white">
                        {game.points}pts / {game.rebounds_total}reb / {game.assists}ast
                      </div>
                      <div className="text-sm text-slate-400">{game.minutes} min</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
