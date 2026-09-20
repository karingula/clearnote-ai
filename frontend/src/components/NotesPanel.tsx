import type { ReactNode } from "react";

import type { GeneratedNote } from "@/types/api";

type NotesPanelProps = {
  notes: GeneratedNote;
};

export default function NotesPanel({
  notes,
}: NotesPanelProps) {
  return (
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
              {notes.action_items.map(
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

        <NoteList
          title="Follow-up Questions"
          items={
            notes.follow_up_questions
          }
        />
      </div>
    </section>
  );
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

function EmptyState() {
  return (
    <p className="text-sm text-slate-500">
      None identified.
    </p>
  );
}