export interface AdminStats {
  totalClients: number;
  activeClients: number;
  highCpuClients: number;
  highMemoryClients: number;
}

export interface ClientAction {
  type: 'delete' | 'edit';
  clientId: string;
} 