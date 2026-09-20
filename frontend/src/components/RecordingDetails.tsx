import type { Recording } from "@/types/api";

type RecordingDetailsProps = {
  recording: Recording;
  hasTranscript: boolean;
  transcribing: boolean;
  onTranscribe: () => void;
};

export default function RecordingDetails({
  recording,
  hasTranscript,
  transcribing,
  onTranscribe,
}: RecordingDetailsProps) {
  return (
    <section className="mt-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">
      <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">
            2. Recording
          </h2>

          <p className="mt-2 text-sm text-slate-600">
            {recording.original_filename}
          </p>

          <p className="mt-1 text-sm text-slate-500">
            Status: {recording.status}
          </p>
        </div>

        {!hasTranscript && (
          <button
            type="button"
            onClick={onTranscribe}
            disabled={transcribing}
            className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {transcribing
              ? "Transcribing..."
              : "Transcribe"}
          </button>
        )}
      </div>
    </section>
  );
}