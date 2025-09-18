import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

const rulesFilePath = path.join(__dirname, 'data', 'rules.json');

function loadRules() {
  try {
    const raw = fs.readFileSync(rulesFilePath, 'utf-8');
    return JSON.parse(raw);
  } catch (error) {
    console.error('Failed to read rules.json', error);
    return { rules: [] };
  }
}

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.post('/api/recommend', (req, res) => {
  const { soilType, crop, region } = req.body || {};

  if (!soilType || !crop) {
    return res.status(400).json({
      error: 'Missing required fields: soilType and crop',
    });
  }

  const data = loadRules();
  const normalizedSoil = String(soilType).toLowerCase();
  const normalizedCrop = String(crop).toLowerCase();

  // Find matching rule by soil and crop; region can influence text notes.
  const match = (data.rules || []).find(
    r => r.soil === normalizedSoil && r.crop === normalizedCrop
  );

  if (!match) {
    return res.json({
      soilType: normalizedSoil,
      crop: normalizedCrop,
      region: region || '',
      recommendation: {
        sowingTime: 'Consult local agri-extension for optimal window',
        irrigation: '1-2 times/week depending on rainfall',
        fertilizer: 'Balanced NPK (e.g., 10-26-26) at recommended doses',
        notes: 'No exact match found. Displaying generic guidance.',
      },
    });
  }

  const response = {
    soilType: normalizedSoil,
    crop: normalizedCrop,
    region: region || '',
    recommendation: {
      sowingTime: match.sowingTime,
      irrigation: match.irrigation,
      fertilizer: match.fertilizer,
      notes: match.notes || null,
    },
  };

  res.json(response);
});

app.listen(PORT, () => {
  console.log(`Smart Farming Advisory backend running on http://localhost:${PORT}`);
});


