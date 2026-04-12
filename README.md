# steam-linux-supported

Data processing to pull owned games, wishlist, Steam Deck supported, ProtonDB, and other details
to create a Shiny Python dashboard showing projected Linux game support.

## Requirements

* uv
* Python
* A Steam API key - [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)

## Setup

Copy `.env-copy` to `.env` and edit as needed.

Initialize environment

```shell
# download packages
uv sync
# activate the venv environment
source .venv/bin/activate
```

Download and prep the data by opening and running `main.ipynb`.  This can take
a long time to run so be patient.  Subsequent runs will be faster as data is cached.
As your owned game inventory and/or wishlist changes, run this script again.
This will create a `data.parquet` file that is used by the Shiny Python dashboard.

## Usage

```shell
# activate the venv environment
source .venv/bin/activate
# run shiny app
shiny run --launch-browser app.py
```

It should open but if not, open your favorite web-browser and
navigate to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Development

```shell
# activate the venv environment
source .venv/bin/activate
# run shiny app
shiny run --reload --launch-browser app.py
```

## References

* [https://github.com/bdefore/protondb-data](https://github.com/bdefore/protondb-data)
* [https://shiny.posit.co/py/](https://shiny.posit.co/py/)
* [https://www.steamdeck.com/en/verified](https://www.steamdeck.com/en/verified)
