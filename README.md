# Inventorist

[![Build Status](https://travis-ci.org/rozumalex/inventorist.svg?branch=master)](https://travis-ci.org/github/triplinker/triplinker)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/triplinker/triplinker/blob/master/LICENSE)

---

Inventorist is a telegram stocktaking bot for your business needs.

## Installation Guide


If you want to get a copy of this bot for your personal usage,
please follow the instructions below.


### Clone the project to your local machine

```
git clone https://github.com/rozumalex/inventorist
```

### Install poetry

```
pip install poetry
```

### Install dependencies

***Note:*** you need to get to the directory with the project,
then you can run the command: 

```
poetry install
```

### Create config.yaml file in the main folder

***Note:*** insert your token and preferred name for database.
You can find token it in BotFather.

```
bot:
  token: 'YOUR_BOT_TOKEN'

database:
  name: YOUR_DB_NAME.db
```

### Run bot

```
poetry shell
cd bot
python bot.py
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/rozumalex/inventorist/blob/master/LICENSE) file for details.

