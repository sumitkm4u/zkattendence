# Attendance System

This project is a simple attendance system using PHP for user login and session management, and Python for handling attendance logs from a device.

## Project Structure


## PHP Scripts

### Login Script (`login.php`)
Handles user login and sets session variables.

### Dashboard Script (`dashboard.php`)
Displays the logged-in user's details.

### Logout Script (`logout.php`)
Logs the user out by destroying the session.

## Python Script

### Attendance Script (`attendance.py`)
Fetches attendance logs from a device, processes them, and sends them to a server.

## Usage

1. **PHP**:
   - Start a local server in the `php` directory.
   - Access the login page via `login.php`.
   - After logging in, you will be redirected to the `dashboard.php`.

2. **Python**:
   - Ensure you have the necessary libraries installed (`zk`, `requests`, `pyttsx3`).
   - Run the script `attendance.py` to process attendance logs.

## Requirements

- PHP 7.x or higher
- Python 3.x
- Necessary Python libraries: `zk`, `requests`, `pyttsx3`

## Installation

### PHP

Ensure you have a local server set up (e.g., XAMPP, WAMP) and place the `php` directory in the server's root directory.

### Python

Install the necessary libraries using `pip`:
```sh
pip install pyzk requests pyttsx3
