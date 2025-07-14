const express = require("express");
const multer = require("multer");
const fs = require("fs");
const login = require("fca-unofficial");
const path = require("path");

const app = express();
const port = process.env.PORT || 3000;

app.use(express.static("public"));
app.use(express.urlencoded({ extended: true }));

const upload = multer({ dest: "uploads/" });

app.post("/start", upload.single("appstate"), (req, res) => {
  const threadId = req.body.threadId;
  const enforcedName = req.body.enforcedName;
  const appStateFile = req.file.path;

  try {
    const appState = JSON.parse(fs.readFileSync(appStateFile, "utf8"));

    login({ appState }, (err, api) => {
      if (err) {
        console.error("Login error:", err);
        return res.send("Login failed: " + (err.error || err));
      }

      api.setGroupInfo(threadId, { name: enforcedName }, (err) => {
        if (err) {
          console.error("Failed to change name:", err);
          return res.send("Failed to lock group name.");
        }
        return res.send("Group name locked to: " + enforcedName);
      });
    });
  } catch (e) {
    console.error("Error parsing appstate:", e);
    return res.send("Invalid appstate file.");
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
