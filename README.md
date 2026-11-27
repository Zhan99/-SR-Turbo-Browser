# SR Turbo Browser

SR Turbo Browser is an Android browser with an integrated download manager and video-download engine.

## Current source snapshot

- App version in the supplied Android project: **3.6** (versionCode 32)
- Android minimum SDK: **29 (Android 10)**
- Compile SDK: **35**
- Java: **17**
- Build system: **Gradle Groovy DSL**
- Source archive: `SR-Turbo-Browser-VideoTurboSpeed-Source (1).zip`

## Existing capabilities in the supplied source

- Multi-connection HTTP(S) downloads, with queueing, pause/resume, retry and recovery
- Download progress, speed and ETA reporting
- yt-dlp / FFmpeg-based video download support
- Browser tabs, session restore, history, bookmarks and private browsing
- Homepage shortcuts, themes and appearance options
- Desktop mode, upload picker and site compatibility helpers

Availability of video formats and resolutions depends on the source website. DRM-protected streams are not supported. Actual speed depends on the server, network, device and connection limits; a configured worker count is not a guaranteed speed increase.

## Pro upgrade work

The `pro-upgrade` branch is the isolated development branch. The `main` branch is kept unchanged while changes are reviewed and tested.

Planned work is split into verifiable stages:

1. **Build and source integrity** — repeatable CI build, dependency and asset checks, APK verification.
2. **Download engine** — audit concurrency, retry, pause/resume, recovery, queue and large-file behavior.
3. **Video engine** — validate format selection, progress, audio extraction, playlists and site compatibility within yt-dlp's supported capabilities.
4. **Browser experience** — improve navigation, tab management, download dashboard, settings and accessibility.
5. **Stability and release** — Android-version checks, regression tests, release signing strategy and documented limitations.

Features will only be marked complete after the corresponding code and tests exist. CI passing is not a substitute for testing on physical Android devices or measuring real-world download speeds.

## Build with GitHub Actions

1. Open the repository's **Actions** tab.
2. Select **Build SR Turbo Browser APK**.
3. Choose **Run workflow** and select the branch you want to test.
4. When the workflow succeeds, open its run and download the `SR-Turbo-Browser-APK` artifact.

The workflow also runs on pushes to `main`, `master`, and `pro-upgrade`, and on pull requests targeting `main` or `master`.

The current workflow builds a **debug APK**. It does not produce a Play Store-ready signed release APK.

## Test suite

From the Android project root:

```bash
bash tests/run.sh
```

The repository's test suite exercises download-engine behavior and selected browser/video integration logic. Passing these tests does not establish device compatibility or a real-world throughput benchmark.

## License and third-party notices

See `COPYING-GPL-3.0` and `THIRD_PARTY_NOTICES` in the supplied source archive. Review all bundled dependencies and their licenses before distributing modified builds.


## CI note
The Android SDK environment is exported as separate `ANDROID_HOME` and `ANDROID_SDK_ROOT` lines for the GitHub Actions runner.
