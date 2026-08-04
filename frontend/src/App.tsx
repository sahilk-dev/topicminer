import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState<string>("checking...");

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("backend unreachable"));
  }, []);

  return(
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>TopicMiner</h1>
      <p>Backend Status: <strong>{status}</strong></p>
    </div>
  );
}

export default App;