sed '/^[^#]/s/^\(.*\)=\(.*\)$/export \1="\2"/' .env > cron.env
