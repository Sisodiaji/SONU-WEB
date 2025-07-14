const express = require("express");
const multer = require("multer");
const fs = require("fs");
const login = require("fca-unofficial");
const path = require("path");

const app = express();
const port = 3000;

app.use(express.static("public"));
app.use(express.urlencoded({ extended: true }));

const upload = multer({ dest: "uploads/" });

app.post("/start", upload.single("appstate"), (req, res) => {
    const appstatePath = req.file.path;
    const threadId = req.body.threadId;
    const enforcedName = req.body.enforcedName;

    if (!threadId || !enforcedName) {
        return res.send("Missing threadId or enforcedName");
    }

    const appState = JSON.parse(fs.readFileSync(appstatePath, "utf8"));

    login({ appState }, (err, api) => {
        if (err) return res.send("Login failed: " + err);

        res.send("Monitoring started for group " + threadId + " with enforced name " + enforcedName);

        setInterval(() => {
            api.getThreadInfo(threadId, (err, info) => {
                if (err) return console.log("Error getting group info:", err.message);

                const currentName = info.name;
                if (currentName !== enforcedName) {
                    console.log(`Group name changed! Reverting to: ${enforcedName}`);
                    api.setTitle(enforcedName, threadId, (err) => {
                        if (err) return console.log("Failed to reset group name:", err.message);
                        console.log(`Name restored to "${enforcedName}"`);
                    });
                } else {
                    console.log("Name is correct.");
                }
            });
        }, 10000);
    });
});

app.listen(port, () => {
    console.log("Server running on http://localhost:" + port);
});