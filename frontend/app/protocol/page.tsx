"use client";

import { useCallback, useEffect, useState } from "react";

type Cluster = { name: string; keywords: string[] };
type Protocol = {
  research_questions: string[];
  keyword_clusters: Cluster[];
  queries: string[];
};
type ProtocolResp = {
  protocol: Protocol | null;
  version_count: number;
  has_proposal: boolean;
  proposal_chars: number;
};

export default function ProtocolPage() {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [info, setInfo] = useState<ProtocolResp | null>(null);
  const [protocol, setProtocol] = useState<Protocol | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async (pid: number) => {
    const resp: ProtocolResp = await fetch(`/api/projects/${pid}/protocol`).then(
      (r) => r.json(),
    );
    setInfo(resp);
    setProtocol(resp.protocol);
  }, []);

  useEffect(() => {
    fetch("/api/projects")
      .then((r) => r.json())
      .then((projects) => {
        if (projects.length > 0) {
          setProjectId(projects[0].id);
          load(projects[0].id);
        } else {
          setMessage("No project found — run the seed script first.");
        }
      })
      .catch(() => setMessage("Backend unreachable — is the API running?"));
  }, [load]);

  async function uploadProposal(file: File) {
    if (!projectId) return;
    setBusy("Uploading proposal…");
    const form = new FormData();
    form.append("file", file);
    const resp = await fetch(`/api/projects/${projectId}/proposal`, {
      method: "POST",
      body: form,
    });
    setBusy(null);
    if (!resp.ok) {
      setMessage(`Upload failed: ${(await resp.json()).detail}`);
      return;
    }
    setMessage("Proposal uploaded.");
    await load(projectId);
  }

  async function generate() {
    if (!projectId) return;
    setBusy("Generating protocol from proposal (LLM)…");
    const resp = await fetch(`/api/projects/${projectId}/protocol/generate`, {
      method: "POST",
    });
    setBusy(null);
    if (!resp.ok) {
      setMessage(`Generation failed: ${(await resp.json()).detail}`);
      return;
    }
    setMessage("Protocol generated — review and edit below, then save.");
    await load(projectId);
  }

  async function save() {
    if (!projectId || !protocol) return;
    setBusy("Saving…");
    const resp = await fetch(`/api/projects/${projectId}/protocol`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ protocol }),
    });
    setBusy(null);
    if (!resp.ok) {
      setMessage(`Save failed: ${(await resp.json()).detail}`);
      return;
    }
    setMessage("Saved as a new version.");
    await load(projectId);
  }

  const setLines = (lines: string) => lines.split("\n");
  const trimmed = (xs: string[]) => xs.map((x) => x.trim()).filter(Boolean);

  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="mb-1 text-2xl font-bold">Review Protocol</h1>
      <p className="mb-6 text-sm text-zinc-500">
        {info
          ? `Proposal: ${info.has_proposal ? `${info.proposal_chars.toLocaleString()} chars` : "not uploaded"} · Versions: ${info.version_count}`
          : "Loading…"}
      </p>

      {message && <p className="mb-4 text-sm text-blue-600">{message}</p>}
      {busy && <p className="mb-4 animate-pulse text-sm text-amber-600">{busy}</p>}

      <div className="mb-8 flex items-center gap-4">
        <label className="cursor-pointer rounded border px-3 py-2 text-sm hover:bg-zinc-50">
          Upload proposal (.pdf/.txt)
          <input
            type="file"
            accept=".pdf,.txt,.md"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && uploadProposal(e.target.files[0])}
          />
        </label>
        <button
          onClick={generate}
          disabled={!info?.has_proposal || !!busy}
          className="rounded bg-black px-3 py-2 text-sm text-white disabled:opacity-40"
        >
          {protocol ? "Regenerate from proposal" : "Generate protocol"}
        </button>
        {protocol && (
          <button
            onClick={save}
            disabled={!!busy}
            className="rounded bg-green-700 px-3 py-2 text-sm text-white disabled:opacity-40"
          >
            Save (new version)
          </button>
        )}
      </div>

      {protocol && (
        <div className="space-y-8">
          <section>
            <h2 className="mb-2 font-bold">Research questions (one per line)</h2>
            <textarea
              className="h-40 w-full rounded border p-2 font-mono text-sm"
              value={protocol.research_questions.join("\n")}
              onChange={(e) =>
                setProtocol({
                  ...protocol,
                  research_questions: setLines(e.target.value),
                })
              }
              onBlur={() =>
                setProtocol({
                  ...protocol,
                  research_questions: trimmed(protocol.research_questions),
                })
              }
            />
          </section>

          <section>
            <h2 className="mb-2 font-bold">Keyword clusters</h2>
            {protocol.keyword_clusters.map((cluster, i) => (
              <div key={i} className="mb-3 rounded border p-3">
                <div className="mb-2 flex items-center gap-2">
                  <input
                    className="w-full rounded border p-1 text-sm font-semibold"
                    value={cluster.name}
                    onChange={(e) => {
                      const clusters = [...protocol.keyword_clusters];
                      clusters[i] = { ...cluster, name: e.target.value };
                      setProtocol({ ...protocol, keyword_clusters: clusters });
                    }}
                  />
                  <button
                    className="text-sm text-red-500"
                    onClick={() =>
                      setProtocol({
                        ...protocol,
                        keyword_clusters: protocol.keyword_clusters.filter(
                          (_, j) => j !== i,
                        ),
                      })
                    }
                  >
                    remove
                  </button>
                </div>
                <input
                  className="w-full rounded border p-1 font-mono text-sm"
                  value={cluster.keywords.join(", ")}
                  onChange={(e) => {
                    const clusters = [...protocol.keyword_clusters];
                    clusters[i] = {
                      ...cluster,
                      keywords: e.target.value.split(","),
                    };
                    setProtocol({ ...protocol, keyword_clusters: clusters });
                  }}
                  onBlur={() => {
                    const clusters = [...protocol.keyword_clusters];
                    clusters[i] = { ...cluster, keywords: trimmed(cluster.keywords) };
                    setProtocol({ ...protocol, keyword_clusters: clusters });
                  }}
                />
              </div>
            ))}
            <button
              className="rounded border px-3 py-1 text-sm hover:bg-zinc-50"
              onClick={() =>
                setProtocol({
                  ...protocol,
                  keyword_clusters: [
                    ...protocol.keyword_clusters,
                    { name: "new cluster", keywords: [] },
                  ],
                })
              }
            >
              + add cluster
            </button>
          </section>

          <section>
            <h2 className="mb-2 font-bold">Search queries (one per line)</h2>
            <textarea
              className="h-48 w-full rounded border p-2 font-mono text-sm"
              value={protocol.queries.join("\n")}
              onChange={(e) =>
                setProtocol({ ...protocol, queries: setLines(e.target.value) })
              }
              onBlur={() =>
                setProtocol({ ...protocol, queries: trimmed(protocol.queries) })
              }
            />
          </section>
        </div>
      )}
    </main>
  );
}
