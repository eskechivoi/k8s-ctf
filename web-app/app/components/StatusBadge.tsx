import React from 'react';
import type { Deployment } from '@/lib/types';

/**
 * Shows the state of the deployment with colors.
 */
const StatusBadge: React.FC<{ status: Deployment['status'] }> = ({ status }) => {
    const statusClasses = {
        'deployed': 'bg-green-100 text-green-800',
        'pending-upgrade': 'bg-yellow-100 text-yellow-800',
        'error': 'bg-red-100 text-red-800',
    };
    return (
        <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${statusClasses[status]}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

export default StatusBadge;