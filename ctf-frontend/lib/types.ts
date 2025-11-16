export interface Dependency {
    name: string;
    version: string;
    lastUpdated: string;
}

export interface Deployment {
    release_name: string;
    status: 'deployed' | 'pending-upgrade' | 'error';
    chart: string;
}

export type Message = {
    type: 'success' | 'error' | 'info';
    text: string;
    details?: string[];
} | null;