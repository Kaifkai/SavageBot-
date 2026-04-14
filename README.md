#  cafevibe SavageBot

> A savage but respectful Discord bot with AI chat, moderation, and fun/games commands. Created by **kaifuddin**.

---

##  Features

###  Moderation
| Command | Description |
|--------|-------------|
| `!kick @user [reason]` | Kick a member |
| `!ban @user [reason]` | Ban a member |
| `!unban Username` | Unban a member |
| `!mute @user [reason]` | Mute a member |
| `!unmute @user` | Unmute a member |
| `!clear [amount]` | Delete messages (max 100) |  
###  Fun & Games
| Command | Description |
|--------|-------------|
| `!roll [NdN]` | Roll dice |
| `!coinflip` | Flip a coin |
| `!8ball <question>` | Ask the magic 8-ball |
| `!rps <rock/paper/scissors>` | Play rock paper scissors |
| `!trivia` | Start a trivia question |
| `!roast [@user]` | Roast someone |

###  AI Chat
| Command | Description |
|--------|-------------|
| `!chat <message>` | Chat with the savage AI |

###  Welcome System
| Command | Description |
|--------|-------------|
| `!setwelcome #channel` | Set welcome channel (admin only) |
| `!welcometest` | Test the welcome message |

---

##  Setup

### 1. Clone the repository
```bash
git clone https://github.com/Kaifkai/SavageBot-.git
cd SavageBot-
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your .env file
```bash
DISCORD_TOKEN=your_discord_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the bot
```bash
python3 bot.py
```

---

##  Getting API Keys

- **Discord Token** → https://discord.com/developers/applications
- **Gemini API Key** → https://console.google.com (free)
- **Groq API Key** → https://console.groq.com (free)

---

##  AI Fallback System
The bot uses a smart fallback system:
1. Tries **Gemini** first
2. If Gemini fails → switches to **Groq** automatically
3. If both fail → sends an error message

This means the bot almost never goes down! 🔥

---

## 📝 License
Made by **kaifuddin**
