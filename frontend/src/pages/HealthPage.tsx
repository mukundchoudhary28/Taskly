import { HealthStatus } from "../components/HealthStatus";
import { useHealthCheck } from "../hooks/useHealthCheck";

export function HealthPage() {
  const state = useHealthCheck();

  return (
    <main>
      <h1>Taskly</h1>
      <HealthStatus state={state} />
    </main>
  );
}
