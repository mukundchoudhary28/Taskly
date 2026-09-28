import type { HealthState } from "../hooks/useHealthCheck";

interface HealthStatusProps {
  state: HealthState;
}

export function HealthStatus({ state }: HealthStatusProps) {
  switch (state.kind) {
    case "loading":
      return (
        <div role="status" aria-live="polite">
          <p>Checking API health…</p>
        </div>
      );
    case "healthy":
      return (
        <div role="status" aria-live="polite">
          <p style={{ color: "var(--color-healthy)" }}>
            API: healthy (database connected)
          </p>
          <p>
            <small>Last checked: {state.data.timestamp}</small>
          </p>
        </div>
      );
    case "degraded":
      return (
        <div role="status" aria-live="polite">
          <p style={{ color: "var(--color-degraded)" }}>
            API: degraded (database unreachable)
          </p>
          <p>
            <small>Last checked: {state.data.timestamp}</small>
          </p>
        </div>
      );
    case "error":
      return (
        <div role="alert">
          <p style={{ color: "var(--color-error)" }}>
            API: unreachable ({state.message})
          </p>
        </div>
      );
  }
}
