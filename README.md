# log-generator
Generate a custom log file for development and testing purposes.

## Usage

```bash
python log_generator.py --output app.log --lines 1000
```

Generate by size (supports B, KB, MB, GB):

```bash
python log_generator.py --output app.log --size 250MB
```

Customize the log format to imitate an existing app:

```bash
python log_generator.py \
  --output app.log \
  --lines 50000 \
  --template "{timestamp} {level} {logger} user={user} - {message}"
```

Supply custom levels, loggers, or messages from newline-delimited files:

```bash
python log_generator.py \
  --output app.log \
  --size 1GB \
  --levels levels.txt \
  --loggers loggers.txt \
  --messages messages.txt \
  --users users.txt
```

### Template fields

Available fields for `--template`:

- `timestamp` (UTC, ISO 8601 with milliseconds)
- `level`
- `logger`
- `pid`
- `thread`
- `message`
- `user`
