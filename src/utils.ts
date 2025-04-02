export async function httpGet<T>(host: string, path: string, headers: { [header: string]: string } = {}): Promise<T> {
    const response = await fetch(host + path, {
        method: 'GET',
        headers,
    });
    const data = await response.json();
    return data as T
}