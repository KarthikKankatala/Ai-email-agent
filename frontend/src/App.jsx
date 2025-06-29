import React, { useState, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [formData, setFormData] = useState({
    gmail_id: "",
    gmail_password: "",
    recipient_email: "",
    user_prompt: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("");
  const [screenshots, setScreenshots] = useState([]);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [isRealEmail, setIsRealEmail] = useState(false);
  const [emailContent, setEmailContent] = useState(null);
  const [aiGenerated, setAiGenerated] = useState(false);
  const wsRef = useRef(null);
  const sessionIdRef = useRef(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // WebSocket handler for real-time screenshots
  const startScreenshotStream = (session_id) => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsProtocol}://${window.location.host.replace(
      /:\d+$/,
      ":8000"
    )}/ws/screenshots/${session_id}`;
    const ws = new window.WebSocket(wsUrl);
    wsRef.current = ws;
    sessionIdRef.current = session_id;
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setScreenshots((prev) => {
          // Avoid duplicates
          if (prev.some((s) => s.filename === data.filename)) return prev;
          return [...prev, data];
        });
      } catch (e) {
        // Ignore parse errors
      }
    };
    ws.onclose = () => {
      wsRef.current = null;
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus("🤖 AI Agent analyzing your prompt...");
    setMessage("");
    setScreenshots([]);
    setError("");
    setIsDemoMode(false);
    setIsRealEmail(false);
    setEmailContent(null);
    setAiGenerated(false);
    sessionIdRef.current = null;

    try {
      const response = await axios.post("/send-ai-email", formData);
      setStatus(response.data.status);
      setMessage(response.data.message);
      setEmailContent(response.data.email_content);
      setAiGenerated(response.data.ai_generated);
      // Start WebSocket stream if session_id is present
      if (response.data.session_id) {
        startScreenshotStream(response.data.session_id);
      }
      // If screenshots are returned immediately (demo mode), set them
      if (response.data.screenshots && response.data.screenshots.length > 0) {
        setScreenshots(response.data.screenshots);
      }
      // Check if we're in demo mode or real email mode
      if (response.data.status === "demo") {
        setIsDemoMode(true);
        setMessage(
          "🎭 Demo Mode: AI-powered email automation simulation. Showing AI analysis and content generation steps."
        );
      } else if (response.data.status === "success") {
        setIsRealEmail(true);
        setMessage(
          "✅ Real email sent successfully using AI-generated content! Check your Gmail sent folder."
        );
      }
      if (response.data.status === "error") {
        setError(
          "AI automation failed. Please check the screenshots for details."
        );
      }
    } catch (err) {
      console.error("Error:", err);
      if (err.response) {
        setError(
          `Server Error: ${err.response.data.detail || err.response.statusText}`
        );
      } else if (err.request) {
        setError(
          "Network Error: Unable to connect to the server. Please check if the backend is running."
        );
      } else {
        setError(`Error: ${err.message}`);
      }
      setStatus("Error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1>🤖 AI Email Agent v2</h1>
        <p className="subtitle">
          Intelligent Gmail automation with AI-powered content generation
        </p>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label htmlFor="gmail_id">Gmail ID:</label>
            <input
              type="email"
              id="gmail_id"
              name="gmail_id"
              value={formData.gmail_id}
              onChange={handleInputChange}
              required
              placeholder="your.email@gmail.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="gmail_password">Password:</label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                id="gmail_password"
                name="gmail_password"
                value={formData.gmail_password}
                onChange={handleInputChange}
                required
                placeholder="Enter your password"
                className="password-input"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={togglePasswordVisibility}
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "👁️" : "👁️‍🗨️"}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="recipient_email">Send To:</label>
            <input
              type="email"
              id="recipient_email"
              name="recipient_email"
              value={formData.recipient_email}
              onChange={handleInputChange}
              required
              placeholder="recipient@example.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="user_prompt">
              🤖 What would you like to send? (Natural Language):
            </label>
            <textarea
              id="user_prompt"
              name="user_prompt"
              value={formData.user_prompt}
              onChange={handleInputChange}
              rows="3"
              required
              placeholder="e.g., Send internship application to tech company, Write a follow-up email after job interview..."
              className="prompt-input"
            />
            <div className="prompt-examples">
              <small>💡 Examples:</small>
              <div className="example-tags">
                <span
                  className="example-tag"
                  onClick={() =>
                    setFormData((prev) => ({
                      ...prev,
                      user_prompt:
                        "Send internship application to tech company",
                    }))
                  }
                >
                  Send internship application to tech company
                </span>
                <span
                  className="example-tag"
                  onClick={() =>
                    setFormData((prev) => ({
                      ...prev,
                      user_prompt:
                        "Write a follow-up email after job interview",
                    }))
                  }
                >
                  Write a follow-up email after job interview
                </span>
                <span
                  className="example-tag"
                  onClick={() =>
                    setFormData((prev) => ({
                      ...prev,
                      user_prompt: "Send thank you email to client",
                    }))
                  }
                >
                  Send thank you email to client
                </span>
              </div>
            </div>
          </div>

          <button type="submit" disabled={isLoading} className="submit-btn">
            {isLoading
              ? "🤖 AI Agent Working..."
              : "🚀 Send AI-Generated Email"}
          </button>
        </form>

        {status && (
          <div className="status">
            <h3>
              Status: {status}
              {wsRef.current && <span className="live-indicator">🔴 LIVE</span>}
            </h3>
            {message && <p className="message">{message}</p>}
            {error && <p className="error">{error}</p>}

            {/* Progress indicator for live streaming */}
            {wsRef.current && screenshots.length > 0 && (
              <div className="progress-container">
                <h4>🤖 AI Agent Progress</h4>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(
                        (screenshots.length / 10) * 100,
                        100
                      )}%`,
                    }}
                  ></div>
                </div>
                <p>
                  Step {screenshots.length} of ~10:{" "}
                  {screenshots[screenshots.length - 1]?.step
                    ?.replace("_", " ")
                    .toUpperCase()}
                </p>
              </div>
            )}

            {emailContent && (
              <div className="email-content-preview">
                <h4>📧 AI-Generated Email Preview:</h4>
                <div className="email-preview">
                  <div className="email-field">
                    <strong>Subject:</strong> {emailContent.subject}
                  </div>
                  <div className="email-field">
                    <strong>Type:</strong>
                    <span className="status-badge ai">
                      {emailContent.email_type}
                    </span>
                  </div>
                  <div className="email-field">
                    <strong>Tone:</strong> {emailContent.tone}
                  </div>
                  <div className="email-field">
                    <strong>Body:</strong>
                    <div className="email-body-preview">
                      {emailContent.body}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {isDemoMode && (
              <div className="demo-notice">
                <p>
                  🎭 <strong>AI Demo Mode Active:</strong> This is a simulation
                  of the AI-powered automation process. In a production
                  environment with proper setup, you would see actual AI
                  analysis, content generation, and real email sending.
                </p>
              </div>
            )}
            {isRealEmail && (
              <div className="success-notice">
                <p>
                  🎉 <strong>AI-Generated Email Sent!</strong> Your email has
                  been successfully created by AI and sent using Gmail
                  automation. Check your Gmail sent folder to confirm.
                </p>
              </div>
            )}
          </div>
        )}

        {screenshots.length > 0 && (
          <div className="screenshots-section">
            <h3>
              📸 Live Automation Progress
              {wsRef.current && (
                <span className="live-indicator">🔴 STREAMING</span>
              )}
            </h3>
            <div className="screenshots-grid">
              {screenshots.map((screenshot, index) => (
                <div
                  key={index}
                  className={`screenshot-item ${
                    index === screenshots.length - 1 ? "new" : ""
                  }`}
                >
                  <img
                    src={`/screenshots/${screenshot.filename}`}
                    alt={screenshot.description}
                    className="screenshot-image"
                  />
                  <div className="screenshot-info">
                    <h4>
                      Step {index + 1}:{" "}
                      {screenshot.step.replace("_", " ").toUpperCase()}
                      {index === screenshots.length - 1 && (
                        <span className="status-badge success">NEW</span>
                      )}
                    </h4>
                    <p>{screenshot.description}</p>
                    <small>Timestamp: {screenshot.timestamp}</small>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Floating action button for quick actions */}
        {screenshots.length > 0 && (
          <button
            className="fab"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            title="Scroll to top"
          >
            ↑
          </button>
        )}
      </div>
    </div>
  );
}

export default App;
