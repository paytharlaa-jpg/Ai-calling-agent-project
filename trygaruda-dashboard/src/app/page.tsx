"use client";

import React, { useState, useEffect } from "react";

// The API URL will default to localhost:8000 for local testing, 
// but in Vercel it should be set via environment variable NEXT_PUBLIC_API_URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const USER_ID = 1; // Hardcoded user for this demo

export default function Dashboard() {
  const [agents, setAgents] = useState<any[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCallModalOpen, setIsCallModalOpen] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);

  // Form states
  const [newAgent, setNewAgent] = useState({ name: "", system_prompt: "", voice_id: "a0e99841-438c-4a64-b679-ae501e7d6091", webhook_url: "" });
  const [phoneNumber, setPhoneNumber] = useState("");
  const [callStatus, setCallStatus] = useState("");

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API_URL}/users/${USER_ID}/agents/`);
      if (res.ok) {
        const data = await res.json();
        setAgents(data);
      }
    } catch (err) {
      console.error("Failed to fetch agents", err);
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/users/${USER_ID}/agents/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newAgent,
          tools: [] // Default empty tools
        })
      });
      if (res.ok) {
        setIsCreateModalOpen(false);
        setNewAgent({ name: "", system_prompt: "", voice_id: "a0e99841-438c-4a64-b679-ae501e7d6091", webhook_url: "" });
        fetchAgents();
      }
    } catch (err) {
      console.error("Failed to create agent", err);
    }
  };

  const handleMakeCall = async (e: React.FormEvent) => {
    e.preventDefault();
    setCallStatus("Calling...");
    try {
      const res = await fetch(`${API_URL}/agents/${selectedAgentId}/calls/outbound?phone_number=${encodeURIComponent(phoneNumber)}`, {
        method: "POST"
      });
      if (res.ok) {
        setCallStatus("Call queued successfully!");
        setTimeout(() => {
          setIsCallModalOpen(false);
          setCallStatus("");
          setPhoneNumber("");
        }, 2000);
      } else {
        setCallStatus("Failed to make call.");
      }
    } catch (err) {
      setCallStatus("Error connecting to API.");
    }
  };

  return (
    <>
      <header className="header">
        <h1>Your Agents</h1>
        <button className="btn-primary" onClick={() => setIsCreateModalOpen(true)}>+ Create Agent</button>
      </header>

      <div className="grid">
        {agents.length === 0 && (
          <div className="glass" style={{ padding: "2rem", textAlign: "center", gridColumn: "1 / -1" }}>
            <p>You haven't trained any agents yet. Click "Create Agent" to start!</p>
          </div>
        )}
        
        {agents.map((agent) => (
          <div key={agent.id} className="agent-card glass">
            <div className="pulse"></div>
            <h3>{agent.name}</h3>
            <p style={{ maxHeight: "60px", overflow: "hidden", textOverflow: "ellipsis", display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical" }}>
              {agent.system_prompt}
            </p>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginTop: "16px", justifyContent: "space-between" }}>
              <span className="tag">Voice: {agent.voice_id.substring(0,6)}...</span>
              <button 
                className="btn-primary" 
                style={{ padding: "6px 12px", fontSize: "0.8rem" }}
                onClick={() => { setSelectedAgentId(agent.id); setIsCallModalOpen(true); }}
              >
                Call
              </button>
            </div>
          </div>
        ))}
      </div>

      <h2 style={{ marginTop: "48px", marginBottom: "16px", fontSize: "1.5rem" }}>Recent Call Logs</h2>
      
      <div className="glass table-container">
        <table>
          <thead>
            <tr>
              <th>Date & Time</th>
              <th>Agent</th>
              <th>Direction</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={4} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                Connect your webhook URL to see live call logs appear here!
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* CREATE AGENT MODAL */}
      {isCreateModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content glass">
            <h2>Train New Agent</h2>
            <form onSubmit={handleCreateAgent} style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "24px" }}>
              <div>
                <label>Agent Name</label>
                <input 
                  required
                  value={newAgent.name} 
                  onChange={e => setNewAgent({...newAgent, name: e.target.value})} 
                  placeholder="e.g. Sales Rep" 
                />
              </div>
              <div>
                <label>System Prompt (Instructions)</label>
                <textarea 
                  required
                  value={newAgent.system_prompt} 
                  onChange={e => setNewAgent({...newAgent, system_prompt: e.target.value})} 
                  placeholder="You are a helpful sales agent for TryGaruda..."
                  rows={4}
                />
              </div>
              <div>
                <label>Voice ID (Cartesia)</label>
                <input 
                  required
                  value={newAgent.voice_id} 
                  onChange={e => setNewAgent({...newAgent, voice_id: e.target.value})} 
                />
              </div>
              <div>
                <label>Webhook URL (Optional)</label>
                <input 
                  value={newAgent.webhook_url} 
                  onChange={e => setNewAgent({...newAgent, webhook_url: e.target.value})} 
                  placeholder="https://yourserver.com/webhook" 
                />
              </div>
              <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "16px" }}>
                <button type="button" onClick={() => setIsCreateModalOpen(false)} style={{ background: "transparent", color: "var(--text-muted)", border: "none", cursor: "pointer", fontSize: "1rem" }}>Cancel</button>
                <button type="submit" className="btn-primary">Create Agent</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MAKE CALL MODAL */}
      {isCallModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content glass">
            <h2>Make Outbound Call</h2>
            <p style={{ color: "var(--text-muted)", marginBottom: "24px" }}>Enter the phone number you want this agent to call.</p>
            <form onSubmit={handleMakeCall} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <label>Phone Number</label>
                <input 
                  required
                  value={phoneNumber} 
                  onChange={e => setPhoneNumber(e.target.value)} 
                  placeholder="+15551234567" 
                />
              </div>
              
              {callStatus && <p style={{ color: "var(--accent)", fontWeight: "bold" }}>{callStatus}</p>}
              
              <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "16px" }}>
                <button type="button" onClick={() => { setIsCallModalOpen(false); setCallStatus(""); }} style={{ background: "transparent", color: "var(--text-muted)", border: "none", cursor: "pointer", fontSize: "1rem" }}>Cancel</button>
                <button type="submit" className="btn-primary">Call Now</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
