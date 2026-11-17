import { FormEvent, useEffect, useState } from "react";

type Idea = { id: number; content: string; created_at: string };
const API_URL = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function loadIdeas() {
    try {
      setError("");
      const response = await fetch(`${API_URL}/api/ideas`);
      if (!response.ok) throw new Error("Could not load ideas");
      setIdeas(await response.json());
    } catch {
      setError("Unable to connect to the API. Please check that the services are running.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void loadIdeas(); }, []);

  async function submitIdea(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = content.trim();
    if (!trimmed) return;

    setSaving(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/ideas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: trimmed })
      });
      if (!response.ok) throw new Error("Could not save idea");
      const saved: Idea = await response.json();
      setIdeas(current => [saved, ...current]);
      setContent("");
    } catch {
      setError("Your idea could not be saved. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <span className="eyebrow">THINK · SHARE · BUILD</span>
        <h1>Idea Board</h1>
        <p>A simple place to capture ideas and make them visible.</p>
      </header>

      <section className="composer">
        <h2>Share an idea</h2>
        <form onSubmit={submitIdea}>
          <textarea
            value={content}
            onChange={event => setContent(event.target.value)}
            placeholder="What’s on your mind?"
            maxLength={2000}
            rows={3}
            required
          />
          <div className="form-footer">
            <span>{content.length}/2000</span>
            <button disabled={saving || !content.trim()}>{saving ? "Posting…" : "Post idea"}</button>
          </div>
        </form>
      </section>

      {error && <p className="error" role="alert">{error}</p>}

      <section className="ideas-section">
        <div className="section-heading">
          <h2>Community ideas</h2>
          <span className="count">{ideas.length}</span>
        </div>
        {loading ? <p className="muted">Loading ideas…</p> :
          ideas.length === 0 ? <div className="empty"><strong>No ideas yet</strong><p>Be the first to share one.</p></div> :
            <div className="ideas-list">
              {ideas.map(idea => (
                <article className="idea-card" key={idea.id}>
                  <p>{idea.content}</p>
                  <time dateTime={idea.created_at}>{new Date(idea.created_at).toLocaleString()}</time>
                </article>
              ))}
            </div>
        }
      </section>
    </main>
  );
}