import { useState } from "react";
import { analyzeVideo, classifyComments, clusterTopics } from "./api";

type Cluster = { cluster_name: string; mention_count: number; rank: number };

function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState("");
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    setLoading(true);
    setError("");
    setClusters([]);
    try {
      setStage("Fetching comments...");
      const { video_id } = await analyzeVideo(url);

      setStage("Classifying comments...");
      await classifyComments(video_id);

      setStage("Clustering topics...");
      const result = await clusterTopics(video_id);

      setClusters(result.clusters);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
      setStage("");
    }
  }

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: 700, margin: "0 auto" }}>
      <h1>TopicMiner</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: "1.5rem" }}>
        <input
          style={{ flex: 1, padding: 8 }}
          placeholder="https://youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button onClick={handleAnalyze} disabled={loading || !url}>
          {loading ? stage || "Analyzing..." : "Analyze"}
        </button>
      </div>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {clusters.length > 0 && (
        <div>
          {clusters.map((c) => (
            <div
              key={c.rank}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "12px 0",
                borderBottom: "1px solid #eee",
              }}
            >
              <span>#{c.rank} {c.cluster_name}</span>
              <strong>{c.mention_count} mentions</strong>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;