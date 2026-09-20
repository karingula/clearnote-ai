import type { ChangeEvent } from "react";

type UploadSectionProps = {
  selectedFile: File | null;
  uploading: boolean;
  onFileChange: (
    event: ChangeEvent<HTMLInputElement>
  ) => void;
  onUpload: () => void;
};

export default function UploadSection({
  selectedFile,
  uploading,
  onFileChange,
  onUpload,
}: UploadSectionProps) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">
      <h2 className="text-xl font-semibold text-slate-950">
        1. Upload recording
      </h2>

      <p className="mt-2 text-sm text-slate-600">
        Supported formats include MP3, M4A, WAV and WebM.
      </p>

      <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-center">
        <label className="inline-flex cursor-pointer items-center justify-center rounded-lg border border-indigo-200 bg-indigo-50 px-5 py-3 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-100">
          Choose Audio File

          <input
            type="file"
            accept=".mp3,.m4a,.wav,.webm,audio/*"
            onChange={onFileChange}
            className="hidden"
          />
        </label>

        <span className="text-sm text-slate-500">
          {selectedFile
            ? selectedFile.name
            : "Please select an audio file"}
        </span>

        <button
          type="button"
          onClick={onUpload}
          disabled={!selectedFile || uploading}
          className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {selectedFile && (
        <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm">
          <div className="font-medium text-slate-900">
            {selectedFile.name}
          </div>

          <div className="mt-1 text-slate-500">
            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
          </div>
        </div>
      )}
    </section>
  );
}