# AI Email Agent

A full-stack web application that automates Gmail email sending using browser automation with Selenium. The application provides a modern React frontend and FastAPI backend with real-time screenshot capture of the automation process.

## Features

- 🤖 **Automated Email Sending**: Automatically logs into Gmail and sends emails
- 📸 **Real-time Screenshots**: Captures screenshots at each step of the automation process
- 🎨 **Modern UI**: Clean React frontend with real-time status updates
- 🔄 **Live Updates**: Frontend updates in real-time as automation progresses
- 🛡️ **Error Handling**: Robust error handling with fallback to demo mode
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
ai-email-agent/
├── main.py                     # FastAPI backend server
├── email_agent_selenium.py     # Selenium-based email automation
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── screenshots/                # Screenshot storage directory
│   └── .gitkeep               # Keeps directory in git
└── frontend/                   # React frontend
    ├── src/
    │   ├── App.jsx            # Main React component
    │   ├── App.css            # Component styles
    │   ├── main.jsx           # React entry point
    │   └── index.css          # Global styles
    ├── package.json           # Node.js dependencies
    ├── vite.config.js         # Vite configuration
    └── index.html             # HTML template
```

## Technology Stack

### Backend

- **FastAPI**: Modern Python web framework
- **Selenium**: Browser automation for Gmail interaction
- **Uvicorn**: ASGI server for running FastAPI
- **WebDriver Manager**: Automatic ChromeDriver management

### Frontend

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API communication
- **CSS3**: Modern styling with responsive design

## Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- Google Chrome browser
- Gmail account

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/KarthikKankatala/Ai-email-agent.git
   cd ai-email-agent
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python main.py
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**

   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173` (or next available port)

## Usage

1. **Open the application**

   - Navigate to `http://localhost:5173` in your browser

2. **Fill in the form**

   - **Gmail ID**: Your Gmail email address
   - **Gmail Password**: Your Gmail password (or app password)
   - **Recipient Email**: The email address to send to
   - **Subject**: Email subject line
   - **Body**: Email body content

3. **Send Email**
   - Click the "Send Email" button
   - Watch the real-time progress with screenshots
   - The automation will:
     - Navigate to Gmail
     - Log in with your credentials
     - Click compose
     - Fill in recipient, subject, and body
     - Send the email
     - Capture screenshots at each step

## API Endpoints

- `GET /`: Health check
- `GET /health`: Detailed health status
- `GET /test`: Test endpoint
- `POST /send-email`: Send email with automation
- `GET /screenshots/{session_id}/{filename}`: Access screenshots

## Security Considerations

⚠️ **Important Security Notes**:

1. **Password Storage**: This application does not store passwords. They are only used temporarily during the automation process.

2. **Gmail Security**:

   - Consider using Gmail App Passwords instead of your main password
   - Enable 2-factor authentication on your Gmail account
   - Be aware that automated login may trigger security alerts

3. **Network Security**:

   - The application runs on localhost by default
   - Do not expose this application to the internet without proper security measures

4. **Browser Automation**:
   - The application uses Selenium for browser automation
   - This may be detected by Gmail's security systems
   - Consider using Gmail API for production use

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**

   - Make sure Google Chrome is installed
   - The application will automatically download the correct ChromeDriver version
   - If issues persist, try updating Chrome to the latest version

2. **Gmail Login Issues**

   - Ensure your Gmail credentials are correct
   - Check if 2-factor authentication is enabled (use app password)
   - Gmail may block automated login attempts

3. **Port Conflicts**

   - Backend runs on port 8000 by default
   - Frontend runs on port 5173 by default
   - If ports are in use, the application will try the next available port

4. **Selenium Errors**
   - Check if Chrome is installed and up to date
   - Ensure no antivirus is blocking ChromeDriver
   - Try running as administrator if on Windows

### Demo Mode

If Selenium automation fails, the application will automatically fall back to demo mode, which shows simulated screenshots of the automation process. This is useful for testing the frontend without actual Gmail credentials.

## Development

### Adding New Features

1. **Backend**: Modify `main.py` and `email_agent_selenium.py`
2. **Frontend**: Modify files in `frontend/src/`
3. **Styling**: Update CSS files in `frontend/src/`

### Testing

- Backend API: Use the `/test` endpoint
- Frontend: The application includes real-time status updates
- Screenshots: Check the `screenshots/` directory for captured images

## License

This project is created for educational and demonstration purposes. Please ensure compliance with Gmail's terms of service and applicable laws when using this application.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs in the terminal
3. Check the browser console for frontend errors
4. Ensure all dependencies are properly installed

---

**Note**: This application is designed for educational purposes and demonstrates browser automation techniques. For production use, consider using the official Gmail API for better security and reliability.
