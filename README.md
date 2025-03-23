Here’s a professional `README.md` file for your Discord bot project. This file provides an overview of the bot, instructions for setting it up, and details about its features.

---

# Discord Bot: F3 xUp and Image Sender

This is a Discord bot designed to manage role assignments (xUp system) and send random images. It includes features like:
- Assigning roles to users.
- Removing users from roles.
- Sending random images from a predefined list.

---

## Table of Contents
1. [Features](#features)
2. [Setup](#setup)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
3. [Usage](#usage)
   - [xUp System](#xup-system)
   - [Random Image Sender](#random-image-sender)
4. [Commands](#commands)
5. [Contributing](#contributing)
6. [License](#license)

---

## Features

- **xUp System**:
  - Users can claim roles by typing `x <role>`.
  - Users can remove themselves from roles by typing `x <role> out`.
  - The bot updates a blame board in real-time to reflect role assignments.

- **Random Image Sender**:
  - The bot can send a random image from a predefined list when triggered by a command.

- **Error Handling**:
  - The bot handles missing files, permission issues, and other errors gracefully.

---

## Setup

### Prerequisites

- Python 3.8 or higher.
- A Discord bot token. You can create a bot and get the token from the [Discord Developer Portal](https://discord.com/developers/applications).
- The `discord.py` library.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Bot Token**:
   - Create a `.env` file in the project root and add your bot token:
     ```
     TOKEN=your-bot-token-here
     ```

### Configuration

- **Image Paths**:
  - Update the `image_paths` list in the bot code with the paths to your images.
  - Example:
    ```python
    image_paths = [
        r"path\to\image1.jpg",
        r"path\to\image2.jpg",
        r"path\to\image3.jpg"
    ]
    ```

- **Role Names**:
  - Update the `tracker` dictionary in the bot code with the roles you want to manage.
  - Example:
    ```python
    tracker = {
        "core": "",
        "exp": "",
        "gold": "",
        "mid": "",
        "roam": ""
    }
    ```

---

## Usage

### xUp System

1. **Start the xUp System**:
   - Type `fml` in the Discord channel to reset the blame board and create a thread for role assignments.

2. **Claim a Role**:
   - Type `x <role>` in the thread to claim a role (e.g., `x core`).

3. **Remove Yourself from a Role**:
   - Type `x <role> out` in the thread to remove yourself from a role (e.g., `x core out`).

### Random Image Sender

- Type `!randomimage` in the Discord channel to send a random image from the predefined list.

---

## Commands

| Command          | Description                              |
|------------------|------------------------------------------|
| `fml`            | Resets the blame board and starts xUp.   |
| `x <role>`       | Claims a role (e.g., `x core`).          |
| `x <role> out`   | Removes yourself from a role.            |
| `!randomimage`    | Sends a random image.                    |

---

## Contributing

Contributions are welcome! Follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support

If you encounter any issues or have questions, feel free to open an issue on GitHub or contact the maintainer.

---

Enjoy using the bot! 🎉
