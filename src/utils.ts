export async function httpGet<T>(host: string, path: string, headers: { [header: string]: string } = {}): Promise<T> {
    const url = host + path;
    console.log("Making request to:", url);
    
    const response = await fetch(url, {
        method: 'GET',
        headers,
    });

    if (!response.ok) {
        console.error("HTTP Error:", response.status, response.statusText);
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const text = await response.text();

    try {
        const data = JSON.parse(text);
        return data as T;
    } catch (error) {
        console.error("JSON Parse Error:", error);
        console.error("Response text:", text);
        throw error;
    }
}