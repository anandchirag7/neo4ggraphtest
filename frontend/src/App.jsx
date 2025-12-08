
import React from "react";
import FileUpload from "./components/FileUpload";
import Chat from "./components/Chat";
import GraphViewer from "./components/GraphViewer";

export default function App() {
  return (
    <div style={{ padding: "1rem", fontFamily: "sans-serif" }}>
      <h1>Enterprise KB App</h1>
      <section>
        <h2>1. Upload PDF</h2>
        <FileUpload />
      </section>
      <hr />
      <section>
        <h2>2. Knowledge Graph</h2>
        <GraphViewer />
      </section>
      <hr />
      <section>
        <h2>3. Chat</h2>
        <Chat />
      </section>
    </div>
  );
}
