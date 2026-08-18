"use client";

import { ChangeEvent, useEffect, useState } from "react";

import {
  generateNotes,
  listRecordings,
  transcribeRecording,
  uploadRecording,
} from "@/lib/api";

import type {
  GeneratedNote,
  Recording,
  Transcript,
} from "@/types/api";


type ProcessingStep =
  | "idle"
  | "uploading"
  | "uploaded"
  | "transcribing"
  | "transcribed"
  | "generating"
  | "complete"
  | "error";


export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [recording, setRecording] =
    useState<Recording | null>(null);

  const [transcript, setTranscript] =
    useState<Transcript | null>(null);

  const [notes, setNotes] =
    useState<GeneratedNote | null>(null);

  const [step, setStep] =
    useState<ProcessingStep>("idle");

  const [error, setError] =
    useState<string | null>(null);
  
  const [recordings, setRecordings] = 
    useState<Recording[]>([]);
  
  const [recordingsLoading, setRecordingsLoading] =
    useState(true);
  
  const [recordingsError, setRecordingsError] =
    useState<string | null>(null);


  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0] ?? null;

    setSelectedFile(file);

    setRecording(null);
    setTranscript(null);
    setNotes(null);
    setError(null);

    setStep("idle");
  }


  async function handleUpload() {
    if (!selectedFile) {
      setError("Please select an audio file.");
      return;
    }

    try {
      setError(null);
      setStep("uploading");

      const uploadedRecording =
        await uploadRecording(selectedFile);
      
      setRecording(uploadedRecording);
      setRecordings((current) => [
        uploadedRecording,
        ...current,
      ]);
      
      setStep("uploaded");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Upload failed."
      );

      setStep("error");
    }
  }


  async function handleTranscribe() {
    if (!recording) {
      return;
    }

    try {
      setError(null);
      setStep("transcribing");

      const result =
        await transcribeRecording(recording.id);

      setTranscript(result);
      setRecording((current) =>
        current
          ? {
            ...current,
            status: "transcribed",
          }
        : current
      );

      setRecordings((current) =>
        current.map((item) =>
          item.id === recording.id
            ? {
              ...item,
              status: "transcribed",
              }
            : item
        )
      );

      setStep("transcribed");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Transcription failed."
      );

      setStep("error");
    }
  }


  async function handleGenerateNotes() {
    if (!recording) {
      return;
    }

    try {
      setError(null);
      setStep("generating");

      const result =
        await generateNotes(recording.id);

      setNotes(result);
      setStep("complete");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Note generation failed."
      );

      setStep("error");
    }
  }

  useEffect(() => {
  async function loadRecordings() {
    try {
      setRecordingsLoading(true);
      setRecordingsError(null);

      const result = await listRecordings();
      console.log("listRecordings result:", result);
      console.log("is array:", Array.isArray(result));

      setRecordings(result);
    } catch (err) {
      setRecordingsError(
        err instanceof Error
          ? err.message
          : "Could not load recordings."
      );
    } finally {
      setRecordingsLoading(false);
    }
  }

  loadRecordings();
}, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-50/70 via-slate-50 to-white">
      <div className="mx-auto max-w-5xl px-6 py-12">
        <header className="mb-10">
  <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-indigo-600">
    Privacy-conscious conversation intelligence
  </p>

  <h1 className="text-4xl font-bold tracking-tight text-slate-950">
    ClearNote <span className="text-indigo-600">AI</span>
  </h1>

  <section className="mb-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">
  <div className="flex items-center justify-between">
    <div>
      <h2 className="text-xl font-semibold text-slate-950">
        Recent Recordings
      </h2>

      <p className="mt-1 text-sm text-slate-500">
        Your previously uploaded recordings.
      </p>
    </div>
  </div>

  {recordingsLoading && (
    <p className="mt-6 text-sm text-slate-500">
      Loading recordings...
    </p>
  )}

  {recordingsError && (
    <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
      {recordingsError}
    </div>
  )}

  {!recordingsLoading &&
    !recordingsError &&
    recordings.length === 0 && (
      <div className="mt-6 rounded-xl bg-slate-50 p-6 text-center">
        <p className="text-sm text-slate-500">
          No recordings yet.
        </p>
      </div>
    )}

  {!recordingsLoading && recordings.length > 0 && (
    <div className="mt-6 divide-y divide-slate-100">
      {recordings.map((item) => (
        <div
          key={item.id}
          className="flex items-center justify-between py-4"
        >
          <div>
            <p className="font-medium text-slate-900">
              {item.original_filename}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              {formatCreatedAt(item.created_at)}
            </p>
          </div>

          <RecordingStatusBadge status={item.status} />
        </div>
      ))}
    </div>
  )}
</section>

  <p className="mt-4 whitespace-nowrap text-lg text-slate-600">
    Upload a recording, transcribe it locally with Whisper, and generate structured AI notes.
  </p>
</header>

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
      onChange={handleFileChange}
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
    onClick={handleUpload}
    disabled={!selectedFile || step === "uploading"}
    className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
  >
    {step === "uploading" ? "Uploading..." : "Upload"}
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

        {error && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {error}
          </div>
        )}

        {recording && (
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

              {!transcript && (
                <button
                  type="button"
                  onClick={handleTranscribe}
                  disabled={step === "transcribing"}
                  className="rounded-lg bg-slate-950 px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {step === "transcribing"
                    ? "Transcribing..."
                    : "Transcribe"}
                </button>
              )}
            </div>
          </section>
        )}

        {transcript && (
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

              {!notes && (
                <button
                  type="button"
                  onClick={handleGenerateNotes}
                  disabled={step === "generating"}
                  className="rounded-lg bg-slate-950 px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {step === "generating"
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
        )}

        {notes && (
          <section className="mt-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">
            <h2 className="text-xl font-semibold text-slate-950">
              4. AI Notes
            </h2>

            <div className="mt-8 space-y-8">
              <NoteSection title="Summary">
                <p className="leading-7 text-slate-700">
                  {notes.summary}
                </p>
              </NoteSection>

              <NoteList
                title="Key Points"
                items={notes.key_points}
              />

              <NoteList
                title="Decisions"
                items={notes.decisions}
              />

              <NoteSection title="Action Items">
                {notes.action_items.length === 0 ? (
                  <EmptyState />
                ) : (
                  <div className="space-y-3">
                    {notes.action_items.map((item, index) => (
                      <div
                        key={`${item.task}-${index}`}
                        className="rounded-lg bg-slate-50 p-4"
                      >
                        <p className="font-medium text-slate-900">
                          {item.task}
                        </p>

                        <div className="mt-2 text-sm text-slate-500">
                          Owner: {item.owner ?? "Not specified"}
                          {" · "}
                          Due: {item.due_date ?? "Not specified"}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </NoteSection>

              <NoteList
                title="Follow-up Questions"
                items={notes.follow_up_questions}
              />
            </div>
          </section>
        )}
      </div>
    </main>
  );
}


function formatSeconds(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  return `${minutes}:${remainingSeconds
    .toString()
    .padStart(2, "0")}`;
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
    uploaded:
      "bg-slate-100 text-slate-700",

    transcribing:
      "bg-indigo-50 text-indigo-700",

    transcribed:
      "bg-emerald-50 text-emerald-700",

    failed:
      "bg-red-50 text-red-700",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${styles[status]}`}
    >
      {status}
    </span>
  );
}


function NoteSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-slate-900">
        {title}
      </h3>

      <div className="mt-3">
        {children}
      </div>
    </div>
  );
}


function NoteList({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <NoteSection title={title}>
      {items.length === 0 ? (
        <EmptyState />
      ) : (
        <ul className="space-y-2">
          {items.map((item, index) => (
            <li
              key={`${item}-${index}`}
              className="rounded-lg bg-slate-50 p-4 text-slate-700"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </NoteSection>
  );
}


function EmptyState() {
  return (
    <p className="text-sm text-slate-500">
      None identified.
    </p>
  );
}