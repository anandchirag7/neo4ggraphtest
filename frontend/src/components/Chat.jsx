
import React, { useState } from "react";
import { API } from "../api";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await API.post("/ask", { question });
      setAnswer(res.data);
    } catch (e) {
      console.error(e);
      setAnswer({ answer_text: "Error while querying backend." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea
        rows={3}
        style={{ width: "100%" }}
        placeholder="Ask a question about your uploaded datasheets..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={ask} disabled={loading}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {answer && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Answer</h3>
          <p>{answer.answer_text}</p>

          {answer.figures && answer.figures.length > 0 && (
            <>
              <h4>Relevant Figures</h4>
              {answer.figures.map((f) => (
                <div key={f.node_id} style={{ marginBottom: "1rem" }}>
                  <p>
                    <b>{f.doc_id}</b> — page {f.page}
                  </p>
                  {f.image_url && (
                    <img
                      src={`http://localhost:8000${f.image_url}`}
                      alt={f.caption}
                      style={{ maxWidth: "100%", border: "1px solid #ccc" }}
                    />
                  )}
                  <div style={{ fontSize: "0.9rem", color: "#555" }}>
                    {f.caption}
                  </div>
                </div>
              ))}
            </>
          )}

          {answer.tables && answer.tables.length > 0 && (
            <>
              <h4>Relevant Tables</h4>
              {answer.tables.map((t) => (
                <div key={t.node_id} style={{ marginBottom: "1rem" }}>
                  <p>
                    <b>{t.doc_id}</b> — page {t.page}
                  </p>
                  {t.table_data && (
                    <div style={{ overflowX: "auto" }}>
                      <table
                        style={{
                          width: "100%",
                          borderCollapse: "collapse",
                          border: "1px solid #ccc",
                          fontSize: "0.9rem",
                        }}
                      >
                        <thead>
                          <tr style={{ backgroundColor: "#f5f5f5" }}>
                            {t.table_data[0] &&
                              Object.keys(t.table_data[0]).map((header, idx) => (
                                <th
                                  key={idx}
                                  style={{
                                    border: "1px solid #ccc",
                                    padding: "8px",
                                    textAlign: "left",
                                    fontWeight: "600",
                                  }}
                                >
                                  {header}
                                </th>
                              ))}
                          </tr>
                        </thead>
                        <tbody>
                          {t.table_data.map((row, rowIdx) => (
                            <tr key={rowIdx}>
                              {Object.values(row).map((cell, cellIdx) => (
                                <td
                                  key={cellIdx}
                                  style={{
                                    border: "1px solid #ccc",
                                    padding: "8px",
                                  }}
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {t.caption && (
                    <div style={{ fontSize: "0.9rem", color: "#555", marginTop: "0.5rem" }}>
                      {t.caption}
                    </div>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}
