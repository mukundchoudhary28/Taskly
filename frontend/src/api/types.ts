export interface HealthCheckResponse {
  status: "healthy" | "degraded";
  checks: {
    api: "ok";
    database: "ok" | "unreachable";
  };
  message: string;
  timestamp: string;
}
