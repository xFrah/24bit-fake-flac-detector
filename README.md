# 24-bit Fake Flac Detector

This toolset mathematically verifies if a 24-bit audio file is a "true" 24-bit master or just an upscaled fake created from a 16-bit source.

## Simulated Fake Check (`simulated_fake_check.py`)
This is the core, definitive check that simulates the process a bootlegger would use to create a fake 24-bit file, and checks if your file perfectly matches that simulation.

### The Process:
1. **Load Files**: Reads both the 24-bit suspect file and the 16-bit reference file.
2. **Calculate Scale**: Finds the precise, level-matched scaling factor between the two files using Mean Squared Error (MSE). This accounts for any volume boost or reduction applied when the fake was generated.
3. **Reconstruct the Fake**: It takes the 16-bit data, applies the scale factor, and forcefully quantizes it to a 24-bit grid (rounding to the nearest 24-bit value, exactly as audio software would during a 16-to-24 bit export).
4. **Compare**: Subtracts the mathematically reconstructed fake from the actual 24-bit file, sample by sample.
5. **Verdict**: If the maximum difference across the entire track is within the limits of rounding error / dither (≤ 1.5 LSBs at 24-bit), the file is **100% confirmed as a mathematically derived fake**. If there's extra detail beyond the noise floor, it fails the match, meaning the 24-bit file contains unique information.

## Quantization Check (`quantization_check.py`)
A supplementary analysis tool that checks theoretical quantization boundaries.

### The Process:
1. Determines the optimal MSE scale factor to level-match the files.
2. Calculates the absolute differences between the level-matched audio.
3. Compares the actual differences.