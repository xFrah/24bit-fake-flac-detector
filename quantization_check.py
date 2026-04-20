import soundfile as sf
import numpy as np

def check_quantization(file_24bit, file_16bit, start=10000, count=20):
    """
    Read both files as float64, extract left channel, 
    and perform a Quantization Error Analysis.
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

    print("=== MSE Level-Matched Difference (Optimal Scaling) ===")

    min_len = min(len(data_24), len(data_16))
    
    num = np.dot(data_24[:min_len], data_16[:min_len])
    den = np.dot(data_16[:min_len], data_16[:min_len])
    
    scale = num / den if den != 0 else 1.0
    db_diff = 20 * np.log10(abs(scale)) if scale != 0 else 0.0

    print(f"Optimal MSE scale factor (16-bit to match 24-bit): {scale:.8f}")
    print(f"Loudness difference (MSE derived): {db_diff:+.2f} dB\n")

    if scale >= 1.0:
        data_16_comp = data_16 * scale
        data_24_comp = data_24
        print("--- Table: 16-bit scaled UP to match 24-bit ---")
        scale_16_factor = scale
        scale_24_factor = 1.0
    else:
        data_16_comp = data_16
        data_24_comp = data_24 / scale if scale != 0 else data_24
        print("--- Table: 24-bit scaled UP to match 16-bit ---")
        scale_16_factor = 1.0
        scale_24_factor = 1.0 / scale if scale != 0 else 1.0

    end = min(start + count, len(data_24), len(data_16))
    hdr1 = f"{'Sample':<8} | {'24-bit (comp)':<26} | {'16-bit (comp)':<26} | {'Difference':<14}"
    print(hdr1)
    print("-" * len(hdr1))

    for i in range(start, end):
        val_24 = data_24_comp[i]
        val_16 = data_16_comp[i]
        diff = val_24 - val_16
        print(f"{i:<8} | {val_24:<26.18f} | {val_16:<26.18f} | {diff:<+14.10f}")

    diffs = data_24_comp[:min_len] - data_16_comp[:min_len]
    max_diff = float(np.max(np.abs(diffs)))

    max_val_16 = 2.0 ** (16 - 1)
    max_val_24 = 2.0 ** (24 - 1)
    step_16 = 1.0 / max_val_16
    step_24 = 1.0 / max_val_24
    max_q_err_16 = (step_16 / 2) * scale_16_factor
    max_q_err_24 = (step_24 / 2) * scale_24_factor

    print(f"\n--- Quantization Error Analysis ---")
    print(f"Theoretical Max 16-bit Error: {max_q_err_16:.12f} (Expected if 24-bit is true master)")
    print(f"Theoretical Max 24-bit Error: {max_q_err_24:.12f} (Expected if 24-bit is upscaled fake)")
    print(f"Actual Max Absolute Diff:     {max_diff:.12f}")
    print("-" * 50)
    
    if max_diff <= max_q_err_24 * 1.1: 
        print("VERDICT: The 24-bit file is a FAKE. It was upscaled from the 16-bit file.")
    elif max_diff <= max_q_err_16 * 1.5:
        print("VERDICT: The 24-bit file is the TRUE MASTER.")
    else:
        print("VERDICT: Files are completely different masters.")
    
    print(f"\nMean absolute difference: {np.mean(np.abs(diffs)):.12f}")
    print(f"RMS difference: {np.sqrt(np.mean(diffs**2)):.12f}")

if __name__ == "__main__":
    file_24bit = r"X:\Banco Del Mutuo Soccorso - Banco Del Mutuo Soccorso (1972) [Hi-Res 24Bit]\04. Metamorfosi.flac"
    file_16bit = r"X:\Banco del Mutuo Soccorso - 1972 - Banco del Mutuo Soccorso (Sony, Web)\04 - Metamorfosi.flac"
    check_quantization(file_24bit, file_16bit)
