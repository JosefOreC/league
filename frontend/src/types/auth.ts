export enum SystemRol {
  ADMIN = "admin",
  COACH = "coach",
  MANAGER = "manager",
  PARTICIPANT = "participant",
  INVITED = "invited",
}

export interface User {
  id: string;
  name: string;
  email: string;
  rol: SystemRol;
}
