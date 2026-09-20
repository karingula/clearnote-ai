import type { Transcript } from "@/types/api";

type TranscriptViewerProps = {
  transcript: Transcript;
  hasNotes: boolean;
  generating: boolean;
  onGenerateNotes: () => void;
};

export default function TranscriptViewer({
  transcript,
  hasNotes,
  generating,
  onGenerateNotes,
}: TranscriptViewerProps) {
  return (
    <section className="mt-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">
      <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">
            3. Transcript
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Language: {transcript.language ?? "Unknown"}
          </p>
        </div>

        {!hasNotes && (
          <button
            type="button"
            onClick={onGenerateNotes}
            disabled={generating}
            className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {generating
              ? "Generating..."
              : "Generate Notes"}
          </button>
        )}
      </div>

      <div className="mt-6 rounded-xl bg-slate-50 p-5">
        <p className="whitespace-pre-wrap leading-7 text-slate-800">
          {transcript.text}
        </p>
      </div>

      {transcript.segments.length > 0 && (
        <div className="mt-8">
          <h3 className="font-semibold text-slate-900">
            Timestamped segments
          </h3>

          <div className="mt-4 space-y-3">
            {transcript.segments.map((segment) => (
              <div
                key={segment.id}
                className="rounded-lg border border-slate-200 p-4"
              >
                <div className="text-xs font-medium text-slate-500">
                  {formatSeconds(segment.start_seconds)}
                  {" → "}
                  {formatSeconds(segment.end_seconds)}
                </div>

                <p className="mt-2 text-slate-800">
                  {segment.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function formatSeconds(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(
    seconds % 60
  );

  return `${minutes}:${remainingSeconds
    .toString()
    .padStart(2, "0")}`;
}