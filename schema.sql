-- Drop tables if they exist
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS chats;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

-- Create settings table
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- settings profile id
    user_id INTEGER NOT NULL, -- user who the settings profile belongs to
    default_theme TEXT NOT NULL DEFAULT 'light', -- theme automatically set on login
    default_model TEXT NOT NULL DEFAULT 'openai/gpt-oss-120b', -- default model for chat creation
    default_sys_prompt TEXT, -- default system prompt for generic chat creation
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create chats table
CREATE TABLE chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL, -- owner/creator of the custom bot
    name TEXT NOT NULL, -- name of the custom bot (i.e. "SQLBot", "PythonHelper", etc.)
    model TEXT NOT NULL, -- model to use for the bot (i.e. "gpt-3.5-turbo", "gpt-4", etc.)
    sys_prompt TEXT, -- instructions for the bot's behavior/specialization
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    sender TEXT NOT NULL, -- "user" or "bot"
    content TEXT NOT NULL, -- text content of the message
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, -- timestamp of when the message was sent
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);