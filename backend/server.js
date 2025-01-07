const express = require("express");
const { exec } = require("child_process");

const app = express();
const PORT = 5000;

app.use(express.json());

app.post("/get_data", (req, res) => {
    const { easting, northing } = req.body;

    // Execute the Python script with the easting and northing as arguments
    const command = `python ./src/get_data.py ${easting} ${northing}`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing script: ${error.message}`);
            res.status(500).json({ error: "Failed to execute Python script" });
            return;
        }

        if (stderr) {
            console.error(`Script error: ${stderr}`);
            res.status(500).json({ error: stderr });
            return;
        }

        // Send the Python script's output as the response
        try {
            const result = JSON.parse(stdout); // Parse JSON from the Python output
            res.json(result);
        } catch (parseError) {
            console.error(`Failed to parse Python output: ${parseError.message}`);
            res.status(500).json({ error: "Failed to parse Python output" });
        }
    });
});

app.listen(PORT, () => {
    console.log(`Node.js server running on http://localhost:${PORT}`);
});
