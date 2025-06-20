// src/components/JDResults.jsx
import React from "react";
import { Bar } from "react-chartjs-2";
import Chart from 'chart.js/auto';

const JDResults = ({ results, onSendMail }) => {
  const chartData = {
    labels: ["Eligible", "Partially Eligible", "Not Eligible"],
    datasets: [
      {
        label: "Students",
        backgroundColor: ["#28a745", "#ffc107", "#dc3545"],
        data: [
          results.eligibility_results?.filter(r => r.status === "eligible").length || 0,
          results.eligibility_results?.filter(r => r.status === "partially_eligible").length || 0,
          results.eligibility_results?.filter(r => r.status === "not_eligible").length || 0,
        ]
      }
    ]
  };

  return (
    <div className="results-box">
      <div className="section">
        <h2>🧾 JD Criteria</h2>
        <pre>{results.jd_criteria?.content || "No JD content found"}</pre>
      </div>

      <div className="section">
        <h2>📊 Eligibility Results</h2>
        <Bar data={chartData} />
        <ul>
          {results.eligibility_results?.map((r, i) => (
            <li key={i}>
              <b>{r.student_id}</b> - {r.status}
              {r.reasons?.length > 0 && (
                <ul>
                  {r.reasons.map((reason, j) => (
                    <li key={j} className="reason">{reason}</li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </div>

      <div className="section">
        <h2>📉 Gap Analysis</h2>
        <ul>
          {results.gap_analysis?.map((g, i) => (
            <li key={i}>
              <b>{g.student_id}</b> - Missing: {g.gaps.join(", ")}
            </li>
          ))}
        </ul>
      </div>

      <div className="section">
        <h2>📚 Training Plan</h2>
        <ul>
          {results.training_recommendations?.map((t, i) => (
            <li key={i}>
              <b>{t.student_id}</b>
              <pre>{t.training_plan}</pre>
            </li>
          ))}
        </ul>
      </div>

      <div className="section">
        <h2>📬 Notification Summary</h2>
        <ul>
          {results.notification_summary?.map((msg, i) => (
            <li key={i}>
              <b>{msg.student_id}</b> - {msg.status} → {msg.message}
              <button onClick={() => onSendMail(msg.student_id)} className="send-btn">
                Send Mail
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default JDResults;
