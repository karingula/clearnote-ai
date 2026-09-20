"use client";

import { ChangeEvent, Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import {
  generateNotes,
  getNotes,
  getTranscript,
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


function ClearNotePage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const selectedRecordingId =
    searchParams.get("recording");

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [openingRecording, setOpeningRecording] =
    useState(false);

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
    const file =
      event.target.files?.[0] ?? null;

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

      router.replace(
        `/?recording=${uploadedRecording.id}`
      );

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


  async function handleSelectRecording(
    selectedRecording: Recording,
    updateUrl = true
  ) {
    try {
      setOpeningRecording(true);
      setError(null);

      setRecording(selectedRecording);

      if (updateUrl) {
        router.replace(
          `/?recording=${selectedRecording.id}`
        );
      }

      setTranscript(null);
      setNotes(null);

      let existingTranscript: Transcript | null =
        null;

      try {
        existingTranscript =
          await getTranscript(
            selectedRecording.id
          );

        setTranscript(existingTranscript);
        setStep("transcribed");
      } catch {
        setStep("uploaded");
      }

      if (existingTranscript) {
        try {
          const existingNotes =
            await getNotes(
              selectedRecording.id
            );

          setNotes(existingNotes);
          setStep("complete");
        } catch {
          setNotes(null);
        }
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not open recording."
      );

      setStep("error");
    } finally {
      setOpeningRecording(false);
    }
  }


  /*
   * Load recording history when the app opens.
   */
  useEffect(() => {
    async function loadRecordings() {
      try {
        setRecordingsLoading(true);
        setRecordingsError(null);

        const result =
          await listRecordings();

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

    void loadRecordings();
  }, []);


  /*
   * Restore the selected recording after refresh.
   *
   * The URL contains:
   *
   * ?recording=<uuid>
   */
  useEffect(() => {
    if (
      !selectedRecordingId ||
      recordings.length === 0
    ) {
      return;
    }

    if (
      recording?.id === selectedRecordingId
    ) {
      return;
    }

    const selectedRecording =
  recordings.find(
    (item) =>
      item.id === selectedRecordingId
  );

if (!selectedRecording) {
  return;
}

const restoredRecording: Recording =
  selectedRecording;

const recordingId =
  restoredRecording.id;

let cancelled = false;

async function restoreRecording() {
  let existingTranscript:
    | Transcript
    | null = null;

  let existingNotes:
    | GeneratedNote
    | null = null;

  try {
    existingTranscript =
      await getTranscript(recordingId);
  } catch {
    existingTranscript = null;
  }

  if (existingTranscript) {
    try {
      existingNotes =
        await getNotes(recordingId);
    } catch {
      existingNotes = null;
    }
  }

  if (cancelled) {
    return;
  }

  setRecording(restoredRecording);
  setTranscript(existingTranscript);
  setNotes(existingNotes);

  if (existingNotes) {
    setStep("complete");
  } else if (existingTranscript) {
    setStep("transcribed");
  } else {
    setStep("uploaded");
  }
}

    void restoreRecording();

    return () => {
      cancelled = true;
    };
  }, [
    selectedRecordingId,
    recordings,
    recording?.id,
  ]);


  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-50/70 via-slate-50 to-white">
      <div className="mx-auto max-w-5xl px-6 py-12">

        <header className="mb-10">
          <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-indigo-600">
            Privacy-conscious conversation intelligence
          </p>

          <h1 className="text-4xl font-bold tracking-tight text-slate-950">
            ClearNote{" "}
            <span className="text-indigo-600">
              AI
            </span>
          </h1>

          <p className="mt-4 whitespace-nowrap text-lg text-slate-600">
            Upload a recording, transcribe it locally with Whisper, and generate structured AI notes.
          </p>
        </header>


        {/* Recent Recordings */}

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
              {recordings.length}{" "}
              recording
              {recordings.length === 1
                ? ""
                : "s"}
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


          {!recordingsLoading &&
            !recordingsError &&
            recordings.length > 0 && (

              <div className="mt-6 grid gap-4">

                {recordings.map((item) => {

                  const isSelected =
                    selectedRecordingId ===
                    item.id;

                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() =>
                        handleSelectRecording(
                          item
                        )
                      }
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
                                {
                                  item.original_filename
                                }
                              </p>

                              <p className="mt-1 text-sm text-slate-500">
                                {formatCreatedAt(
                                  item.created_at
                                )}
                              </p>

                            </div>

                          </div>


                          <div className="mt-4 flex flex-wrap items-center gap-3">

                            <RecordingStatusBadge
                              status={
                                item.status
                              }
                            />

                            <span className="text-sm text-slate-500">
                              {getRecordingNextAction(
                                item.status
                              )}
                            </span>

                          </div>

                        </div>


                        <div className="pt-2 text-xl text-slate-400 transition group-hover:translate-x-1 group-hover:text-indigo-600">
                          →
                        </div>

                      </div>

                    </button>
                  );
                })}

              </div>
            )}

        </section>


        {openingRecording && (
          <div className="mb-8 rounded-xl border border-indigo-200 bg-indigo-50 p-4 text-sm font-medium text-indigo-700">
            Opening recording...
          </div>
        )}


        {/* Upload */}

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
                onChange={
                  handleFileChange
                }
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
              disabled={
                !selectedFile ||
                step === "uploading"
              }
              className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {step === "uploading"
                ? "Uploading..."
                : "Upload"}
            </button>

          </div>


          {selectedFile && (
            <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm">

              <div className="font-medium text-slate-900">
                {selectedFile.name}
              </div>

              <div className="mt-1 text-slate-500">
                {(
                  selectedFile.size /
                  1024 /
                  1024
                ).toFixed(2)}{" "}
                MB
              </div>

            </div>
          )}

        </section>


        {/* Error */}

        {error && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {error}
          </div>
        )}


        {/* Current Recording */}

        {recording && (
          <section className="mt-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">

            <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-center">

              <div>

                <h2 className="text-xl font-semibold text-slate-950">
                  2. Recording
                </h2>

                <p className="mt-2 text-sm text-slate-600">
                  {
                    recording.original_filename
                  }
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Status:{" "}
                  {recording.status}
                </p>

              </div>


              {!transcript && (
                <button
                  type="button"
                  onClick={
                    handleTranscribe
                  }
                  disabled={
                    step ===
                    "transcribing"
                  }
                  className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {step ===
                  "transcribing"
                    ? "Transcribing..."
                    : "Transcribe"}
                </button>
              )}

            </div>

          </section>
        )}


        {/* Transcript */}

        {transcript && (
          <section className="mt-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">

            <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-center">

              <div>

                <h2 className="text-xl font-semibold text-slate-950">
                  3. Transcript
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Language:{" "}
                  {transcript.language ??
                    "Unknown"}
                </p>

              </div>


              {!notes && (
                <button
                  type="button"
                  onClick={
                    handleGenerateNotes
                  }
                  disabled={
                    step ===
                    "generating"
                  }
                  className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {step ===
                  "generating"
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


            {transcript.segments.length >
              0 && (

              <div className="mt-8">

                <h3 className="font-semibold text-slate-900">
                  Timestamped segments
                </h3>


                <div className="mt-4 space-y-3">

                  {transcript.segments.map(
                    (segment) => (

                      <div
                        key={segment.id}
                        className="rounded-lg border border-slate-200 p-4"
                      >

                        <div className="text-xs font-medium text-slate-500">

                          {formatSeconds(
                            segment.start_seconds
                          )}

                          {" → "}

                          {formatSeconds(
                            segment.end_seconds
                          )}

                        </div>


                        <p className="mt-2 text-slate-800">
                          {
                            segment.text
                          }
                        </p>

                      </div>
                    )
                  )}

                </div>

              </div>
            )}

          </section>
        )}


        {/* AI Notes */}

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
                items={
                  notes.key_points
                }
              />


              <NoteList
                title="Decisions"
                items={
                  notes.decisions
                }
              />


              <NoteSection title="Action Items">

                {notes.action_items
                  .length === 0 ? (

                  <EmptyState />

                ) : (

                  <div className="space-y-3">

                    {notes.action_items.map(
                      (
                        item,
                        index
                      ) => (

                        <div
                          key={`${item.task}-${index}`}
                          className="rounded-lg bg-slate-50 p-4"
                        >

                          <p className="font-medium text-slate-900">
                            {
                              item.task
                            }
                          </p>


                          <div className="mt-2 text-sm text-slate-500">

                            Owner:{" "}
                            {item.owner ??
                              "Not specified"}

                            {" · "}

                            Due:{" "}
                            {item.due_date ??
                              "Not specified"}

                          </div>

                        </div>
                      )
                    )}

                  </div>
                )}

              </NoteSection>


              <NoteList
                title="Follow-up Questions"
                items={
                  notes.follow_up_questions
                }
              />

            </div>

          </section>
        )}

      </div>
    </main>
  );
}



function formatSeconds(
  seconds: number
): string {
  const minutes =
    Math.floor(seconds / 60);

  const remainingSeconds =
    Math.floor(seconds % 60);

  return `${minutes}:${remainingSeconds
    .toString()
    .padStart(2, "0")}`;
}



function formatCreatedAt(
  value: string
): string {
  return new Date(
    value
  ).toLocaleString();
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

          {items.map(
            (item, index) => (

              <li
                key={`${item}-${index}`}
                className="rounded-lg bg-slate-50 p-4 text-slate-700"
              >
                {item}
              </li>

            )
          )}

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

export default function Home() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-gradient-to-b from-indigo-50/70 via-slate-50 to-white">
          <div className="mx-auto max-w-5xl px-6 py-12">
            <p className="text-sm text-slate-500">
              Loading ClearNote AI...
            </p>
          </div>
        </main>
      }
    >
      <ClearNotePage />
    </Suspense>
  );
}