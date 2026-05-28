import { useAuth } from "../context/AuthContext";
import { SystemRol } from "../types/auth";
import { Tournament } from "../types/tournament";

/**
 * Centralizes ALL role-based permission logic in one place.
 * Use this hook in any component that needs to show/hide actions based on the user's role.
 */
export function useRoleGuard(tournament?: Tournament | null) {
  const { user } = useAuth();

  const role = user?.rol;
  const userId = user?.id || user?.user_id;

  // ── System-level checks ────────────────────────────────────────────────────
  const isAdmin = role === SystemRol.ADMIN;
  const isManager = role === SystemRol.ORGANIZADOR;
  const isParticipant = role === SystemRol.PARTICIPANTE;
  const isManagerOrAdmin = isAdmin || isManager;

  // ── Tournament-level checks ────────────────────────────────────────────────
  // A user "owns" a tournament if they created it (creator_user_id matches)
  const isCreator = !!tournament && !!userId && tournament.creator_user_id === userId;

  // A user can EDIT a tournament if:
  // - They are ADMIN AND are the creator of that tournament, OR
  // - They are MANAGER AND are the creator of that tournament
  // (In this system, the creator automatically gets TournamentRole.Manager)
  const canEditTournament = isManagerOrAdmin && isCreator;

  // A user can VIEW a tournament depending on role:
  // - ADMIN: always
  // - MANAGER: only their own
  // - PARTICIPANT: only REGISTRATION_OPEN
  const canViewTournament = (t: Tournament) => {
    if (isAdmin) return true;
    if (isManager) return t.creator_user_id === userId;
    return false; // Participants see only filtered lists
  };

  // Can manage inscriptions (approve/reject teams)
  const canManageTeams = canEditTournament;

  // Can register a team (only participants)
  const canRegisterTeam = isParticipant;

  // Can create a new tournament
  const canCreateTournament = isManagerOrAdmin;

  // Can configure tournament rules
  const canConfigureRules = canEditTournament;

  // Can manage match results
  const canRegisterResults = canEditTournament;

  return {
    user,
    role,
    userId,
    isAdmin,
    isManager,
    isParticipant,
    isManagerOrAdmin,
    isCreator,
    canEditTournament,
    canViewTournament,
    canManageTeams,
    canRegisterTeam,
    canCreateTournament,
    canConfigureRules,
    canRegisterResults,
  };
}
