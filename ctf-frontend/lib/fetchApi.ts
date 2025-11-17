const MAX_RETRIES = 3;

/**
 * Utility function to do API calls with exponential retries.
 *
 * @template T Expected type of response (or void/undefined for no content).
 * @template U Request body type (JSON object or FormData).
 * @param {string} endpoint API endpoint
 * @param {'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'} method HTTP method
 * @param {U} [bodyData] Request body (JS object, FormData, or null).
 * @returns {Promise<T>}
 */
export const fetchApi = async <T = void, U = unknown>(
    endpoint: string, 
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE', 
    bodyData?: U
): Promise<T> => {
    let lastError: any = null;

    for (let i = 0; i < MAX_RETRIES; i++) {
        try {
            const isFormData = bodyData instanceof FormData;
            const hasBody = !!bodyData;

            const options: RequestInit = {
                method,
                cache: method === 'GET' ? 'default' : 'no-cache', 
            };

            if (hasBody) {
                if (method === 'POST' || method === 'PUT' || method === 'PATCH' || (method === 'DELETE' && !isFormData)) {
                    if (isFormData) {
                        options.body = bodyData as BodyInit; 
                    } else {
                        options.headers = { 'Content-Type': 'application/json' };
                        options.body = JSON.stringify(bodyData);
                    }
                }
            }

            const response = await fetch(endpoint, options);
            const contentType = response.headers.get('content-type');

            if (!response.ok) {
                let errorDetails: { error: string, details: string[] } = { 
                    error: `HTTP Error: ${response.status} ${response.statusText}`, 
                    details: [] 
                };
                
                if (contentType && contentType.includes('application/json')) {
                    try {
                        const errorJson = await response.json();
                        errorDetails.error = errorJson.error || errorDetails.error;
                        if (errorJson.message) errorDetails.details.push(String(errorJson.message));
                        if (errorJson.details) errorDetails.details.push(String(errorJson.details));
                    } catch (e) {
                        errorDetails.details.push('Could not parse error response as JSON.');
                    }
                } else {
                    const errorText = await response.text();
                    errorDetails.details.push(errorText.substring(0, 100) + (errorText.length > 100 ? '...' : ''));
                }
                throw errorDetails; 
            }
            
            if (response.status === 204 || (!contentType && response.status >= 200 && response.status < 300)) {
                return undefined as unknown as T; 
            }

            if (contentType && contentType.includes('application/json')) {
                return (await response.json()) as T;
            }
            
            if (response.text) {
                if (typeof response.text === 'function') {
                    return undefined as unknown as T;
                }
            }


        } catch (error) {
            lastError = error;
            const delay = Math.pow(2, i) * 1000 + Math.random() * 500;
            
            if (i < MAX_RETRIES - 1) {
                console.warn(`Fetch failed for ${endpoint} (Attempt ${i + 1}/${MAX_RETRIES}). Retrying in ${delay.toFixed(0)}ms.`, error);
                await new Promise(resolve => setTimeout(resolve, delay));
            } else {
                console.error(`Fetch failed after ${MAX_RETRIES} attempts for ${endpoint}.`, lastError);
                throw lastError;
            }
        }
    }
    throw lastError;
};