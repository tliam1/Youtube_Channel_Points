# YouTube Chat Bot - Grub Points System

This bot tracks user activity in your YouTube live streams and rewards viewers with "grub points." The system includes gambling features and will eventually incorporate trading and redemption systems.

# NOT A COMPLETE PROJECT. CODE IS MESSY!

## Features:
- **Grub Points**: Viewers earn points by interacting in live chats. Payout amount and frequency are adjustable.
- **Gambling**: Viewers can gamble their points using chat commands.
- **Trading**: Viewers can donate points to others using chat commands.
- **Redeems**: Viewers can use their points to redeem a specified prize.
- **Planned Features**: Battle system and multi-chatter bets

## Installation Instructions

### Prerequisites:
1. **Python 3.x**: Ensure you have Python installed. You can download it [here](https://www.python.org/downloads/).
2. **pip**: Python package manager (usually included with Python).
3. **MySQL Database**: A MySQL database is required to store user points and other data.
4. **YouTube Data API v3 Key**: You will need a valid YouTube API key. Follow the steps [here](https://developers.google.com/youtube/v3/getting-started) to obtain an API key.

### Steps:

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd youtube-chat-bot
    ```

2. **Install dependencies**:
    In the root directory of the project, install the required libraries:
    ```bash
    pip install -r requirements.txt <--- TODO: I don't have this file created yet!!!!
    ```

3. **Database Setup**:
    - Set up a MySQL database.
    - Run the SQL script provided code to create the necessary tables (or write your own):
    ```sql
    CREATE DATABASE youtube_grub_points;
    USE youtube_grub_points;

    CREATE TABLE gambleinfo (
        userId VARCHAR(255) PRIMARY KEY,
        userName VARCHAR(255),
        grubPoints INT DEFAULT 0
    );
    ```

4. **Configuration**:
    - Make a config file for any credentials + get the client_secret.json from Google Dev Console 
    - Fill in your MySQL credentials inside `your_config.py`:
    ```python
    MYSQL_USER = "your_mysql_username"
    MYSQL_PASSWORD = "your_mysql_password"
    MYSQL_DB = "youtube_grub_points"
    MYSQL_HOST = "localhost"
    ```

### Running the Bot:

1. **Start the Bot**:
    Run the following command:
    ```bash
    python main.py
    ```

2. **Input Live Stream ID**:
    When prompted, input the YouTube live stream ID for the bot to monitor. The ID can be found at the end of the stream's URL.
    ```
       Live stream link: https://www.youtube.com/watch?v=aNd24DSns5
       live stream ID: aNd24DSns5
    ```

4. **Chat Commands**:
    - `!p`: View your current grub points.
    - `!g [amount]`: Gamble a specified number of grub points.
    - `!d @user [amount]`: Donate grub points to another user by their channel handle.
    - `!r [prize (optional)]`: Redeem a prize from the dictionary in rewards.py

## Additional Information:
- Ensure your MySQL server is running and accessible before starting the bot.
- You can modify the delay between API calls and other configurations inside the `main.py` file.
- To avoid reaching YouTube’s API quota limit, caching has been added to reduce redundant calls.
- If you want to increase your quota limits (as I have), you must submit a request form.

### Planned Features:
- Adding a pot for multi-chatter bets.
- Adding more rewards
- Clean up main.py
- Add requirements.txt
- Adding some form of PVP with grub points as a reward
- Anti-spam (global command cooldown)
- For the love of all that is good, write some validation functions 
  
For questions or issues, feel free to reach out!
