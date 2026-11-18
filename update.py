#!/usr/bin/env python3
"""Regenerate apps.json from the three upstream GitHub releases.

Upstreams (all public, no token needed):
  - Regram (Telegram)  RegramDev/Regram-ios      bundle app.swiftgram.ios
  - iPadn (lite)        mengangs/ipadn             bundle app.local.iPadn
  - Erosion-CN          Kianuni/Erosion-CN         bundle com.jbdotparty.Erosion

Run by hand or by .github/workflows/update.yml (daily + manual).
Icon URLs are built from GITHUB_REPOSITORY (owner/repo) so the same
script works in any fork: set SOURCE_REPO env to override.
"""
import json
import os
import re
import urllib.request

SOURCE_REPO = os.environ.get("SOURCE_REPO") or os.environ.get("GITHUB_REPOSITORY") or "OWNER/REPO"
ICON_BASE = f"https://raw.githubusercontent.com/{SOURCE_REPO}/main/icons"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps.json")
UA = {"User-Agent": "regram-altstore-source/1.0"}


def gh(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def text(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode().strip()


def changelog(body, limit=1500):
    body = (body or "").strip()
    # Keep only the "更新内容" section; drop the long build-verification part.
    m = re.split(r"##\s*构建", body, maxsplit=1)
    body = m[0].strip()
    body = re.sub(r"^##\s+", "", body, flags=re.M)
    return body[:limit]


def latest(repo):
    return gh(f"/repos/{repo}/releases/latest")


def asset(release, suffix):
    for a in release.get("assets", []):
        if a["name"].endswith(suffix):
            return a
    return None


def sha_of(release, ipa_name):
    a = asset(release, ".sha256")
    if not a:
        return ""
    try:
        return text(a["browser_download_url"]).split()[0]
    except Exception:
        return ""


def entry(app, release, ipa, version, icon, subtitle, desc_extra=""):
    sha = sha_of(release, ipa["name"])
    desc = changelog(release.get("body", ""))
    if sha:
        desc = (desc + f"\n\nSHA-256: {sha}").strip()
    if desc_extra:
        desc = (desc + f"\n\n{desc_extra}").strip()
    ver = {
        "version": version,
        "date": release.get("published_at", ""),
        "localizedDescription": desc,
        "downloadURL": ipa["browser_download_url"],
        "size": ipa["size"],
    }
    return {
        "name": app["name"],
        "bundleIdentifier": app["bundle"],
        "developerName": app["dev"],
        "subtitle": subtitle,
        "localizedDescription": desc,
        "iconURL": icon,
        "version": version,
        "versionDate": release.get("published_at", ""),
        "downloadURL": ipa["browser_download_url"],
        "size": ipa["size"],
        "versions": [ver],
    }


def build():
    apps = []

    # --- Regram (Telegram, NOT the Instagram tweak of the same name) ---
    rel = latest("RegramDev/Regram-ios")
    tag = rel["tag_name"].lstrip("v")          # 13.2-b34663
    m = re.match(r"(.+)-b(\d+)$", tag)
    version = f"{m.group(1)}.{m.group(2)}" if m else tag   # 13.2.34663: build bumps must change `version`
    ipa = asset(rel, ".ipa")
    apps.append(entry(
        {"name": "Regram", "bundle": "app.swiftgram.ios", "dev": "RegramDev"},
        rel, ipa, version, f"{ICON_BASE}/regram.jpg",
        "Telegram 第三方客户端（非 Instagram 版 Regram）",
        "原版 13.2 (b34663)。在 LiveContainer 里用：下载后导入 LiveContainer 覆盖，别用内置更新走证书安装。",
    ))

    # --- iPadn, lite build (1 App ID, the one the user uses) ---
    rel = latest("mengangs/ipadn")
    tag = rel["tag_name"].lstrip("v")          # 2.2.1
    ipa = asset(rel, "-lite-unsigned.ipa")
    apps.append(entry(
        {"name": "iPadn", "bundle": "app.local.iPadn", "dev": "mengangs"},
        rel, ipa, tag, f"{ICON_BASE}/ipadn.png",
        "下载安装自己拥有的 App 历史版本（精简版）",
        "精简版 lite，只占 1 个 App ID。未签名，需用自己的工具签名后安装。",
    ))

    # --- Erosion-CN (mirrors its official source, so LBox has all three in one place) ---
    rel = latest("Kianuni/Erosion-CN")
    tag = rel["tag_name"].lstrip("v")          # 1.0.5
    ipa = asset(rel, ".ipa")
    apps.append(entry(
        {"name": "Erosion", "bundle": "com.jbdotparty.Erosion", "dev": "Kianuni"},
        rel, ipa, tag, f"{ICON_BASE}/erosion.png",
        "iOS MobileGestalt 系统配置工具箱（中英双语）",
        "官方源 https://raw.githubusercontent.com/Kianuni/Erosion-CN/main/apps.json 也有同一版，这里只做汇总。",
    ))

    # Preserve up to 2 older versions per app from the existing apps.json.
    try:
        old = json.load(open(OUT))
        old_by_bundle = {a["bundleIdentifier"]: a for a in old.get("apps", [])}
    except Exception:
        old_by_bundle = {}
    for app in apps:
        old = old_by_bundle.get(app["bundleIdentifier"])
        if old:
            seen = {v["version"] for v in app["versions"]}
            for v in old.get("versions", []):
                if v.get("version") not in seen and len(app["versions"]) < 3:
                    app["versions"].append(v)
                    seen.add(v["version"])

    source = {
        "name": "白日梦的源",
        "identifier": "ccwu.pigpig.regram-ipadn-erosion",
        "subtitle": "Regram / iPadn / Erosion 更新汇总",
        "description": "Regram（Telegram 版，非 Instagram 版）、iPadn（精简版）、Erosion-CN 三个 App 的更新汇总源，自动跟各自 GitHub 最新正式版。只做汇总，不改包。",
        "iconURL": f"{ICON_BASE}/regram.jpg",
        "website": "https://github.com/RegramDev/Regram-ios",
        "apps": apps,
        "news": [],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(source, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for a in apps:
        print(a["name"], a["version"], a["versionDate"], a["size"], a["downloadURL"])


if __name__ == "__main__":
    build()
