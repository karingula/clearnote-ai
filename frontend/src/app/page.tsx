type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

async function getApiHealth(): Promise<HealthResponse | null> {
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as HealthResponse;
  } catch {
    return null;
  }
}

export default async function Home() {
  const apiHealth = await getApiHealth();
  const apiIsOnline = apiHealth?.status === "healthy";

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-5xl px-6 py-16">
        <header className="mb-12">
          <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">
            Privacy-conscious conversation intelligence
          </p>

          <h1 className="text-4xl font-bold tracking-tight text-slate-950">
            ClearNote AI
          </h1>

          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
            Transform recorded conversations into reviewable transcripts,
            summaries, decisions and structured action items.
          </p>
        </header>

        <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex items-center justify-between gap-6">
            <div>
              <h2 className="text-lg font-semibold text-slate-950">
                System status
              </h2>

              <p className="mt-1 text-sm text-slate-600">
                Connection between the Next.js frontend and FastAPI backend.
              </p>
            </div>

            <div
              className={`rounded-full px-4 py-2 text-sm font-medium ${
                apiIsOnline
                  ? "bg-green-100 text-green-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {apiIsOnline ? "API connected" : "API unavailable"}
            </div>
          </div>

          {apiHealth && (
            <dl className="mt-8 grid gap-6 border-t border-slate-200 pt-6 sm:grid-cols-3">
              <div>
                <dt className="text-sm text-slate-500">Status</dt>
                <dd className="mt-1 font-medium text-slate-950">
                  {apiHealth.status}
                </dd>
              </div>

              <div>
                <dt className="text-sm text-slate-500">Service</dt>
                <dd className="mt-1 font-medium text-slate-950">
                  {apiHealth.service}
                </dd>
              </div>

              <div>
                <dt className="text-sm text-slate-500">Version</dt>
                <dd className="mt-1 font-medium text-slate-950">
                  {apiHealth.version}
                </dd>
              </div>
            </dl>
          )}
        </section>
      </div>
    </main>
  );
}