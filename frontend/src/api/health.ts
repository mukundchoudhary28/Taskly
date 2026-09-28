import { apiFetch } from "./client";
import type { HealthCheckResponse } from "./types";

export function getHealth(): Promise<HealthCheckResponse> {
  return apiFetch<HealthCheckResponse>("/health");
}
