/**
 * API client — thin wrappers around fetch.
 * All endpoints live under /api/ which Vite proxies to localhost:8000 in dev
 * and FastAPI serves directly in production.
 */

const BASE = '/api'

async function _post(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json()
}

/** Start a new game. Returns initial game state with first crisis. */
export function startGame(mode) {
  return _post(`${BASE}/game`, { mode })
}

/**
 * Submit the player's decision for the current turn.
 * Classic: { choice_index: 0 }
 * Freeform: { player_input: "..." }
 * Returns consequences + next crisis (or game-over data).
 */
export function resolveGame(gameId, payload) {
  return _post(`${BASE}/game/${gameId}/resolve`, payload)
}

/** Delete a session (optional cleanup). */
export async function deleteGame(gameId) {
  await fetch(`${BASE}/game/${gameId}`, { method: 'DELETE' })
}
