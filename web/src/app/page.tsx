"use client";

import { FormEvent, useRef, useState } from "react";

type ClassifyResponse = {
  task_type: string;
  domain: string | null;
  urgency: string;
  stakeholder: string | null;
  autonomous: boolean;
  primary_model: string;
  fallback_chain: string[];
};

type Exchange = {
  id: string;
  text: string;
  status: "loading" | "done" | "error";
  result?: ClassifyResponse;
  error?: string;
};

const URGENCY_STYLES: Record<string, string> = {
  routine: "bg-muted text-muted-foreground",
  priority: "bg-primary/10 text-primary",
  critical: "bg-destructive/10 text-destructive",
};

async function classify(text: string): Promise<ClassifyResponse> {
  const response = await fetch("/backend/api/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    throw new Error(`Backend ответил ${response.status}`);
  }
  return response.json();
}

function ResultCard({ result }: { result: ClassifyResponse }) {
  const urgencyClass = URGENCY_STYLES[result.urgency] ?? URGENCY_STYLES.routine;
  return (
    <dl className="grid grid-cols-2 gap-x-4 gap-y-2 rounded-lg border border-border bg-muted/60 p-4 text-sm sm:grid-cols-3">
      <div>
        <dt className="text-muted-foreground">Тип задачи</dt>
        <dd className="font-medium">{result.task_type}</dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Домен</dt>
        <dd className="font-medium">{result.domain ?? "—"}</dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Срочность</dt>
        <dd>
          <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${urgencyClass}`}>
            {result.urgency}
          </span>
        </dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Стейкхолдер</dt>
        <dd className="font-medium">{result.stakeholder ?? "—"}</dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Автономно</dt>
        <dd className="font-medium">{result.autonomous ? "Да" : "Нет"}</dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Модель</dt>
        <dd className="font-medium">{result.primary_model}</dd>
      </div>
    </dl>
  );
}

export default function Home() {
  const [input, setInput] = useState("");
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const isBusy = exchanges.some((e) => e.status === "loading");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = input.trim();
    if (!text || isBusy) return;

    const id = crypto.randomUUID();
    setExchanges((prev) => [...prev, { id, text, status: "loading" }]);
    setInput("");

    try {
      const result = await classify(text);
      setExchanges((prev) =>
        prev.map((e) => (e.id === id ? { ...e, status: "done", result } : e))
      );
    } catch (err) {
      setExchanges((prev) =>
        prev.map((e) =>
          e.id === id
            ? { ...e, status: "error", error: err instanceof Error ? err.message : "Неизвестная ошибка" }
            : e
        )
      );
    } finally {
      inputRef.current?.focus();
    }
  }

  function handleRetry(exchange: Exchange) {
    setInput(exchange.text);
    setExchanges((prev) => prev.filter((e) => e.id !== exchange.id));
    inputRef.current?.focus();
  }

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-2xl flex-col px-4 py-6">
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Jarvis OS</h1>
        <p className="text-sm text-muted-foreground">
          Опиши задачу — покажу, как она классифицируется и какая модель её обработает.
        </p>
      </header>

      <main className="flex-1 space-y-4" aria-live="polite">
        {exchanges.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Например: «Нужна презентация резидентов ИНТЦ для Трутнева».
          </p>
        )}

        {exchanges.map((exchange) => (
          <div key={exchange.id} className="space-y-2">
            <p className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground w-fit max-w-[85%] ml-auto">
              {exchange.text}
            </p>

            {exchange.status === "loading" && (
              <div
                className="h-16 w-full animate-pulse rounded-lg border border-border bg-muted/60"
                role="status"
                aria-label="Классифицирую..."
              />
            )}

            {exchange.status === "done" && exchange.result && (
              <ResultCard result={exchange.result} />
            )}

            {exchange.status === "error" && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm">
                <p className="text-destructive">Не получилось: {exchange.error}</p>
                <button
                  type="button"
                  onClick={() => handleRetry(exchange)}
                  className="mt-2 cursor-pointer rounded-md border border-border px-3 py-1 text-sm font-medium hover:bg-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring"
                >
                  Повторить
                </button>
              </div>
            )}
          </div>
        ))}
      </main>

      <form onSubmit={handleSubmit} className="sticky bottom-0 mt-6 flex gap-2 bg-background pt-2">
        <label htmlFor="task-input" className="sr-only">
          Описание задачи
        </label>
        <input
          id="task-input"
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Опиши задачу..."
          disabled={isBusy}
          className="flex-1 rounded-lg border border-border bg-background px-4 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={isBusy || !input.trim()}
          className="cursor-pointer rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring disabled:cursor-not-allowed disabled:opacity-50"
        >
          Отправить
        </button>
      </form>
    </div>
  );
}
