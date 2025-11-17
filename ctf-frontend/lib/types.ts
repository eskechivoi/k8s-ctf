export interface Dependency {
    name: string;
    version: string;
    description: string;
}

export type DeploymentStatus = 'deployed' | 'pending-upgrade' | 'failed' | 'error';

export type Deployment = {
    release_name: string;
    chart: string;
    status: DeploymentStatus;
    service_url?: string;
}

export type Message = {
    type: 'success' | 'error' | 'info';
    text: string;
    details?: string[];
} | null;