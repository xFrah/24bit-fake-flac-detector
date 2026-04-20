import soundfile as sf
import numpy as np

def simulate_and_check_fake(file_24bit, file_16bit, start=10000, count=20):
    """
    Read both files as float64, calculate scale, mathematically reconstruct 
    a fake 24-bit file from the 16-bit file, and check if it perfectly matches.
    """

    data_24, sr_24 = sf.read(file_24bit, dtype='float64')
    data_16, sr_16 = sf.read(file_16bit, dtype='float64')

    if data_24.ndim > 1:
        data_24 = data_24[:, 0]
    if data_16.ndim > 1:
        data_16 = data_16[:, 0]

    info_24 = sf.info(file_24bit)
    info_16 = sf.info(file_16bit)

    print(f"File 1 (24-bit): {info_24.subtype}, {sr_24} Hz, {len(data_24)} samples")
    print(f"File 2 (16-bit): {info_16.subtype}, {sr_16} Hz, {len(data_16)} samples\n")

    if sr_16 != sr_24:
        print("ERROR: Sample rates must match exactly for Bit-Depth quantization checks!")
        return

    min_len = min(len(data_24), len(data_16))
    
    # Calculate MSE scale
    num = np.dot(data_24[:min_len], data_16[:min_len])
    den = np.dot(data_16[:min_len], data_16[:min_len])
    scale = num / den if den != 0 else 1.0
    db_diff = 20 * np.log10(abs(scale)) if scale != 0 else 0.0

    print("--- Simulated Fake Validation ---")
    print(f"Optimal MSE scale factor: {scale:.12f}")
    print(f"Loudness difference (MSE derived): {db_diff:+.4f} dB\n")
    print("Reconstructing fake 24-bit file: quantizing (16-bit * scale) to 24-bit grid...")
    
    # Mathematical reconstruction of how the fake was produced
    max_val_24 = 2.0 ** (24 - 1)
    simulated_fake = np.round(data_16[:min_len] * scale * max_val_24) / max_val_24
    
    sim_diffs = data_24[:min_len] - simulated_fake
    sim_max_diff = float(np.max(np.abs(sim_diffs)))
    
    end = min(start + count, min_len)
    hdr2 = f"{'Sample':<8} | {'24-bit (actual)':<26} | {'Simulated Fake':<26} | {'Difference':<14}"
    print(hdr2)
    print("-" * len(hdr2))
    
    for i in range(start, end):
        val_24 = data_24[i]
        val_fake = simulated_fake[i]
        diff = val_24 - val_fake
        print(f"{i:<8} | {val_24:<26.18f} | {val_fake:<26.18f} | {diff:<+14.10f}")

    lsb_dither_rounding = (1.0 / max_val_24) * 1.5
    
    non_zero_count = np.count_nonzero(sim_diffs)
    total_samples = len(sim_diffs)
    non_zero_pct = (non_zero_count / total_samples) * 100.0
    zero_pct = 100.0 - non_zero_pct
    
    print(f"\nStats across all {total_samples} samples:")
    print(f"Max absolute difference: {sim_max_diff:.12f}")
    print(f"Exactly matched (0 diff): {total_samples - non_zero_count} samples ({zero_pct:.4f}%)")
    print(f"Imperfect matches:        {non_zero_count} samples ({non_zero_pct:.4f}%)")

    if sim_max_diff == 0.0:
        print("-> FAKE CONFIRMED: 100% PERFECT MATHEMATICAL MATCH. Difference is exactly 0.")
    elif sim_max_diff <= lsb_dither_rounding:
        print(f"-> FAKE CONFIRMED: PERFECT MATCH (within 1 LSB dither/rounding={lsb_dither_rounding}). Difference maxes at 24-bit limit.")
    else:
        print("-> NOT A PERFECT MATCH. The 24-bit file contains information not explained by simple scaling & 24-bit export.")

if __name__ == "__main__":
    file_24bit = r"X:\Banco Del Mutuo Soccorso - Banco Del Mutuo Soccorso (1972) [Hi-Res 24Bit]\04. Metamorfosi.flac"
    file_16bit = r"X:\Banco del Mutuo Soccorso - 1972 - Banco del Mutuo Soccorso (Sony, Web)\04 - Metamorfosi.flac"
    simulate_and_check_fake(file_24bit, file_16bit)
