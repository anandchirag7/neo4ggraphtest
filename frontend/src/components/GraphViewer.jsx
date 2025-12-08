
import React, { useEffect, useState } from "react";
import { API } from "../api";
import ForceGraph2D from "react-force-graph-2d";

export default function GraphViewer() {
  const [docs, setDocs] = useState([]);
  const [docId, setDocId] = useState("");
  const [graph, setGraph] = useState(null);

  useEffect(() => {
    API.get("/documents")
      .then((res) => setDocs(res.data))
      .catch((e) => console.error(e));
  }, []);

  const loadGraph = async () => {
    if (!docId) return;
    try {
      const res = await API.get(`/graph/${docId}`);
      setGraph(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <div>
        <select value={docId} onChange={(e) => setDocId(e.target.value)}>
          <option value="">Select document...</option>
          {docs.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        <button onClick={loadGraph} disabled={!docId}>
          Load graph
        </button>
      </div>

      <div style={{ height: "400px", border: "1px solid #ddd", marginTop: "1rem" }}>
        {graph ? (
          <ForceGraph2D
            graphData={graph}
            nodeLabel="label"
            nodeAutoColorBy="group"
          />
        ) : (
          <p style={{ padding: "1rem" }}>No graph loaded.</p>
        )}
      </div>
    </div>
  );
}
