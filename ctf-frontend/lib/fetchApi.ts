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
                // Agregamos 'no-cache' por defecto para evitar problemas con la caché
                // en peticiones que no sean GET, aunque se puede personalizar.
                cache: method === 'GET' ? 'default' : 'no-cache', 
            };

            // 1. Manejo unificado del cuerpo para POST, PUT, PATCH, DELETE.
            if (hasBody) {
                // Métodos que generalmente soportan cuerpo
                if (method === 'POST' || method === 'PUT' || method === 'PATCH' || (method === 'DELETE' && !isFormData)) {
                    if (isFormData) {
                        // Para FormData, no se establece 'Content-Type', el navegador lo hace.
                        options.body = bodyData as BodyInit; 
                    } else {
                        // Para JSON, establecer el Content-Type y serializar el cuerpo.
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
                
                // Intento leer el cuerpo del error como JSON
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
                    // Si no es JSON, capturar parte del texto
                    const errorText = await response.text();
                    errorDetails.details.push(errorText.substring(0, 100) + (errorText.length > 100 ? '...' : ''));
                }
                
                // Lanzar un objeto de error más estructurado.
                throw errorDetails; 
            }
            
            // 2. Manejo de Respuestas de Éxito
            
            // Si el status es 204 (No Content) o no hay Content-Type, asumir éxito sin cuerpo.
            if (response.status === 204 || (!contentType && response.status >= 200 && response.status < 300)) {
                 // Devolvemos undefined para respetar T=void/undefined.
                return undefined as unknown as T; 
            }

            // Si es JSON, parsear y devolver
            if (contentType && contentType.includes('application/json')) {
                return (await response.json()) as T;
            }
            
            // Si no es JSON y la función esperaba un tipo (T no es void/unknown), podríamos considerarlo un error,
            // pero por simplicidad, lo tratamos como un éxito sin cuerpo, a menos que se espere un tipo específico (como un string).
            // Si T fuera esperado como string, usaríamos response.text(). Por defecto, devolvemos undefined/void.
            if (response.text) {
                // Intentamos devolver el texto si se esperaba un string, pero el tipo T puede ser complejo.
                // Lo más seguro es devolver un error o undefined para forzar a que las peticiones que
                // devuelven JSON se configuren como tal.
                if (typeof response.text === 'function') {
                    // Si el usuario espera T=string, podría fallar aquí. Dejamos undefined por defecto.
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