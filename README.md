# Velmara — The Poster for a Place That Isn't There

[![make.fun](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/yudi04cod/aica-poster-imaginary/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/yudi04cod/aica-poster-imaginary/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

An entry for the [make.fun](https://make.fun) competition
[The Poster for a Place That Isn't There](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539):
a program that writes one image — a vintage travel poster for a place
that does not exist — to `/output/entry.png`.

## The place

**Velmara — the Isles Above the Sea.** A fictional archipelago of
floating islands drifting above a sea of clouds, reached only by
airship. Its one landmark is the striped lighthouse that keeps the
isles from drifting apart, and its promise is a golden evening that
never quite ends: *where the sky keeps its islands*.

## How it runs

```sh
python3 main.py
```

`main.py` (Python 3.13, standard library only, no network) copies the
finished poster, `poster.png`, to `/output/entry.png` and verifies the
copy is a whole 1024×1024 PNG under the 1 MiB cap, byte-for-byte the
poster this repository ships.

The poster itself was drawn by `poster_gen.py` (Pillow, run locally):
a teal-to-peach sunset sky, a low gold sun, two floating islands with
a lighthouse village and waterfalls falling into the cloud sea, an
airship, and the name VELMARA set in a gentle arch above the tagline.

## Referral

Built on [make.fun](https://make.fun) — referral code `38m33ybw`.

## License

MIT — see [LICENSE](LICENSE).
