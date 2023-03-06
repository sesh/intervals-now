This script generates an [omg.lol](https://omg.lol) [/now](https://nownownow.com/about) block containing running stats from [Intervals.icu](https://intervals.icu).
It's possible that the Venn diagram of users this is useful for only contains me.

Currently only metric units are supported.


## Usage

There are four environment variables that need to be configured to run the sync:

- `INTERVALS_ATHLETE_ID` + `INTERVALS_API_KEY` are available in the "Developer Settings" section of the Intervals settings
- `OMGLOL_USERNAME`, `OMGLOL_API_KEY` are available in the Account section of the omg.lol dashboard

Optionally you can include `<!-- block intervals-now -->` and `<!-- end intervals-now -->` in your /now page's Markdown to specify when you want your Intervals stats to go.
If this doesn't exist the block will be added at the end of your page.

Once the environment variables are available, running the script is as simple as:

```
> python generate.py
```

Python versions >= 3.6 should be supported.


### Usage as a Github Action

Simply fork this repository and add the environment variables to update you page with Github Actions.
The simplest configuration involves settings up the four environment variables as Repository Secrets in the Github settings for your fork of this repository.


## Contributing

You are welcome to submit Pull Requests or raise issues.
All CI steps will need to be passing before PRs are merged.
You can run them locally with:

```
> isort . && black . && ruff . && bandit -r .
```
