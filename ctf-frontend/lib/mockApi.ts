import { Dependency, Deployment } from './types';

// --- MOCK API SERVICE ---

// Mock data for available dependencies (challenges)
export const MOCK_DEPENDENCIES: Dependency[] = [
    { name: 'challenge-web-basic-1', version: '1.0.0', description: '2024-05-01' },
    { name: 'challenge-network-hard', version: '2.1.0', description: '2024-05-15' },
    { name: 'challenge-crypto-intro', version: '1.2.3', description: '2024-06-10' },
];

// Mock data for active deployments
export let MOCK_DEPLOYMENTS: Deployment[] = [];

/**
 * Utility function to simulate an API call.
 * This function simulates network latency and handles mock responses
 * for fetching dependencies and deploying/uploading challenges.
 */
export const mockFetch = <T, U>(endpoint: string, method: 'GET' | 'POST', data?: U): Promise<T> => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (endpoint.includes('/api/dependencies')) {
                if (method === 'GET') {
                    resolve(MOCK_DEPENDENCIES as unknown as T);
                } 
                else if (method === 'POST' && data && typeof data === 'object' && data !== null && 'challengeFile' in data) {
                    const file = (data as unknown as { challengeFile: File }).challengeFile;
                    const challengeName = file.name.replace(/\.tar(\.gz)?$/, '');
                    
                    if (file.name.includes('error')) {
                        reject({ status: 500, error: 'Mocked error during file upload.' });
                    } else if (!MOCK_DEPENDENCIES.some(d => d.name === challengeName)) {
                        MOCK_DEPENDENCIES.push({ 
                            name: challengeName, 
                            version: '1.0.0', 
                            description: new Date().toISOString().split('T')[0] 
                        });
                        resolve({ message: `File '${challengeName}' successfully uploaded and processed.` } as unknown as T);
                    } else {
                        resolve({ message: `File '${challengeName}' successfully updated.` } as unknown as T);
                    }
                }
            } 
            else if (endpoint.includes('/api/deployment') && 
                     method === 'POST' && 
                     data && 
                     typeof data === 'object' && 
                     data !== null && 
                     'user_name' in data && 
                     'challenge_name' in data) {
                
                const deployData = data as { user_name: string, challenge_name: string };
                
                const newDeployment: Deployment = {
                    release_name: `${deployData.user_name}-${deployData.challenge_name}`,
                    status: 'deployed',
                    chart: deployData.challenge_name,
                };
                MOCK_DEPLOYMENTS.push(newDeployment);
                
                resolve({ 
                    message: `Deployment of '${deployData.challenge_name}' successful for user '${deployData.user_name}'.`,
                    release_name: newDeployment.release_name,
                    helm_output: ["Helm mock output..."] 
                } as unknown as T);
            } 
            else if (endpoint.includes('/api/deployment') && method === 'GET') {
                resolve(MOCK_DEPLOYMENTS as unknown as T);
            }
            
            reject({ status: 404, error: 'Endpoint not mocked.' });
        }, 800);
    });
};