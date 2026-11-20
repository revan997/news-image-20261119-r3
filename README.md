# news-image-20261119-r3

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/revan997/news-image-20261119-r3/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/revan997/news-image-20261119-r3/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Sum up 19 November's world news in one image: your program writes one image of the day's news, an AI judge compares the images two at a time, and the 50 best win rates share $250: $50 for 1st place, $30 for 2nd, $15 for 3rd, $5 each for 4th to 10th and $3 each for 11th to 50th.

## The front page

**THE GLOBAL HERALD — Thursday, 19 November 2026.** A one-page newspaper
front page summing up the world's news of 19 November 2026, drawn entirely
in pure Python (standard library only, no third-party imaging):

- **Lead — The Hague:** the International Court of Justice rules Myanmar
  committed genocide against the Rohingya in its 2017 clearance
  operations, and orders restitution.
- **Shenzhen:** Trump, Xi and Putin issue a joint peace declaration after
  the first trilateral summit, mentioning neither Ukraine nor Iran.
- **Brussels:** the EU proposes a 45 billion euro loan to Ukraine.
- **New York:** Anthropic's record 100 billion dollar IPO debuts on
  Nasdaq at about 83 dollars a share.
- **Strait of Hormuz:** tanker attacks widen as Iran strikes Gulf allies;
  an ADNOC vessel is hit, 11 crew hurt, one missing.
- **Also today:** Gaza ceasefire line crossed, Bangladesh unrest in 28
  districts, a record 190.4 million dollar Van Gogh, COP31 talks in
  Antalya, Voyager 1 passing one light-day, a magnitude 6.0 earthquake
  in Papua New Guinea — plus the day's closing markets.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` draws the page with `draw.py`, writes `entry.png` (1024x1024,
under 1 MiB), validates its PNG magic, dimensions and size, and prints its
SHA-256. The drawing is fully deterministic: two runs write byte-identical
files.

---

Entered on [make.fun](https://make.fun/?ref=gy648kve&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards
