# contribution-sky

my github contribution graph as a night sky. every day i committed is a star, and a satellite sweeps across and tracks them, like [satellite-detector](https://github.com/valerie-ekeigwe/satellite-detector) does with real footage.

a github action redraws it every night from live data and publishes it to the `output` branch.

<img src="https://raw.githubusercontent.com/valerie-ekeigwe/contribution-sky/output/contribution-sky.svg" width="100%" alt="contribution graph drawn as stars, with a satellite sweeping across">

run it locally with fake data:

```bash
python sky.py --demo sky.svg
```

## want one?

1. fork this repo
2. go to the Actions tab, enable workflows, and run **Contribution sky** once
3. add this to your profile README (swap in your username):

```html
<img src="https://raw.githubusercontent.com/YOUR_USERNAME/contribution-sky/output/contribution-sky.svg" width="100%">
```

it redraws itself every night.
