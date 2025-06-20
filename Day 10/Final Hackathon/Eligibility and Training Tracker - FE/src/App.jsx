import { useState } from "react";
import axios from "axios";
import { marked } from "marked";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a JD file");

    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    setResults(null);

    try {
      const res = await axios.post("http://localhost:8000/process-jd/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = res.data ?? {};
      data.notification_summary = Array.isArray(data.notification_summary)
        ? data.notification_summary
        : [];

      setResults(data);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }

    setLoading(false);
  };

const getEligibilityChartData = () => {
  const resultsList = results.eligibility_results || [];

  const eligible = resultsList.filter((r) => r.status === "eligible").length;
  const partially = resultsList.filter((r) => r.status === "partially_eligible").length;
  const notEligible = resultsList.filter((r) => r.status === "not_eligible").length;

  return {
    labels: ["Eligible", "Partially Eligible", "Not Eligible"],
    datasets: [
      {
        data: [eligible, partially, notEligible],
        backgroundColor: ["#10B981", "#FBBF24", "#EF4444"], // green, orange, red
      },
    ],
  };
};


  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>🎯 Eligibility & Training Tracker</h1>

        <div style={styles.uploadSection}>
          <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileChange} />
          <button style={styles.uploadButton} onClick={handleUpload} disabled={loading}>
            {loading ? "Processing..." : "Upload JD"}
          </button>
        </div>

        {results && (
          <div style={styles.resultsSection}>
            {/* Pie Chart */}
            <div style={{ width: "250px", margin: "0 auto", marginBottom: "2rem" }}>
              <Pie data={getEligibilityChartData()} />
            </div>

            {/* JDParser */}
            <section>
              <h2 style={styles.sectionTitle}>🧾 JD Criteria</h2>
              <pre style={styles.preBlock}>
                {results.jd_criteria?.content || "No JD content found"}
              </pre>
            </section>

            {/* EligibilityMapper */}
            <section>
              <h2 style={styles.sectionTitle}>✅ Eligibility Results</h2>
              <ul>
                {results.eligibility_results?.map((r, i) => (
                  <li key={i}>
                    <b>{r.student_id}</b> - {r.status}
                    {r.reasons?.length > 0 && (
                      <ul style={styles.reasonList}>
                        {r.reasons.map((reason, j) => (
                          <li key={j}>{reason}</li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            </section>

            {/* GapAnalyzer */}
            <section>
              <h2 style={styles.sectionTitle}>📉 Gap Analysis</h2>
              <ul>
                {results.gap_analysis?.map((gap, i) => (
                  <li key={i}>
                    <b>{gap.student_id}</b> - Missing: {gap.gaps.join(", ")}
                  </li>
                ))}
              </ul>
            </section>

            {/* TrainingRecommender */}
            <section>
              <h2 style={styles.sectionTitle}>📚 Training Plan</h2>
              <ul>
                {results.training_recommendations?.map((rec, i) => (
                  <li key={i}>
                    <b>{rec.student_id}</b>
                    <div
                      style={styles.markdownBox}
                      dangerouslySetInnerHTML={{
                        __html: marked.parse(rec.training_plan || "No plan found."),
                      }}
                    />
                  </li>
                ))}
              </ul>
            </section>

            {/* Notifier */}
            <section>
              <h2 style={styles.sectionTitle}>📬 Notification Summary</h2>
              <ul>
                {results.notification_summary?.map((msg, i) => (
                  <li key={i}>
                    <b>{msg.student_id}</b> - {msg.status} → {msg.message}
                  </li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

// ✅ Styles for dark theme + centered layout
const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#111827", // black/gray
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "2rem",
    color: "white",
    width: "100%",
  },
  card: {
    backgroundColor: "#1F2937", // dark card
    borderRadius: "12px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.3)",
    padding: "2rem",
    width: "100%",
    maxWidth: "900px",
  },
  title: {
    fontSize: "2rem",
    fontWeight: "bold",
    color: "#3B82F6", // blue
    marginBottom: "1.5rem",
    textAlign: "center",
  },
  uploadSection: {
    display: "flex",
    gap: "1rem",
    marginBottom: "1.5rem",
    justifyContent: "center",
    alignItems: "center",
    flexWrap: "wrap",
  },
  uploadButton: {
    backgroundColor: "#3B82F6",
    color: "white",
    padding: "10px 20px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  resultsSection: {
    marginTop: "2rem",
  },
  sectionTitle: {
    fontSize: "1.2rem",
    fontWeight: "bold",
    margin: "1.5rem 0 0.5rem",
    color: "#F9FAFB",
  },
  preBlock: {
    backgroundColor: "#374151", // dark gray
    padding: "1rem",
    borderRadius: "8px",
    overflowX: "auto",
    whiteSpace: "pre-wrap",
  },
  reasonList: {
    color: "#F87171", // red
    marginLeft: "1rem",
  },
  markdownBox: {
    backgroundColor: "#4B5563",
    padding: "1rem",
    marginTop: "0.5rem",
    borderRadius: "8px",
  },
};
