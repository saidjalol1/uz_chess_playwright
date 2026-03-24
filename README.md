# Flutter App Registration Automation

A Python automation script that uses Playwright to automate Flutter app registration processes with stealth configuration, human-like interactions, and comprehensive error handling.

## Features

- **Email Validation**: Robust email format validation with descriptive error messages
- **Stealth Configuration**: Persistent browser context to avoid automation detection
- **Human-like Interactions**: Random typing delays and realistic user behavior simulation
- **Multi-tab Navigation**: Automatic detection and switching to registration tabs
- **Error Handling**: Comprehensive error capture with screenshot generation
- **Resource Management**: Guaranteed cleanup of browser processes and resources
- **Flexible Input**: Support for both command-line arguments and function parameters

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 2GB RAM (4GB recommended for optimal performance)
- **Storage**: 500MB free space for browser installation and user data
- **Network**: Internet connection for browser downloads and target website access

## Installation

### Step 1: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `playwright>=1.40.0` - Browser automation framework
- `pytest>=7.0.0` - Testing framework  
- `hypothesis>=6.0.0` - Property-based testing library
- `pytest-cov>=4.0.0` - Test coverage reporting
- `pytest-asyncio>=0.21.0` - Async test support

### Step 2: Install Playwright Browsers

```bash
# Install all supported browsers (recommended)
playwright install

# Or install specific browser only
playwright install chromium
```

### Step 3: System Dependencies (Linux Only)

On Linux systems, install additional dependencies:

```bash
# Install system dependencies for Playwright
playwright install-deps

# Or install manually (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

### Step 4: Verify Installation

```bash
# Run tests to verify setup
pytest

# Test basic functionality (will show usage if no email provided)
python main.py
```

## Usage

### Command Line Usage

The script accepts email input through two methods as specified in Requirements 1.3 and 1.4:

```bash
# Method 1: Positional argument
python main.py user@example.com

# Method 2: --email flag  
python main.py --email user@example.com

# Display help and usage information
python main.py --help
```

### Usage Examples

```bash
# Standard email formats
python main.py john.doe@company.com
python main.py test+automation@gmail.com
python main.py user123@subdomain.example.org

# The script validates email format and shows descriptive errors for invalid inputs
python main.py invalid-email        # Shows format error
python main.py                      # Shows usage message (Requirement 1.4)
```

### Programmatic Usage

You can also use the automation as a function parameter (Requirement 1.3):

```python
import asyncio
from main import main

async def run_automation():
    try:
        # Email provided as function parameter
        await main("user@example.com")
        print("Registration completed successfully")
    except Exception as e:
        print(f"Registration failed: {e}")

# Execute the automation
asyncio.run(run_automation())
```

### Exit Codes

The script returns specific exit codes for different scenarios:

- `0`: Success - Registration flow completed successfully
- `1`: Error - Invalid email format or missing email argument  
- `130`: Interrupted - User cancelled with Ctrl+C
- Other: Unexpected errors during execution

## Configuration Options

The script uses a comprehensive configuration system in `config.py`. Key configuration areas:

### Target Website Configuration

```python
# In config.py - Update these for your specific Flutter registration site
target_url = "https://your-flutter-site.com/register"
selectors = {
    "signup_button": "button[data-testid='signup-button']",  # CSS selector for signup button
    "email_input": "input[type='email']"                    # CSS selector for email input
}
```

### Timeout Configuration

```python
timeouts = {
    "page_load": 30000,        # Page load timeout (30 seconds)
    "element_visible": 30000,  # Element visibility timeout (30 seconds) 
    "new_tab": 10000          # New tab detection timeout (10 seconds)
}
```

### Browser Configuration

```python
browser = {
    "headless": False,                    # Run in visible mode (recommended for debugging)
    "user_data_dir": "./browser_data",   # Persistent browser data directory
    "viewport": {"width": 1920, "height": 1080}  # Browser window size
}
```

### Stealth Mode Configuration

```python
stealth = {
    "enabled": True,                     # Enable stealth mode to avoid detection
    "human_like_typing": True,           # Use human-like typing patterns
    "typing_delay_range": (50, 150)     # Random delay between keystrokes (ms)
}
```

### Logging Configuration

```python
logging = {
    "level": "info",                     # Log level: "debug", "info", or "error"
    "screenshot_on_error": True,         # Capture screenshots when errors occur
    "screenshot_dir": "./screenshots"    # Directory for error screenshots
}
```

## Output and Logging

### Console Output

The script provides detailed logging during execution:

```
[2024-01-15 10:30:15] INFO: Initializing browser with stealth configuration
[2024-01-15 10:30:16] INFO: Browser initialized successfully
[2024-01-15 10:30:17] INFO: Navigating to target URL: https://example.com
[2024-01-15 10:30:18] INFO: Navigation completed
[2024-01-15 10:30:19] INFO: Waiting for signup button
[2024-01-15 10:30:20] INFO: Signup button found, clicking
[2024-01-15 10:30:21] INFO: Email input field found, typing email with human-like delays
[2024-01-15 10:30:23] INFO: Email entered successfully
[2024-01-15 10:30:24] INFO: Initializing TabManager and waiting for new tab
[2024-01-15 10:30:25] INFO: New tab detected
[2024-01-15 10:30:26] INFO: Registration flow completed successfully
```

### Error Screenshots

When errors occur, screenshots are automatically captured to help with debugging:

```
screenshots/
├── error_1642248615.png  # Screenshot when error occurred
├── error_1642248620.png  # Another error screenshot  
└── ...
```

### Debug Mode

Enable detailed debug logging by modifying `config.py`:

```python
DEFAULT_CONFIG.logging.level = "debug"
```

Debug mode provides:
- Detailed step-by-step execution information
- Element selector search details
- Timing information for each operation
- Browser interaction specifics

## Project Structure

```
flutter-app-registration-automation/
├── main.py                    # CLI entry point and argument parsing
├── validators.py              # Email validation with regex patterns
├── logger.py                  # Structured logging with timestamps
├── browser_controller.py      # Browser automation with stealth features
├── tab_manager.py            # Tab detection and management
├── automation_flow.py        # Flow orchestration and error handling
├── config.py                 # Configuration dataclasses and defaults
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── .gitignore               # Git ignore patterns
├── screenshots/             # Error screenshots (auto-created)
├── browser_data/            # Persistent browser data (auto-created)
└── tests/                   # Test files
    ├── test_validators.py           # Email validation tests
    ├── test_logger.py              # Logger functionality tests
    ├── test_browser_controller.py  # Browser controller tests
    ├── test_tab_manager.py         # Tab manager tests
    ├── test_automation_flow.py     # Flow orchestration tests
    ├── test_main.py               # CLI entry point tests
    └── test_property_*.py         # Property-based tests
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Browser Launch Failures

**Symptoms**: Script fails with browser initialization errors

**Solutions**:
- Verify Playwright installation: `playwright install`
- Check Python version: `python --version` (must be 3.8+)
- Ensure sufficient disk space (500MB+)
- On Linux: Install system dependencies with `playwright install-deps`

#### 2. Element Not Found Errors

**Symptoms**: Script cannot find signup button or email input field

**Solutions**:
- Update selectors in `config.py` to match your target website
- Use browser developer tools (F12) to inspect elements and find correct selectors
- Check screenshots in `screenshots/` directory to see page state during error
- Enable debug logging to see detailed element search information
- Verify the target website structure hasn't changed

#### 3. Timeout Issues

**Symptoms**: Script times out waiting for elements or page loads

**Solutions**:
- Increase timeout values in `config.py` for slow networks
- Verify target website is accessible from your network
- Check if website is blocking your IP or user agent
- Run with `headless=False` to visually observe what's happening
- Test with a simple, known-working website first

#### 4. Email Validation Errors

**Symptoms**: Script rejects valid email addresses

**Solutions**:
- Ensure email follows standard format: `user@domain.com`
- Check for extra spaces or special characters
- Verify email contains exactly one @ symbol
- Test with simple format first: `test@example.com`

#### 5. Permission and File System Errors

**Symptoms**: Cannot create directories or save screenshots

**Solutions**:
- Ensure write permissions for current directory
- Check available disk space
- Run from a directory with write access
- Verify `screenshots/` and `browser_data/` can be created

#### 6. Stealth Detection Issues

**Symptoms**: Website detects automation and blocks the script

**Solutions**:
- Ensure stealth mode is enabled in configuration (default: enabled)
- Use persistent user data directory (already configured)
- Avoid running multiple instances simultaneously
- Add longer delays between actions if needed
- Try different browser settings or user agents

#### 7. Network Connectivity Problems

**Symptoms**: Pages fail to load or navigation times out

**Solutions**:
- Check internet connection stability
- Verify target URL works in regular browser
- Check for proxy or firewall restrictions
- Increase page load timeout values
- Test with different network connection

### Advanced Troubleshooting

#### Enable Debug Logging

For detailed troubleshooting information:

```python
# In config.py
DEFAULT_CONFIG.logging.level = "debug"
```

#### Manual Testing

Test individual components:

```bash
# Test email validation only
python -c "from validators import validate_email; print(validate_email('test@example.com'))"

# Run specific test modules
pytest test_validators.py -v
pytest test_browser_controller.py -v
```

#### Screenshot Analysis

When errors occur:
1. Check `screenshots/` directory for error screenshots
2. Compare with expected page appearance
3. Look for missing elements or unexpected page states
4. Update selectors based on actual page structure

### Getting Additional Help

If issues persist:

1. **Review Error Screenshots**: Check `screenshots/` for visual debugging
2. **Enable Debug Logging**: Set logging level to "debug" for detailed information  
3. **Check Configuration**: Verify selectors match your target website structure
4. **Test Incrementally**: Start with simple websites to isolate issues
5. **Review Console Output**: Look for specific error messages and context

## Development and Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -k "property"        # Property-based tests only
pytest -k "unit"           # Unit tests only
pytest test_validators.py  # Specific module tests
```

### Test Coverage

The project maintains comprehensive test coverage:
- **Unit Tests**: Specific examples and edge cases
- **Property-Based Tests**: Universal correctness properties using Hypothesis
- **Integration Tests**: End-to-end flow validation
- **Error Handling Tests**: All error paths and cleanup scenarios

### Code Quality

The codebase follows Python best practices:
- Type hints for all function signatures
- Comprehensive error handling with context
- Modular architecture with clear separation of concerns
- Detailed logging for debugging and monitoring
- Resource cleanup guarantees using try-finally blocks

## License

This project is provided for educational and automation purposes. Please ensure compliance with the terms of service of any websites you automate.
