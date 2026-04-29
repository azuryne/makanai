const BASE = "http://localhost:8000"

async function req(method, path, body, token) {                     // req build headers, attached to JWT (if have), else throe the server returns 4xx/5xx
    const headers = { 'Content-Type': 'application/json'};
    if (token) headers['Authorization'] = `Bearer ${token}`;        // exactly what api/deps.py reads on the backend

    const res = await fetch(BASE + path, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined
    });

    if (!res.ok) {
        // FastAPI errors look like { detail: "..." }
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json()
}

export const api = {
    post: (path, body, token) => req('POST', path, body, token),
    get: (path, token) => req('GET', path, null, token),
};
