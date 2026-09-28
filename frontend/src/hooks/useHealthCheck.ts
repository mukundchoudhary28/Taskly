import { useEffect, useState } from "react";
import { getHealth } from "../api/health";
import type { HealthCheckResponse } from "../api/types";

export type HealthState =
  | { kind: "loading" }
  | { kind: "healthy"; data: HealthCheckResponse }
  | { kind: "degraded"; data: HealthCheckResponse }
  | { kind: "error"; message: string };

export function useHealthCheck(): HealthState {
  const [state, setState] = useState<HealthState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const data = await getHealth();
        if (cancelled) return;
        if (data.status === "healthy") {
          setState({ kind: "healthy", data });
        } else {
          setState({ kind: "degraded", data });
        }
      } catch (err) {
        if (cancelled) return;
        setState({
          kind: "error",
          message: err instanceof Error ? err.message : "Unknown error",
        });
      }
    }

    check();

    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
