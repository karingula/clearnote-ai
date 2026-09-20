import type { Recording } from "@/types/api";

type RecordingCardProps = {
  recording: Recording;
  isSelected: boolean;
  onSelect: (recording: Recording) => void;
};

export default function RecordingCard({
  recording,
  isSelected,
  onSelect,
}: RecordingCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(recording)}
      className={`group w-full rounded-2xl border p-5 text-left transition ${
        isSelected
          ? "border-indigo-300 bg-indigo-50 shadow-sm"
          : "border-slate-200 bg-white hover:border-indigo-200 hover:bg-indigo-50/40 hover:shadow-sm"
      }`}
    >
      <div className="flex items-start justify-between gap-6">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-100 text-xl">
              🎙️
            </div>

            <div className="min-w-0">
              <p className="truncate font-semibold text-slate-900">
                {recording.original_filename}
              </p>

              <p className="mt-1 text-sm text-slate-500">
                {formatCreatedAt(recording.created_at)}
              </p>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <RecordingStatusBadge status={recording.status} />

            <span className="text-sm text-slate-500">
              {getRecordingNextAction(recording.status)}
            </span>
          </div>
        </div>

        <div className="pt-2 text-xl text-slate-400 transition group-hover:translate-x-1 group-hover:text-indigo-600">
          →
        </div>
      </div>
    </button>
  );
}

function formatCreatedAt(value: string): string {
  return new Date(value).toLocaleString();
}

function RecordingStatusBadge({
  status,
}: {
  status: Recording["status"];
}) {
  const styles = {
    uploaded: "bg-slate-100 text-slate-700",
    transcribing: "bg-indigo-50 text-indigo-700",
    transcribed: "bg-emerald-50 text-emerald-700",
    failed: "bg-red-50 text-red-700",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${styles[status]}`}
    >
      {status}
    </span>
  );
}

function getRecordingNextAction(
  status: Recording["status"]
): string {
  switch (status) {
    case "uploaded":
      return "Ready to transcribe";

    case "transcribing":
      return "Transcription in progress";

    case "transcribed":
      return "Open transcript and notes";

    case "failed":
      return "Needs attention";

    default:
      return "";
  }
}