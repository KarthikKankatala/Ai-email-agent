import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [formData, setFormData] = useState({
    gmail_id: "",
    gmail_password: "",
    recipient_email: "",
    subject: "",
    body: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("");
  const [screenshots, setScreenshots] = useState([]);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [isRealEmail, setIsRealEmail] = useState(false);

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus("Starting automation...");
    setMessage("");
    setScreenshots([]);
    setError("");
    setIsDemoMode(false);
    setIsRealEmail(false);

    try {
      const response = await axios.post("/send-email", formData);
      setStatus(response.data.status);
      setMessage(response.data.message);
      setScreenshots(response.data.screenshots);

      // Check if we're in demo mode or real email mode
      if (response.data.status === "demo") {
        setIsDemoMode(true);
        setMessage(
          "Demo mode: Selenium automation not available. Showing simulated screenshots."
        );
      } else if (response.data.status === "success") {
        setIsRealEmail(true);
        setMessage(
          "✅ Real email sent successfully! Check your Gmail sent folder."
        );
      }

      if (response.data.status === "error") {
        setError(
          "Automation failed. Please check the screenshots for details."
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
        <h1>🤖 AI Email Agent</h1>
        <p className="subtitle">
          Automate Gmail email sending with step-by-step screenshots
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
            <label htmlFor="subject">Subject:</label>
            <input
              type="text"
              id="subject"
              name="subject"
              value={formData.subject}
              onChange={handleInputChange}
              placeholder="Email subject"
            />
          </div>

          <div className="form-group">
            <label htmlFor="body">Message:</label>
            <textarea
              id="body"
              name="body"
              value={formData.body}
              onChange={handleInputChange}
              rows="4"
              placeholder="Email message body"
            />
          </div>

          <button type="submit" disabled={isLoading} className="submit-btn">
            {isLoading ? "Sending..." : "Send Email"}
          </button>
        </form>

        {status && (
          <div className="status">
            <h3>Status: {status}</h3>
            {message && <p className="message">{message}</p>}
            {error && <p className="error">{error}</p>}
            {isDemoMode && (
              <div className="demo-notice">
                <p>
                  🎭 <strong>Demo Mode Active:</strong> This is a simulation of
                  the automation process. In a production environment with
                  proper Selenium setup, you would see actual browser
                  screenshots and send real emails.
                </p>
              </div>
            )}
            {isRealEmail && (
              <div className="success-notice">
                <p>
                  🎉 <strong>Real Email Sent!</strong> Your email has been
                  successfully sent using Gmail automation. Check your Gmail
                  sent folder to confirm.
                </p>
              </div>
            )}
          </div>
        )}

        {screenshots.length > 0 && (
          <div className="screenshots">
            <h3>Automation Screenshots:</h3>
            <div className="screenshot-grid">
              {screenshots.map((screenshot, index) => (
                <div key={index} className="screenshot-item">
                  <h4>Step {index + 1}</h4>
                  <img
                    src={screenshot}
                    alt={`Step ${index + 1}`}
                    className="screenshot"
                    onError={(e) => {
                      e.target.style.display = "none";
                      e.target.nextSibling.style.display = "block";
                    }}
                  />
                  <div className="screenshot-error" style={{ display: "none" }}>
                    <p>Screenshot not available</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
