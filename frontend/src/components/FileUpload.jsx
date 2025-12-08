
import React, { useState } from "react";
import { API } from "../api";

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const upload = async () => {
    if (!file) return;
    setStatus("Uploading...");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await API.post("/upload_pdf", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus(`Uploaded: doc_id=${res.data.doc_id}`);
    } catch (e) {
      console.error(e);
      setStatus("Upload failed");
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={upload} disabled={!file}>
        Upload
      </button>
      <p>{status}</p>
    </div>
  );
}
