"use client";

import { useEffect, useState } from "react";

type Health = {
  status: string;
  tasks: Record<string, string>;
  missing_api_keys: string[];
};

export default function Home() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then(setHealth)
      .catch((err) => setError(String(err)));
  }, []);

  return (
    <main className="mx-auto max-w-2xl p-8 font-mono">
      <h1 className="mb-6 text-2xl font-bold">Research Hub</h1>

      {error && (
        <p className="text-red-600">
          Backend unreachable: {error} — is the API running on :8000?
        </p>
      )}

      {!error && !health && <p>Checking backend…</p>}

      {health && (
        <div className="space-y-4">
          <p>
            Backend status:{" "}
            <span className="font-bold text-green-600">{health.status}</span>
          </p>

          <div>
            <h2 className="mb-1 font-bold">LLM task routing</h2>
            <ul className="list-inside list-disc text-sm">
              {Object.entries(health.tasks).map(([task, model]) => (
                <li key={task}>
                  {task} → {model}
                </li>
              ))}
            </ul>
          </div>

          {health.missing_api_keys.length > 0 && (
            <p className="text-sm text-amber-600">
              Missing API keys: {health.missing_api_keys.join(", ")} (set them
              in .env)
            </p>
          )}
        </div>
      )}
    </main>
  );
}
