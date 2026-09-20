"use client";

import { ChangeEvent, Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import RecordingHistory from "@/components/RecordingHistory";
import UploadSection from "@/components/UploadSection";
import TranscriptViewer from "@/components/TranscriptViewer";
import NotesPanel from "@/components/NotesPanel";

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

        <RecordingHistory
          recordings={recordings}
          selectedRecordingId={selectedRecordingId}
          loading={recordingsLoading}
          error={recordingsError}
          onSelectRecording={handleSelectRecording}
        />


        {openingRecording && (
          <div className="mb-8 rounded-xl border border-indigo-200 bg-indigo-50 p-4 text-sm font-medium text-indigo-700">
            Opening recording...
          </div>
        )}

        <UploadSection
          selectedFile={selectedFile}
          uploading={step === "uploading"}
          onFileChange={handleFileChange}
          onUpload={handleUpload}
        />

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
          <TranscriptViewer
            transcript={transcript}
            hasNotes={Boolean(notes)}
            generating={step === "generating"}
            onGenerateNotes={handleGenerateNotes}
          />
        )}

        {/* AI Notes */}
        {notes && (
          <NotesPanel notes={notes} />
        )}

      </div>
    </main>
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