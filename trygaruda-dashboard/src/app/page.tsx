import React from "react";

export default function Dashboard() {
  return (
    <>
      <header className="header">
        <h1>Your Agents</h1>
        <button className="btn-primary">+ Create Agent</button>
      </header>

      <div className="grid">
        {/* Agent Card 1 */}
        <div className="agent-card glass">
          <div className="pulse"></div>
          <h3>Inbound Support Rep</h3>
          <p>Answers customer FAQs, books appointments, and routes complex queries to human staff.</p>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span className="tag">Inbound</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>+91 80 1234 5678</span>
          </div>
        </div>

        {/* Agent Card 2 */}
        <div className="agent-card glass">
          <div className="pulse" style={{ background: "var(--text-muted)", boxShadow: "none", animation: "none" }}></div>
          <h3>Outbound SDR</h3>
          <p>Qualifies leads from website signups and schedules demos using Google Calendar.</p>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span className="tag">Outbound</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Offline</span>
          </div>
        </div>
      </div>

      <h2 style={{ marginTop: "48px", marginBottom: "16px", fontSize: "1.5rem" }}>Recent Call Logs</h2>
      
      <div className="glass table-container">
        <table>
          <thead>
            <tr>
              <th>Date & Time</th>
              <th>Agent</th>
              <th>Direction</th>
              <th>Duration</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Sep 16, 2026 - 10:30 AM</td>
              <td>Inbound Support Rep</td>
              <td>Inbound</td>
              <td>3m 45s</td>
              <td className="status-success">Completed</td>
            </tr>
            <tr>
              <td>Sep 16, 2026 - 09:15 AM</td>
              <td>Outbound SDR</td>
              <td>Outbound</td>
              <td>1m 12s</td>
              <td className="status-success">Completed</td>
            </tr>
            <tr>
              <td>Sep 15, 2026 - 04:20 PM</td>
              <td>Outbound SDR</td>
              <td>Outbound</td>
              <td>0m 45s</td>
              <td className="status-failed">Voicemail</td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  );
}
