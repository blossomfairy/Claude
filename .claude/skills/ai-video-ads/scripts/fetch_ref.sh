#!/bin/bash
# fetch_ref.sh URL OUTDIR -> OUTDIR/ref.mp4 (yt-dlp; Vimeo falls back to player HLS)
set -e; URL=$1; OUT=$2; mkdir -p "$OUT"
command -v yt-dlp >/dev/null || pip install -q yt-dlp
yt-dlp -q -f 'best[height<=1080]/best' -o "$OUT/ref.%(ext)s" "$URL" 2>/dev/null && exit 0
id=$(echo "$URL" | grep -oE 'vimeo.com/[0-9]+' | grep -oE '[0-9]+') || { echo "download failed"; exit 1; }
curl -sSL -A 'Mozilla/5.0' -H 'Referer: https://vimeo.com/' "https://player.vimeo.com/video/$id" -o "$OUT/player.html"
hls=$(python3 -c "
import re,json,sys;h=open('$OUT/player.html').read();c=json.loads(re.search(r'window\.playerConfig\s*=\s*(\{.*?\})\s*(?:;|</script>)',h,re.S).group(1))
x=c['request']['files']['hls'];print(x['cdns'][x['default_cdn']]['url'])")
ffmpeg -loglevel error -y -i "$hls" -c copy "$OUT/ref.mp4"
