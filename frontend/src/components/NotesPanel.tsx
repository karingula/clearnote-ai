"use client";

import {
  useState,
  type ReactNode,
} from "react";

import type {
  ActionItem,
  GeneratedNote,
  ReviewedNote,
  ReviewedNoteInput,
} from "@/types/api";


type NotesPanelProps = {
  notes: GeneratedNote;
  reviewedNote: ReviewedNote | null;
  savingReview: boolean;
  onSaveReview: (
    payload: ReviewedNoteInput
  ) => Promise<void>;
};


export default function NotesPanel({
  notes,
  reviewedNote,
  savingReview,
  onSaveReview,
}: NotesPanelProps) {
  const [isEditing, setIsEditing] =
    useState(false);

  const [draft, setDraft] =
    useState<ReviewedNoteInput>(
      createReviewDraft(
        reviewedNote ?? notes
      )
    );

  function startReview() {
    setDraft(
      createReviewDraft(
        reviewedNote ?? notes
      )
    );

    setIsEditing(true);
  }


  function cancelReview() {
    setDraft(
      createReviewDraft(
        reviewedNote ?? notes
      )
    );

    setIsEditing(false);
  }


  async function saveReview() {
    await onSaveReview(draft);

    setIsEditing(false);
  }


  if (isEditing) {
    return (
      <ReviewEditor
        draft={draft}
        setDraft={setDraft}
        saving={savingReview}
        onSave={saveReview}
        onCancel={cancelReview}
      />
    );
  }


  return (
    <section className="mt-8 rounded-2xl border border-slate-200/80 bg-white/90 p-8 shadow-sm backdrop-blur">

      <div className="flex items-center justify-between gap-4">

        <div>
          <h2 className="text-xl font-semibold text-slate-950">
            4. AI Notes
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Original AI-generated draft
          </p>
        </div>


        <div className="flex items-center gap-3">

          {reviewedNote ? (
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
              Reviewed
            </span>
          ) : (
            <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
              Not reviewed
            </span>
          )}


          <button
            type="button"
            onClick={startReview}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
          >
            {reviewedNote
              ? "Edit Review"
              : "Review Notes"}
          </button>

        </div>

      </div>


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


        <ActionItemList
          items={notes.action_items}
        />


        <NoteList
          title="Follow-up Questions"
          items={
            notes.follow_up_questions
          }
        />

      </div>


      {reviewedNote && (
        <div className="mt-10 border-t border-slate-200 pt-8">

          <p className="text-sm font-semibold uppercase tracking-wider text-emerald-700">
            Human Reviewed Version
          </p>

          <div className="mt-6 space-y-8">

            <NoteSection title="Summary">
              <p className="leading-7 text-slate-700">
                {reviewedNote.summary}
              </p>
            </NoteSection>


            <NoteList
              title="Key Points"
              items={
                reviewedNote.key_points
              }
            />


            <NoteList
              title="Decisions"
              items={
                reviewedNote.decisions
              }
            />


            <ActionItemList
              items={
                reviewedNote.action_items
              }
            />


            <NoteList
              title="Follow-up Questions"
              items={
                reviewedNote.follow_up_questions
              }
            />

          </div>

        </div>
      )}

    </section>
  );
}


type ReviewEditorProps = {
  draft: ReviewedNoteInput;

  setDraft: React.Dispatch<
    React.SetStateAction<ReviewedNoteInput>
  >;

  saving: boolean;

  onSave: () => Promise<void>;

  onCancel: () => void;
};


function ReviewEditor({
  draft,
  setDraft,
  saving,
  onSave,
  onCancel,
}: ReviewEditorProps) {

  function updateActionItem(
    index: number,
    field: keyof ActionItem,
    value: string
  ) {
    setDraft((current) => ({
      ...current,

      action_items:
        current.action_items.map(
          (item, itemIndex) =>
            itemIndex === index
              ? {
                ...item,
                [field]:
                  value.trim() === ""
                    ? null
                    : value,
              }
              : item
        ),
    }));
  }


  function addActionItem() {
    setDraft((current) => ({
      ...current,

      action_items: [
        ...current.action_items,

        {
          task: "",
          owner: null,
          due_date: null,
        },
      ],
    }));
  }


  function removeActionItem(
    index: number
  ) {
    setDraft((current) => ({
      ...current,

      action_items:
        current.action_items.filter(
          (_, itemIndex) =>
            itemIndex !== index
        ),
    }));
  }


  return (
    <section className="mt-8 rounded-2xl border border-indigo-200 bg-white p-8 shadow-sm">

      <div className="flex items-start justify-between gap-6">

        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-indigo-600">
            Human Review
          </p>

          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            Review AI Notes
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Correct anything the AI got wrong before approving these notes.
          </p>
        </div>

      </div>


      <div className="mt-8 space-y-8">

        <ReviewField title="Summary">

          <textarea
            value={draft.summary}
            onChange={(event) =>
              setDraft((current) => ({
                ...current,
                summary:
                  event.target.value,
              }))
            }
            rows={5}
            className="w-full rounded-lg border border-slate-300 p-3 text-slate-800 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
          />

        </ReviewField>


        <ReviewListField
          title="Key Points"
          items={draft.key_points}
          onChange={(items) =>
            setDraft((current) => ({
              ...current,
              key_points: items,
            }))
          }
        />


        <ReviewListField
          title="Decisions"
          items={draft.decisions}
          onChange={(items) =>
            setDraft((current) => ({
              ...current,
              decisions: items,
            }))
          }
        />


        <ReviewField title="Action Items">

          <div className="space-y-4">

            {draft.action_items.map(
              (item, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                >

                  <div className="space-y-3">

                    <input
                      type="text"
                      value={item.task}
                      placeholder="Task"
                      onChange={(event) =>
                        updateActionItem(
                          index,
                          "task",
                          event.target.value
                        )
                      }
                      className="w-full rounded-lg border border-slate-300 bg-white p-3 text-sm text-slate-800"
                    />


                    <div className="grid gap-3 sm:grid-cols-2">

                      <input
                        type="text"
                        value={
                          item.owner ?? ""
                        }
                        placeholder="Owner"
                        onChange={(event) =>
                          updateActionItem(
                            index,
                            "owner",
                            event.target.value
                          )
                        }
                        className="rounded-lg border border-slate-300 bg-white p-3 text-sm text-slate-800"
                      />


                      <input
                        type="date"
                        value={
                          item.due_date ?? ""
                        }
                        placeholder="Due date"
                        onChange={(event) =>
                          updateActionItem(
                            index,
                            "due_date",
                            event.target.value
                          )
                        }
                        className="rounded-lg border border-slate-300 bg-white p-3 text-sm text-slate-800"
                      />

                    </div>


                    <button
                      type="button"
                      onClick={() =>
                        removeActionItem(
                          index
                        )
                      }
                      className="text-sm font-medium text-red-600 hover:text-red-700"
                    >
                      Remove action item
                    </button>

                  </div>

                </div>
              )
            )}


            <button
              type="button"
              onClick={addActionItem}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              + Add action item
            </button>

          </div>

        </ReviewField>


        <ReviewListField
          title="Follow-up Questions"
          items={
            draft.follow_up_questions
          }
          onChange={(items) =>
            setDraft((current) => ({
              ...current,
              follow_up_questions: items,
            }))
          }
        />

      </div>


      <div className="mt-10 flex justify-end gap-3">

        <button
          type="button"
          onClick={onCancel}
          disabled={saving}
          className="rounded-lg border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 disabled:opacity-50"
        >
          Cancel
        </button>


        <button
          type="button"
          onClick={() => void onSave()}
          disabled={saving}
          className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving
            ? "Saving..."
            : "Save Review"}
        </button>

      </div>

    </section>
  );
}


type ReviewListFieldProps = {
  title: string;
  items: string[];
  onChange: (items: string[]) => void;
};


function ReviewListField({
  title,
  items,
  onChange,
}: ReviewListFieldProps) {
  return (
    <ReviewField title={title}>

      <textarea
        value={items.join("\n")}
        onChange={(event) =>
          onChange(
            event.target.value
              .split("\n")
              .map((item) =>
                item.trim()
              )
              .filter(Boolean)
          )
        }
        rows={5}
        className="w-full rounded-lg border border-slate-300 p-3 text-slate-800 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
      />

      <p className="mt-2 text-xs text-slate-500">
        Enter one item per line.
      </p>

    </ReviewField>
  );
}


type ReviewFieldProps = {
  title: string;
  children: ReactNode;
};


function ReviewField({
  title,
  children,
}: ReviewFieldProps) {
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


function createReviewDraft(
  source: GeneratedNote | ReviewedNote
): ReviewedNoteInput {
  return {
    summary: source.summary,

    decisions: [
      ...source.decisions,
    ],

    action_items:
      source.action_items.map(
        (item) => ({
          ...item,
        })
      ),

    key_points: [
      ...source.key_points,
    ],

    follow_up_questions: [
      ...source.follow_up_questions,
    ],
  };
}


type NoteSectionProps = {
  title: string;
  children: ReactNode;
};


function NoteSection({
  title,
  children,
}: NoteSectionProps) {
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


type NoteListProps = {
  title: string;
  items: string[];
};


function NoteList({
  title,
  items,
}: NoteListProps) {
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


function ActionItemList({
  items,
}: {
  items: ActionItem[];
}) {
  return (
    <NoteSection title="Action Items">

      {items.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="space-y-3">

          {items.map(
            (item, index) => (
              <div
                key={`${item.task}-${index}`}
                className="rounded-lg bg-slate-50 p-4"
              >

                <p className="font-medium text-slate-900">
                  {item.task}
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
  );
}


function EmptyState() {
  return (
    <p className="text-sm text-slate-500">
      None identified.
    </p>
  );
}