const API_URL = import.meta.env.VITE_API_URL;

export async function analyzeVideo(url: string) {
    const res = await fetch(`${API_URL}/videos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error("Failed to analyze video");
    return res.json();
}

export async function classifyComments(videoId: string) {
    const res = await fetch(`${API_URL}/videos/${videoId}/classify`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to classify comments");
    return res.json();
}

export async function clusterTopics(videoId: string) {
    const res = await fetch(`${API_URL}/videos/${videoId}/cluster-topics`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to cluster topics");
    return res.json();
}