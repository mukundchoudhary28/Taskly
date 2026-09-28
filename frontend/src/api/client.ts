const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiFetch<T>(path: string): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new ApiError("API is unreachable");
  }

  if (response.ok || response.status === 503) {
    try {
      return (await response.json()) as T;
    } catch {
      throw new ApiError("Invalid response from API");
    }
  }

  throw new ApiError(`Unexpected status: ${response.status}`, response.status);
}
