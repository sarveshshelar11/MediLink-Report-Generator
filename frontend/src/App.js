import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleUpload = async () => {
    if (!file) {
      alert("Please select an Excel (.xlsx) file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setMessage("Generating report...");

      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      // If the server responds with JSON, it might be an error
      const contentType = response.headers.get("content-type");

      if (!response.ok) {
        if (contentType && contentType.includes("application/json")) {
          const errJson = await response.json();
          const detail = errJson.detail || errJson.error || JSON.stringify(errJson);
          throw new Error(detail);
        } else {
          throw new Error("Server error while generating report");
        }
      }

      // Success: download the returned blob (zip)
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      // File name may be set by server; default to Patient_Reports.zip
      a.download = "Patient_Reports.zip";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setMessage("Report generated successfully ✅");
    } catch (error) {
      console.error(error);
      setMessage(`Failed to generate report: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "60px", fontFamily: "Arial" }}>
      <h2>MediLink – Patient Report Generator</h2>
      <p>Upload an Excel (.xlsx) file to generate patient PDF reports (zipped).</p>

      <input
        id="fileInput"
        type="file"
        accept=".xlsx, .xls, .csv"
        onChange={(e) => {
          setMessage("");
          setFile(e.target.files[0]);
        }}
      />
      <div style={{ marginTop: "10px", color: "#333" }}>
        {file ? <strong>Selected file:</strong> : "No file selected"}
        {file && <span style={{ marginLeft: 8 }}>{file.name}</span>}
      </div>

      <button
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          backgroundColor: "#007bff",
          border: "none",
          color: "white",
          cursor: "pointer",
          borderRadius: "6px",
        }}
        onClick={handleUpload}
        disabled={loading}
      >
        {loading ? "Processing..." : "Upload & Generate"}
      </button>

      <p style={{ marginTop: "15px", color: "#555" }}>{message}</p>
    </div>
  );
}

export default App;
