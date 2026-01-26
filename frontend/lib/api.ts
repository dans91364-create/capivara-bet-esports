/**
 * API client for Capivara Bet backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with error handling.
 */
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API fetch error:", error);
    throw error;
  }
}

/**
 * Game types
 */
export interface Game {
  id: number;
  game: string;
  team1: string;
  team2: string;
  start_time: string;
  tournament?: string;
  best_of: number;
  winner?: string;
  team1_score?: number;
  team2_score?: number;
  finished: boolean;
  is_live: boolean;
  odds?: Odds[];
}

export interface Odds {
  bookmaker: string;
  team1_odds?: number;
  team2_odds?: number;
  timestamp: string;
}

/**
 * Player types
 */
export interface Player {
  player_id: string;
  player_name: string;
  team?: string;
  sport?: string;
}

export interface PlayerGameLog {
  game_id: string;
  game_date: string;
  opponent: string;
  is_home: boolean;
  minutes?: number;
  points?: number;
  rebounds_total?: number;
  assists?: number;
  steals?: number;
  blocks?: number;
}

export interface PlayerPropAnalysis {
  prop_type: string;
  line: number;
  average: number;
  over_rate: number;
  under_rate: number;
  last_5_avg?: number;
  last_10_avg?: number;
  home_avg?: number;
  away_avg?: number;
}

export interface PlayerProps {
  player_id: string;
  player_name: string;
  team: string;
  props: PlayerPropAnalysis[];
  recent_games: PlayerGameLog[];
}

/**
 * Fetch games by date and filters.
 */
export async function getGames(params?: {
  date?: string;
  league?: string;
  game?: string;
}): Promise<Game[]> {
  const searchParams = new URLSearchParams();
  if (params?.date) searchParams.set("date", params.date);
  if (params?.league) searchParams.set("league", params.league);
  if (params?.game) searchParams.set("game", params.game);

  const query = searchParams.toString();
  return fetchAPI<Game[]>(`/api/games${query ? `?${query}` : ""}`);
}

/**
 * Fetch live games.
 */
export async function getLiveGames(game?: string): Promise<Game[]> {
  const searchParams = new URLSearchParams();
  if (game) searchParams.set("game", game);

  const query = searchParams.toString();
  return fetchAPI<Game[]>(`/api/games/live${query ? `?${query}` : ""}`);
}

/**
 * Fetch game by ID.
 */
export async function getGameById(gameId: number): Promise<Game> {
  return fetchAPI<Game>(`/api/games/${gameId}`);
}

/**
 * Search players.
 */
export async function searchPlayers(
  query: string,
  sport: string = "nba"
): Promise<Player[]> {
  const searchParams = new URLSearchParams({ q: query, sport });
  return fetchAPI<Player[]>(`/api/players/search?${searchParams.toString()}`);
}

/**
 * Fetch player game log.
 */
export async function getPlayerGameLog(
  playerId: string,
  limit: number = 10
): Promise<PlayerGameLog[]> {
  const searchParams = new URLSearchParams({ limit: limit.toString() });
  return fetchAPI<PlayerGameLog[]>(
    `/api/players/${playerId}/gamelog?${searchParams.toString()}`
  );
}

/**
 * Fetch player props.
 */
export async function getPlayerProps(playerId: string): Promise<PlayerProps> {
  return fetchAPI<PlayerProps>(`/api/props/${playerId}`);
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{
  status: string;
  timestamp: string;
  database: string;
  version: string;
}> {
  return fetchAPI("/api/health");
}
