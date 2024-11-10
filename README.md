# Laser Tag Game Management Bot

[![Maintainability](https://api.codeclimate.com/v1/badges/21949f746d0145bd3f6e/maintainability)](https://codeclimate.com/github/SvamiBog/LasertagWarszaw/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/21949f746d0145bd3f6e/test_coverage)](https://codeclimate.com/github/SvamiBog/LasertagWarszaw/test_coverage)

Welcome to the **Laser Tag Game Management Bot** project! This comprehensive platform is designed to streamline the management of laser tag games, allowing administrators and players to interact seamlessly. Built with Django and Python, the platform integrates with Telegram to provide real-time notifications and game updates. This README will walk you through the purpose, key features, installation, and usage of the project.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [Contributions](#contributions)
- [License](#license)

## Overview

The **Laser Tag Game Management Bot** is an interactive platform for managing laser tag events. It provides administrators with the ability to create and oversee games while players can join and track game details through notifications. This system ensures a smooth experience for all participants by automating essential administrative tasks and delivering real-time status updates.

## Features

### For Administrators:
- **Game Creation and Management**: Administrators can create, edit, and delete games through a user-friendly web interface.
- **Automatic Status Updates**: The system determines the game status dynamically based on the current time and the scheduled start time.
- **Player List Management**: View lists of registered players and manage participant information.
- **Telegram Integration**: Send notifications and updates to players about upcoming games or game status changes.
- **Secure Authentication**: Login and logout functionality to ensure only authorized personnel can access administrative features.

### For Players:
- **Real-Time Notifications**: Receive game updates and reminders via Telegram.
- **Easy Registration**: Sign up for games through the bot and stay informed about upcoming events.
- **Game Status Information**: View game details, including date, time, and status (upcoming, ongoing, or completed).

## Technology Stack

The project is built using the following technologies:

- **Python 3.12**: The core programming language.
- **Django 5.1**: A powerful web framework for developing the backend.
- **Bootstrap 5**: Used for creating responsive and modern user interfaces.
- **pytz**: For handling timezone conversions to ensure accurate status updates.
- **Telegram Bot API**: Facilitates player notifications and game management through Telegram.
- **SQLite**: The default database used for development (can be switched to PostgreSQL or other databases for production).

## Installation

Follow these steps to set up the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/laser-tag-bot.git
   cd laser-tag-bot
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies using Poetry**:
   ```bash
   poetry install
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add your environment variables, such as database URL and Telegram bot token.

5. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Run the development server**:
   ```bash
   make run
   ```

## Usage

### Administrator Panel
Administrators can access the game management interface at `/games/`. This section includes features for creating, updating, and viewing games. The status of each game is determined automatically based on the current time and is displayed in the list and detail views.

### Player Interaction
Players can register for games through the integrated Telegram bot. The bot sends reminders and updates about game status, ensuring that players are informed and prepared.

### Game Status Logic
The game status is computed in real-time:
- **Upcoming**: The game has not yet started.
- **Ongoing**: The game is currently happening (automatically determined for a 2-hour duration).
- **Completed**: The game has ended.

This logic ensures that the status is always accurate without manual updates.

## Future Improvements

- **Enhanced User Dashboard**: Include player statistics and historical data about past games.
- **Advanced Analytics**: Provide insights into game attendance and popular game times.
- **Integration with Other Communication Platforms**: Expand to support SMS or email notifications.
- **Improved Security**: Implement more robust authentication options and audit trails.

## Contributions

We welcome contributions to improve this project! If you have ideas or encounter issues, please open an issue or submit a pull request.

### How to Contribute
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your commit message"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request on GitHub.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.