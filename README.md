# About
This provides a m3u that has all of your available FuboTV channels that you can import into something like [Jellyfin](https://jellyfin.org), [Channels](https://getchannels.com), or [xTeVe](https://github.com/xteve-project/xTeVe). It requires a subscription from FuboTV to work.

# Using
The server exposes 1 endpoint:

| Endpoint | Description |
|---|---|
| /fubo/playlist.m3u | The channel list you'll import into your client |

Import: `http://YOUR_IP:7777/fubo/playlist.m3u` into your client.

# Running
The recommended way of running is to pull the image from [Docker Hub](https://hub.docker.com/r/jgomez177/vlc-bridge-fubo).

## Environement Variables
| Environment Variable | Description | Required? |
|---|---|---|
| FUBO_USER | FuboTV Username or Email address | Yes |
| FUBO_PASS | FuboTV Password | Yes |

## Docker Run
By default, the easiest way to get running is:

```bash
docker run -d -p 7777:7777 -e FUBO_USER="user@email.com" -e FUBO_PASS="secret" --name vlc-bridge-fubo jgomez177/vlc-bridge-fubo
```
