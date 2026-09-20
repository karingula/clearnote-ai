import RecordingCard from "@/components/RecordingCard";
import type { Recording } from "@/types/api";

type RecordingHistoryProps = {
  recordings: Recording[];
  selectedRecordingId: string | null;
  loading: boolean;
  error: string | null;
  onSelectRecording: (recording: Recording) => void;
};

export default function RecordingHistory({
  recordings,
  selectedRecordingId,
  loading,
  error,
  onSelectRecording,
}: RecordingHistoryProps) {
  return (
    <section className="mb-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">
      <div className="flex items-start justify-between gap-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-indigo-600">
            Workspace
          </p>

          <h2 className="mt-1 text-2xl font-bold text-slate-950">
            Recent Recordings
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Reopen previous recordings or continue where you left off.
          </p>
        </div>

        <div className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700">
          {recordings.length} recording
          {recordings.length === 1 ? "" : "s"}
        </div>
      </div>

      {loading && (
        <p className="mt-6 text-sm text-slate-500">
          Loading recordings...
        </p>
      )}

      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      )}

      {!loading &&
        !error &&
        recordings.length === 0 && (
          <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center">
            <div className="text-3xl">
              🎙️
            </div>

            <h3 className="mt-3 font-semibold text-slate-900">
              No recordings yet
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              Upload your first audio file to create a transcript and AI notes.
            </p>
          </div>
        )}

      {!loading &&
        !error &&
        recordings.length > 0 && (
          <div className="mt-6 grid gap-4">
            {recordings.map((recording) => (
              <RecordingCard
                key={recording.id}
                recording={recording}
                isSelected={
                  selectedRecordingId === recording.id
                }
                onSelect={onSelectRecording}
              />
            ))}
          </div>
        )}
    </section>
  );
}