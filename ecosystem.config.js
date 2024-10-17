module.exports = {
  apps : [{
    name   : "web",
    script : "python app.py --mode=web",
    autorestart: true,
    instances:1
  },
  {
    name   : "tg_gmail_notify",
    script : "python app.py --mode=polling",
    autorestart: true,
    instances:1
  },
  {
    name   : "term_ptt",
    script : "python app.py --mode=ptt",
    autorestart: true,
    instances:1
  }]
}
