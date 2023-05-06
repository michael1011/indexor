# indexor

Index the Bitcoin chain into a PostgreSQL database

## Usage

### Setup

```sh
poetry install
```

#### Config file

Sample config

```toml
[db]
host = "127.0.0.1"
port = 5432
user = "indexor"
password = "indexor"
database = "indexor"

[bitcoin]
host = "127.0.0.1"
port = 8332
cookie = "/media/michael/HDD/Bitcoin/.cookie"
```

```shell
poetry run indexor
```
