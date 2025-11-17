import React from 'react';
import { RefreshCw, Loader2, List, AlertTriangle } from 'lucide-react';
import DeploymentItem from '../components/DeploymentItem';
import type { Deployment } from '@/lib/types';

interface DeployedSectionProps {
    isLoading: boolean;
    deployments: Deployment[];
    fetchData: () => Promise<void>;
}

/**
 * Component to list all the active Helm releases.
 */
const DeployedSection: React.FC<DeployedSectionProps> = ({ isLoading, deployments, fetchData }) => {
    
    const activeDeployments = deployments.filter((d: Deployment) => d.status !== 'failed' && d.status !== 'error');
    const failedDeployments = deployments.filter((d: Deployment) => d.status === 'failed' || d.status === 'error');

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center border-b pb-2">
                <h3 className="text-xl font-bold text-gray-800">
                    Active Deployments ({activeDeployments.length})
                </h3>
                <button 
                    onClick={fetchData} 
                    disabled={isLoading}
                    className="flex items-center text-sm px-3 py-1 bg-gray-200 rounded-lg hover:bg-gray-300 transition disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} /> 
                    Refresh
                </button>
            </div>
            
            {isLoading && (
                 <div className="p-8 text-center text-gray-500">
                    <Loader2 className="w-8 h-8 mx-auto animate-spin" />
                    <p className="mt-3">Fetching deployment statuses...</p>
                </div>
            )}

            {!isLoading && activeDeployments.length === 0 && (
                 <div className="p-6 text-center text-gray-500 border border-dashed rounded-xl">
                    <List className="w-6 h-6 mx-auto mb-2" />
                    <p className="text-sm">No active challenges running for your user.</p>
                </div>
            )}
            
            <div className="space-y-3">
                {activeDeployments.map(d => <DeploymentItem key={d.release_name} deployment={d} fetchData={fetchData} />)}
            </div>
            
            {failedDeployments.length > 0 && (
                <div className="pt-4 border-t border-red-200">
                    <h4 className="text-lg font-semibold text-red-700 flex items-center mb-3">
                        <AlertTriangle className="w-5 h-5 mr-2" /> Failed Deployments ({failedDeployments.length})
                    </h4>
                    <div className="space-y-3">
                        {failedDeployments.map(d => <DeploymentItem key={d.release_name} deployment={d} fetchData={fetchData} />)}
                    </div>
                </div>
            )}
        </div>
    );
};

export default DeployedSection;