const API_BASE = import.meta.env.VITE_API_BASE || "/api/v1";
const INSTRUCTOR_TOKEN_KEY = "korkyt-instructor-token";

function buildErrorMessage(path: string, status: number, text: string, contentType: string): string {
  if (contentType.includes("application/json")) {
    try {
      const payload = JSON.parse(text) as { detail?: string };
      if (payload.detail) {
        return payload.detail;
      }
    } catch {
      return text || `Request failed with status ${status}`;
    }
  }

  if (contentType.includes("text/html")) {
    return `API returned HTML instead of JSON for ${path}. Check nginx/Vite proxy and API URL.`;
  }

  return text || `Request failed with status ${status}`;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";
  const text = await response.text();

  if (!response.ok) {
    throw new Error(buildErrorMessage(path, response.status, text, contentType));
  }

  if (response.status === 204 || text.length === 0) {
    return undefined as T;
  }

  if (!contentType.includes("application/json")) {
    throw new Error(`Expected JSON from ${path}, got ${contentType || "unknown content type"}.`);
  }

  return JSON.parse(text) as T;
}

export function getInstructorToken(): string | null {
  return localStorage.getItem(INSTRUCTOR_TOKEN_KEY);
}

export function setInstructorToken(token: string): void {
  localStorage.setItem(INSTRUCTOR_TOKEN_KEY, token);
}

export function clearInstructorToken(): void {
  localStorage.removeItem(INSTRUCTOR_TOKEN_KEY);
}

export async function instructorApiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getInstructorToken();
  const headers = new Headers(init.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return apiFetch<T>(path, {
    ...init,
    headers,
  });
}
