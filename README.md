# ModDB Anomaly Add-on Notifier

## 📜 Description

**ModDB Anomaly Add-on Notifier** is a Python script that checks for new add-ons on ModDB add-ons for a specific mod and sends webhook messages. It's perfect for staying informed without needing to check ModDB manually.

## ✨ Features

* Monitors add-ons on ModDB for a selected mod
* Sends customizable webhook messages
* Runs periodically via scheduler
* Easy to configure via `config.toml` and `message.json`

## 🛠️ Setup

1. **Clone the Repository**

```bash
git clone https://github.com/Tosox/anomaly-addon-notifier.git
cd anomaly-addon-notifier
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Create Config Files**

* `config.toml`: stores webhook urls, scheduler settings, and the RSS feed url
* `message.json`: the message body (supports $title, $description, $timestamp, $url, $image_url)

## 📁 `config.toml` Configuration

Before running the script, you must create a `config.toml` file. There is a `config-example.toml` provided which you can copy and edit.

### ⌚ Script Schedule (`[schedule]`)

This is used to define the schedule on when the script should run.

```toml
[schedule]
interval = 60  # Interval in minutes
```

### 🔔 Webhook Settings (`[webhook]`)

A list of Discord webhook URLs that should receive notifications when a new add-on is published.

```toml
[webhook]
urls = [
  "https://discord.com/api/webhooks/1234567890123456789/yourwebhooktoken",
  "https://discord.com/api/webhooks/9876543210987654321/anotherwebhook"
]
```

### 📡 RSS Feed Source (`[rss_feed]`)

This is the URL of the ModDB RSS feed you want to monitor. For S.T.A.L.K.E.R. Anomaly add-ons, the feed URL is:

```toml
[rss_feed]
url = "https://rss.moddb.com/mods/stalker-anomaly/addons/feed/rss.xml"
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
