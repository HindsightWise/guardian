module.exports = {
    apps: [
        {
            name: "cortex",
            script: "./skills/core/cortex.mjs",
            watch: ["skills/core/public", "skills/core/cortex.mjs"],
            ignore_watch: ["node_modules", ".git", ".openclaw/workspace"],
            env: {
                NODE_ENV: "production",
                PORT: 3333
            }
        },
        {
            name: "circadian",
            script: "./skills/core/circadian.mjs",
            watch: ["skills/core/circadian.mjs"],
            ignore_watch: ["node_modules", ".openclaw/workspace"],
        },
        {
            // Sentry/Observer Refactored
            name: "sentry",
            script: "./skills/sentry/market_stream.mjs",
            watch: ["skills/sentry/market_stream.mjs"],
            ignore_watch: ["node_modules", ".openclaw/workspace"],
            env: { NODE_ENV: "production" }
        },
        {
            name: "observer",
            script: "./skills/sentry/macro_watch.mjs",
            watch: ["skills/sentry/macro_watch.mjs"],
            ignore_watch: ["node_modules", ".openclaw/workspace"],
            env: { NODE_ENV: "production" }
        },
        {
            name: "scribe",
            script: "./skills/memory/scribe.mjs",
            watch: ["skills/memory/scribe.mjs"],
            ignore_watch: ["node_modules", ".openclaw/workspace"],
        },
        {
            name: "listener",
            script: "./skills/core/listener.mjs",
            watch: ["skills/core/listener.mjs"],
            ignore_watch: ["node_modules", ".openclaw/workspace"],
        },
        {
            name: "overlord",
            script: "./skills/alpaca/overlord.mjs",
            watch: ["skills/alpaca/overlord.mjs"],
            ignore_watch: ["node_modules", ".openclaw/workspace"],
            env: {
                NODE_ENV: "production"
            }
        },
        {
            name: "telegram",
            script: "./skills/core/telegram.mjs",
            watch: ["skills/core/telegram.mjs"],
            ignore_watch: ["node_modules", ".openclaw/workspace"],
        }
    ]
};
