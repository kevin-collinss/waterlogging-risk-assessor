const express = require("express");
const cors = require("cors");
const { exec } = require("child_process");

const app = express();
app.use(express.json());
app.use(cors()); // Enable CORS

app.post("/get_data", (req, res) => {
    const { easting, northing } = req.body;
    if (!easting || !northing) {
        return res.status(400).json({ error: "Missing easting or northing" });
    }

    const command = `python src/get_data.py ${easting} ${northing}`;
    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error("Error executing Python script:", stderr);
            return res.status(500).json({ error: "Failed to execute Python script" });
        }
        try {
            const output = JSON.parse(stdout);
            res.json(output);
        } catch (parseError) {
            console.error("Error parsing Python script output:", stdout);
            res.status(500).json({ error: "Failed to parse Python output" });
        }
    });
});

const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
