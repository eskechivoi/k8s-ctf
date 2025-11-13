import React from 'react';
import StatusBadge from './StatusBadge';
import type { Deployment } from '@/lib/types';

interface DeploymentItemProps {
    deployment: Deployment;
}

/**
 * Shows an individual element from the list of active deployments.
 */
const DeploymentItem: React.FC<DeploymentItemProps> = ({ deployment }) => (
    <div className="flex justify-between items-center p-3 bg-white shadow-sm rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
        <div>
            <p className="font-semibold text-gray-800">{deployment.release_name}</p>
            <p className="text-sm text-gray-500">Chart: {deployment.chart}</p>
        </div>
        <StatusBadge status={deployment.status} />
    </div>
);

export default DeploymentItem;