module.exports = {
apps : [
  {
    name   : "web",
    script : "python app.py --mode=web",
    autorestart: true,
    instances:1
  },
  {
    name   : "gmail_notify",
    script : "python app.py --mode=gmail_notify",
    autorestart: true,
    instances:1
  },
  {
    name   : "tg_notify",
    script : "python app.py --mode=tg_notify",
    autorestart: true,
    instances:1
  },
  {
    name   : "termptt",
    script : "python app.py --mode=termptt",
    autorestart: true,
    instances:1,
    cron_restart:'15 * * * *'
  },
  {
    name   : "webptt",
    script : "python app.py --mode=webptt",
    autorestart: true,
    instances:1,
    cron_restart:'15 * * * *'
  },
  {
    name   : "pttmail_notify",
    script : "python app.py --mode=pttmail_notify",
    autorestart: true,
    instances:1,
    cron_restart:'30 * * * *'
  }
]
}