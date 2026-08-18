import type {
  GeneratedNote,
  Recording,
  RecordingListResponse,
  Transcript,
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";


async function parseApiError(response: Response): Promise<string> {
  try {
    const body = await response.json();

    if (typeof body.detail === "string") {
      return body.detail;
    }

    return `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
}


export async function uploadRecording(
  file: File
): Promise<Recording> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/recordings`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}


export async function transcribeRecording(
  recordingId: string
): Promise<Transcript> {
  const response = await fetch(
    `${API_BASE_URL}/api/recordings/${recordingId}/transcribe`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}


export async function generateNotes(
  recordingId: string
): Promise<GeneratedNote> {
  const response = await fetch(
    `${API_BASE_URL}/api/recordings/${recordingId}/generate-notes`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}

export async function listRecordings(): Promise<Recording[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/recordings?limit=50&offset=0`
  );

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  const data: RecordingListResponse = await response.json();

  return data.items;
}